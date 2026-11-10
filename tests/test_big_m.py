"""Trazas manuales, certificados exactos y casos delicados de la Gran M."""

from fractions import Fraction

import pytest

from plapp import big_m
from plapp.big_m import solve_big_m
from plapp.io_json import load_problem
from plapp.linalg import identity, matmul, matvec
from plapp.model import Constraint, LPProblem
from plapp.mvalue import MValue
from plapp.result import Status
from scripts.verify import compare_solution, verify_with_scipy
from tests.conftest import PROBLEMS


def problem(objective, rows, sense="max"):
    """Construir problemas pequeños con todas las entradas exactas."""
    return LPProblem(
        tuple(map(Fraction, objective)),
        tuple(
            Constraint(tuple(map(Fraction, a)), relation, Fraction(b)) for a, relation, b in rows
        ),
        sense=sense,
    )


def test_example_one_manual_trace(example_one):
    solution = solve_big_m(example_one)
    assert len(solution.iterations) == 3
    assert [(i.entering_variable, i.leaving_variable) for i in solution.iterations] == [
        ("x2", "s2"),
        ("x1", "s1"),
        (None, None),
    ]
    first, second, last = solution.iterations
    assert [i.objective_value for i in solution.iterations] == [0, 2400, 3380]
    assert [r.ratio for r in first.ratios] == [100, 30, 40]
    assert [r.ratio for r in second.ratios] == [42, 90, None]
    assert "negativo" in second.ratios[2].exclusion_reason
    assert second.reduced_costs == (Fraction(70, 3), 0, 0, Fraction(-80, 3), 0)
    assert last.reduced_costs == (0, 0, -14, -22, 0)
    assert last.pivot is None and "óptima" in last.entering_reason
    assert first.basis == (2, 3, 4) and second.basis == (2, 1, 4)


def test_initial_canonical_min_and_max():
    solution = solve_big_m(load_problem(PROBLEMS / "ejemplo_2.json"))
    first = solution.iterations[0]
    assert first.objective_value == MValue(0, 9)
    assert first.reduced_costs == (MValue(4, -7), MValue(1, -4), MValue(0, 1), 0, 0, 0)
    assert "restó M" in first.notes[0]
    maximum = solve_big_m(problem((1,), [((1,), ">=", 2), ((1,), "<=", 3)]))
    assert maximum.iterations[0].objective_value == MValue(0, -2)
    assert "sumó M" in maximum.iterations[0].notes[0]


def test_tableau_certificates(fixture_problem):
    original, _ = fixture_problem
    solution = solve_big_m(original)
    standard = solution.standard_form
    assert (solution.iterations[-1].entering_variable is None) == (
        solution.status != Status.UNBOUNDED
    )
    assert solution.iterations[-1].entering_reason
    for iteration in solution.iterations:
        rows = iteration.tableau
        assert tuple(tuple(row[j] for j in iteration.basis) for row in rows) == identity(len(rows))
        assert all(row[-1] >= 0 for row in rows)
        assert all(isinstance(value, Fraction) for row in rows for value in row)
        assert all(iteration.reduced_costs[j] == 0 for j in iteration.basis)
    if solution.status != Status.OPTIMAL:
        return
    basis_matrix = tuple(tuple(row[j] for j in solution.final_basis) for row in standard.a)
    assert matmul(basis_matrix, solution.final_b_inverse) == identity(len(basis_matrix))
    assert matvec(solution.final_b_inverse, standard.b) == tuple(
        row[-1] for row in solution.iterations[-1].tableau
    )
    assert matmul(solution.final_b_inverse, standard.a) == tuple(
        row[:-1] for row in solution.iterations[-1].tableau
    )


def test_infeasible_before_unbounded_real_objective():
    solution = solve_big_m(problem((0, 1), [((1, 0), "<=", 0), ((1, 0), ">=", 1)]))
    assert solution.status == Status.INFEASIBLE
    assert "no tiene solución factible" in solution.message
    assert "artificiales" in solution.message


def test_unbounded_message_and_termination():
    solution = solve_big_m(load_problem(PROBLEMS / "ejemplo_5.json"))
    assert solution.status == Status.UNBOUNDED
    assert "solución no acotada" in solution.message and "x2" in solution.message
    assert not solution.values and solution.objective_value is None
    assert len(solution.iterations) == 2
    last = solution.iterations[-1]
    assert all(row.ratio is None and row.exclusion_reason for row in last.ratios)
    assert "solución no acotada" in last.leaving_reason
    assert solution.unbounded_origin == {"x1": 1, "x2": 0}
    assert solution.unbounded_direction == {"x1": 1, "x2": 1}
    assert "(x1, x2) = (1, 0) + t·(1, 1)" in solution.message
    assert all(
        a.tableau != b.tableau
        for a, b in zip(solution.iterations, solution.iterations[1:], strict=False)
    )


