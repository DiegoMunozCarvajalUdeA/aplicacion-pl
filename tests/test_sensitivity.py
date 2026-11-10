"""Sensibilidad contra SciPy sobre una base óptima conocida y no degenerada."""

from dataclasses import replace
from fractions import Fraction

import pytest
from hypothesis import given, settings

from plapp.big_m import solve_big_m
from plapp.io_json import load_problem
from plapp.mvalue import MValue
from plapp.result import Solution, StandardForm, Status
from plapp.sensitivity import sensitivity_analysis
from scripts.verify import verify_with_scipy
from tests.conftest import PROBLEMS
from tests.test_big_m import problem
from tests.test_oracle_scipy import small_problems


def test_example_one_sensitivity(example_one):
    f = Fraction
    standard = StandardForm(
        ("x1", "x2", "s1", "s2", "s3"),
        ("original", "original", "holgura", "holgura", "holgura"),
        tuple(tuple(map(f, row)) for row in ((2, 1, 1, 0, 0), (1, 3, 0, 1, 0), (0, 1, 0, 0, 1))),
        (f(100), f(90), f(40)),
        tuple(MValue(f(value)) for value in (50, 80, 0, 0, 0)),
        (2, 3, 4),
        (),
    )
    solution = Solution(
        method="big_m",
        status=Status.OPTIMAL,
        message="Solución óptima",
        values={"x1": f(42), "x2": f(16)},
        objective_value=f(3380),
        slacks={"R1": f(0), "R2": f(0), "R3": f(24)},
        standard_form=standard,
        final_basis=(0, 1, 4),
        final_b_inverse=(
            (f(3, 5), f(-1, 5), f(0)),
            (f(-1, 5), f(2, 5), f(0)),
            (f(1, 5), f(-2, 5), f(1)),
        ),
    )
    report = sensitivity_analysis(example_one, solution)
    oracle = verify_with_scipy(example_one)
    assert {key: float(value) for key, value in report.shadow_prices.items()} == pytest.approx(
        oracle.shadow_prices
    )
    assert report.shadow_prices == {"R1": f(14), "R2": f(22), "R3": f(0)}
    assert report.reduced_costs == {"x1": f(0), "x2": f(0)}
    assert report.objective_ranges == {"x1": (f(80, 3), f(160)), "x2": (f(25), f(150))}
    assert report.rhs_ranges == {"R1": (f(30), f(180)), "R2": (f(50), f(150)), "R3": (f(16), None)}
    assert report.interpretations and all(report.interpretations.values())


def test_example_two_exact_derivation():
    original = load_problem(PROBLEMS / "ejemplo_2.json")
    solution = solve_big_m(original)
    # Columnas básicas (x1, x2, e2): B = [(3,1,0),(4,3,-1),(1,2,0)].
    # x1=(2b1-b3)/5, x2=(-b1+3b3)/5, e2=b1-b2+b3.
    # B⁻¹=[(2/5,0,-1/5),(-1/5,0,3/5),(1,-1,1)].
    # (4,1,0)B⁻¹=(7/5,0,-1/5); R3 original se negó: precio +1/5.
    # Única no básica no artificial: s3, r=1/5. Para c1+Δ exige
    # (1+Δ)/5≥0; para c2+Δ, (1-3Δ)/5≥0.
    # RHS: exigir x_B≥0 da Δb1∈[-1,9], Δb2≤1,
    # Δb3 normalizado∈[-1,2]; original Δb3∈[-2,1].
    report = sensitivity_analysis(original, replace(solution, final_b_inverse=None, iterations=()))
    f = Fraction
    assert report.shadow_prices == {"R1": f(7, 5), "R2": 0, "R3": f(1, 5)}
    assert report.reduced_costs == {"x1": 0, "x2": 0}
    assert report.objective_ranges == {"x1": (f(3), None), "x2": (None, f(4, 3))}
    assert report.rhs_ranges == {"R1": (f(2), f(12)), "R2": (None, f(7)), "R3": (f(-6), f(-3))}
    assert not report.warnings
    oracle = verify_with_scipy(original)
    assert {k: float(v) for k, v in report.shadow_prices.items()} == pytest.approx(
        oracle.shadow_prices
    )


