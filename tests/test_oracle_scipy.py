"""Oráculo independiente y comparación generativa de los futuros métodos propios."""

from dataclasses import replace
from fractions import Fraction

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from scipy.optimize import linprog

from plapp.big_m import solve_big_m
from plapp.io_json import problem_to_dict
from plapp.model import Constraint, LPProblem, validate
from plapp.revised_simplex import solve_revised
from plapp.sensitivity import sensitivity_analysis
from scripts.verify import compare_solution, scipy_inputs, verify_with_scipy


def test_fixtures_match_scipy(fixture_problem):
    problem, expected = fixture_problem
    oracle = verify_with_scipy(problem)
    assert oracle.status == expected["estado"]
    if oracle.status != "optimo":
        return
    assert oracle.objective_value == pytest.approx(float(Fraction(expected["z"])))
    if not expected["multiples"]:
        assert oracle.values == pytest.approx(
            {name: float(Fraction(value)) for name, value in expected["x"].items()}
        )
    else:
        assert oracle.values["x1"] + 2 * oracle.values["x2"] == pytest.approx(5)
    for field, values in (("holguras", oracle.slacks), ("precios_sombra", oracle.shadow_prices)):
        if field in expected:
            assert values == pytest.approx(
                {key: float(Fraction(value)) for key, value in expected[field].items()}
            )
    # El punto esperado también debe ser factible, independientemente de HiGHS.
    for row in problem.constraints:
        activity = sum(
            a * Fraction(expected["x"][name])
            for a, name in zip(row.coefficients, problem.variable_names, strict=True)
        )
        assert (
            activity <= row.rhs
            if row.relation == "<="
            else (activity >= row.rhs if row.relation == ">=" else activity == row.rhs)
        )


@pytest.mark.parametrize(
    ("sense", "relation", "coefficient", "rhs", "price"),
    [
        ("max", "<=", 1, 4, 2),
        ("min", ">=", 1, 4, 2),
        ("max", "<=", -1, -4, 2),
        ("min", ">=", -1, -4, 2),
        ("max", "=", 1, 4, 2),
        ("min", "=", 1, 4, 2),
    ],
)
def test_shadow_price_signs(sense, relation, coefficient, rhs, price):
    objective = 2 if coefficient > 0 else -2
    problem = LPProblem(
        (Fraction(objective),),
        (Constraint((Fraction(coefficient),), relation, Fraction(rhs)),),
        sense=sense,
    )
    oracle = verify_with_scipy(problem)
    assert oracle.shadow_prices["R1"] == pytest.approx(price)
    shifted = replace(
        problem,
        constraints=(replace(problem.constraints[0], rhs=Fraction(rhs) + Fraction(1, 100)),),
    )
    difference = (verify_with_scipy(shifted).objective_value - oracle.objective_value) / 0.01
    assert difference == pytest.approx(price)


@st.composite
def small_problems(draw):
    """PL con dimensiones y signos variados; impedir filas totalmente nulas."""
    n = draw(st.integers(2, 4))
    m = draw(st.integers(1, 4))
    coefficients = st.lists(st.integers(-9, 9), min_size=n, max_size=n)
    objective = tuple(map(Fraction, draw(coefficients)))
    constraints = []
    for _ in range(m):
        row = draw(coefficients.filter(lambda values: any(values)))
        constraints.append(
            Constraint(
                tuple(map(Fraction, row)),
                draw(st.sampled_from(["<=", ">=", "="])),
                Fraction(draw(st.integers(-9, 9))),
            )
        )
    return LPProblem(objective, tuple(constraints), sense=draw(st.sampled_from(["max", "min"])))


def unique_nondegenerate(problem, oracle):
    """Guardia conservadora: n restricciones activas independientes y cara óptima puntual."""
    if oracle.status != "optimo":
        return False
    x = np.array([oracle.values[name] for name in problem.variable_names])
    n = len(x)
    active = [
        list(map(float, row.coefficients))
        for row in problem.constraints
        if abs(
            sum(float(a) * value for a, value in zip(row.coefficients, x, strict=True))
            - float(row.rhs)
        )
        < 1e-7
    ]
    active.extend(np.eye(n)[index].tolist() for index, value in enumerate(x) if abs(value) < 1e-7)
    if len(active) != n or np.linalg.matrix_rank(active) != n:
        return False
    inputs = scipy_inputs(problem)
    inputs["A_eq"] = (inputs["A_eq"] or []) + [list(map(float, problem.objective))]
    inputs["b_eq"] = (inputs["b_eq"] or []) + [oracle.objective_value]
    for index in range(n):
        for direction in (-1, 1):
            inputs["c"] = [direction if position == index else 0 for position in range(n)]
            result = linprog(**inputs, method="highs")
            if result.status != 0 or abs(result.x[index] - x[index]) > 1e-7:
                return False
    return True


@settings(max_examples=30, deadline=None)
@given(small_problems())
def test_generated_models_are_valid(problem):
    validated, issues = validate(problem_to_dict(problem))
    assert not issues and validated == problem
    assert verify_with_scipy(problem).status in ("optimo", "infactible", "no_acotado")


@pytest.mark.parametrize(
    "solver",
    [
        solve_big_m,
        pytest.param(
            solve_revised,
            marks=pytest.mark.xfail(
                raises=NotImplementedError, strict=False, reason="Simplex revisado pendiente"
            ),
        ),
    ],
)
@settings(max_examples=40, deadline=None)
@given(problem=small_problems())
def test_own_solver_against_scipy(solver, problem):
    oracle = verify_with_scipy(problem)
    own = solver(problem)
    assert not compare_solution(problem, own, oracle)


@pytest.mark.parametrize("solver", [solve_big_m, solve_revised])
@pytest.mark.xfail(
    raises=NotImplementedError, strict=False, reason="Sensibilidad pendiente del equipo"
)
@settings(max_examples=30, deadline=None)
@given(problem=small_problems())
def test_shadow_prices_against_scipy(solver, problem):
    oracle = verify_with_scipy(problem)
    own = solver(problem)
    if unique_nondegenerate(problem, oracle):
        report = sensitivity_analysis(problem, own)
        assert {key: float(value) for key, value in report.shadow_prices.items()} == pytest.approx(
            oracle.shadow_prices, abs=1e-7
        )