@pytest.mark.parametrize(
    ("objective", "rows"),
    [
        ((1, 0), [((-4, 5), "=", 0), ((-1, 1), "=", 0), ((4, -5), "=", 0)]),
        ((2, 4), [((-3, -2), ">=", 0), ((4, 2), "=", 0), ((-5, -3), "=", 0)]),
        (
            (3, 3, -2),
            [
                ((-1, 4, 1), "=", 0),
                ((-1, 4, 1), "=", 0),
                ((5, 4, 1), "=", 0),
                ((5, 1, -2), "=", 0),
                ((4, 4, 5), "=", 0),
            ],
        ),
    ],
)
def test_redundant_zero_rows_never_reenter_artificials(objective, rows):
    original = problem(objective, rows, sense="min")
    solution = solve_big_m(original)
    assert solution.status == Status.OPTIMAL and solution.objective_value == 0
    assert not any(solution.values.values())
    assert not compare_solution(original, solution, verify_with_scipy(original))
    assert any("nunca vuelve a entrar" in note for note in solution.iterations[0].notes)
    assert all(
        not i.entering_variable or not i.entering_variable.startswith("a")
        for i in solution.iterations
    )


def test_identical_equalities_positive_rhs():
    original = problem((1, 2), [((1, 1), "=", 4), ((1, 1), "=", 4)])
    solution = solve_big_m(original)
    assert solution.values == {"x1": 0, "x2": 4} and solution.objective_value == 8
    assert any("redundante" in note for note in solution.notes)
    assert not compare_solution(original, solution, verify_with_scipy(original))


def test_multiple_segment_and_degenerate_variable():
    solution = solve_big_m(load_problem(PROBLEMS / "ejemplo_6.json"))
    assert solution.values == {"x1": 0, "x2": Fraction(5, 2)}
    assert solution.alternative_solutions == ({"x1": 3, "x2": 1},)
    assert "segmento entre (0, 5/2) y (3, 1)" in solution.message
    degenerate = solve_big_m(load_problem(PROBLEMS / "ejemplo_7.json"))
    assert degenerate.degenerate and not degenerate.multiple_optima
    assert any("variables básicas en 0: x1" in note for note in degenerate.notes)


def test_dependent_equalities_keep_square_basis():
    solution = solve_big_m(problem((1,), [((1,), "=", 1), ((2,), "=", 2)]))
    assert solution.values == {"x1": 1} and not solution.multiple_optima
    assert any("redundante" in note for note in solution.notes)
    assert len(solution.final_b_inverse) == len(solution.final_basis) == 2
    assert solution.iterations[-1].objective_value == 1


def test_zero_artificial_cleanup_with_negative_pivot():
    solution = solve_big_m(problem((0,), [((-1,), "=", 0)], sense="min"))
    assert solution.status == Status.OPTIMAL and not solution.multiple_optima
    assert solution.iterations[0].pivot.value == -1
    assert solution.iterations[0].leaving_variable == "a1"
    assert solution.final_basis == (0,)
    assert any("Retiro de artificial" in note for note in solution.notes)


@pytest.mark.parametrize("bounded", [False, True])
def test_alternative_after_degenerate_pivot(bounded):
    rows = [((1, 0, 0), "<=", 1), ((0, 1, -1), "<=", 0), ((0, -1, 1), "<=", 0)]
    if bounded:
        rows.append(((0, 1, 0), "<=", 2))
    solution = solve_big_m(problem((1, 0, 0), rows))
    assert solution.multiple_optima and solution.values == {"x1": 1, "x2": 0, "x3": 0}
    assert solution.alternative_solutions[0] == {
        "x1": 1,
        "x2": 2 if bounded else 1,
        "x3": 2 if bounded else 1,
    }
    if bounded:
        assert not solution.alternative_rays
    else:
        assert solution.alternative_rays == ({"x1": 0, "x2": 1, "x3": 1},)
        assert "rayo" in solution.message


def test_zero_costs_do_not_prove_multiple_points():
    solution = solve_big_m(problem((0, 0), [((1, 0), "<=", 0), ((0, 1), "<=", 0)]))
    assert not solution.multiple_optima and solution.degenerate


def test_alternative_search_counts_bases_without_row_permutations():
    original = problem(
        (0, 0),
        [((0, 1), "<=", 0), ((0, -1), "<=", 0)] + [((0, 1), "<=", 0)] * 3 + [((1, 1), "<=", 0)],
    )
    solution = solve_big_m(original)
    assert solution.status == Status.OPTIMAL and solution.degenerate
    assert not solution.multiple_optima and solution.values == {"x1": 0, "x2": 0}


def test_beale_switches_to_bland():
    original = problem(
        (10, -57, -9, -24),
        [
            (("1/2", "-11/2", "-5/2", 9), "<=", 0),
            (("1/2", "-3/2", "-1/2", 1), "<=", 0),
            ((1, 0, 0, 0), "<=", 1),
        ],
    )
    solution = solve_big_m(original)
    assert solution.status == Status.OPTIMAL and solution.objective_value == 1
    assert solution.values == {"x1": 1, "x2": 0, "x3": 1, "x4": 0}
    assert len(solution.iterations) == 14
    assert any("Se repitió una base" in note for note in solution.notes)
    assert all("Bland" in i.entering_reason for i in solution.iterations[6:-1])


def test_iteration_limit_is_explicit(example_one, monkeypatch):
    monkeypatch.setattr(big_m, "MAX_ITERATIONS", 1)
    with pytest.raises(ValueError, match="límite de 1 iteraciones"):
        solve_big_m(example_one)