@pytest.mark.parametrize("example", [1, 2])
def test_ranges_by_scipy_perturbation(example):
    original = load_problem(PROBLEMS / f"ejemplo_{example}.json")
    solution = solve_big_m(original)
    report = sensitivity_analysis(original, solution)
    for kind, ranges in (("b", report.rhs_ranges), ("c", report.objective_ranges)):
        names = [r.name for r in original.constraints] if kind == "b" else original.variable_names
        for name, (lower, upper) in ranges.items():
            index = names.index(name)
            current = original.constraints[index].rhs if kind == "b" else original.objective[index]
            slope = report.shadow_prices[name] if kind == "b" else solution.values[name]
            inside = [
                (current + bound) / 2 if bound is not None else current + direction
                for direction, bound in ((-1, lower), (1, upper))
            ]
            outside = [
                bound + Fraction(direction, 100)
                for direction, bound in ((-1, lower), (1, upper))
                if bound is not None
            ]
            for value in inside + outside:
                if kind == "b":
                    rows = tuple(
                        replace(row, rhs=value) if i == index else row
                        for i, row in enumerate(original.constraints)
                    )
                    shifted = replace(original, constraints=rows)
                else:
                    objective = tuple(
                        value if i == index else c for i, c in enumerate(original.objective)
                    )
                    shifted = replace(original, objective=objective)
                oracle = verify_with_scipy(shifted)
                predicted = float(solution.objective_value + slope * (value - current))
                if value in inside:
                    assert oracle.status == "optimo" and oracle.objective_value == pytest.approx(
                        predicted
                    )
                    if kind == "c":
                        assert oracle.values == pytest.approx(
                            {k: float(v) for k, v in solution.values.items()}
                        )
                else:
                    assert oracle.status != "optimo" or oracle.objective_value != pytest.approx(
                        predicted
                    )


@pytest.mark.parametrize("reverse_basis", [False, True])
def test_redundant_original_row_and_rhs_consistency(reverse_basis):
    original = problem((1, 2), [((1, 1), "=", 4), ((1, 1), "=", 4)])
    solution = solve_big_m(original)
    if reverse_basis:
        solution = replace(solution, final_basis=solution.final_basis[::-1])
    report = sensitivity_analysis(original, solution)
    assert report.shadow_prices == {"R1": 2, "R2": 0}
    assert report.rhs_ranges == {"R1": (4, 4)}
    assert any("R2: precio sombra no único: fila redundante" in w for w in report.warnings)
    assert "no se informa rango" in report.interpretations["b:R2"]
    assert "perturbación aislada" in report.interpretations["b:R1"]
    rows = (replace(original.constraints[0], rhs=Fraction(5)), original.constraints[1])
    assert verify_with_scipy(replace(original, constraints=rows)).status == "infactible"


def test_degenerate_ranges_and_warnings():
    original = load_problem(PROBLEMS / "ejemplo_7.json")
    report = sensitivity_analysis(original, solve_big_m(original))
    assert any("Degeneración" in w and "pueden no ser únicos" in w for w in report.warnings)
    assert any(row.rhs in report.rhs_ranges[row.name] for row in original.constraints)


def test_all_optimal_fixtures_have_exact_dual_certificate(fixture_problem):
    original, _ = fixture_problem
    solution = solve_big_m(original)
    if solution.status != Status.OPTIMAL:
        with pytest.raises(ValueError, match="requiere una solución óptima"):
            sensitivity_analysis(original, solution)
        return
    report = sensitivity_analysis(original, replace(solution, final_b_inverse=None, iterations=()))
    assert (
        sum(report.shadow_prices[row.name] * row.rhs for row in original.constraints)
        == solution.objective_value
    )
    sign = -1 if original.sense == "max" else 1
    assert all(sign * value >= 0 for value in report.reduced_costs.values())
    for name, (lower, upper) in report.objective_ranges.items():
        current = original.objective[original.variable_names.index(name)]
        assert (lower is None or lower <= current) and (upper is None or current <= upper)


@settings(max_examples=150, deadline=None, derandomize=True)
@given(small_problems())
def test_generated_sensitivity_by_resolving_perturbations(original):
    solution = solve_big_m(original)
    if solution.status != Status.OPTIMAL:
        return
    report = sensitivity_analysis(original, solution)
    assert (
        sum(report.shadow_prices[r.name] * r.rhs for r in original.constraints)
        == solution.objective_value
    )
    sign = -1 if original.sense == "max" else 1
    for j, name in enumerate(original.variable_names):
        reduced = original.objective[j] - sum(
            report.shadow_prices[row.name] * row.coefficients[j] for row in original.constraints
        )
        assert report.reduced_costs[name] == reduced and sign * reduced >= 0
        assert reduced * solution.values[name] == 0
    for kind, ranges in (("b", report.rhs_ranges), ("c", report.objective_ranges)):
        names = [r.name for r in original.constraints] if kind == "b" else original.variable_names
        for name, (lower, upper) in ranges.items():
            index = names.index(name)
            current = original.constraints[index].rhs if kind == "b" else original.objective[index]
            if upper is None:
                value = current + 1
            elif lower is None:
                value = current - 1
            else:
                value = (lower + upper) / 2
            if value == current:
                continue
            if kind == "b":
                shifted = replace(
                    original,
                    constraints=tuple(
                        replace(row, rhs=value) if i == index else row
                        for i, row in enumerate(original.constraints)
                    ),
                )
                slope = report.shadow_prices[name]
            else:
                shifted = replace(
                    original,
                    objective=tuple(
                        value if i == index else cost for i, cost in enumerate(original.objective)
                    ),
                )
                slope = solution.values[name]
            shifted_solution = solve_big_m(shifted)
            assert shifted_solution.status == Status.OPTIMAL
            assert shifted_solution.objective_value == solution.objective_value + slope * (
                value - current
            )
