"""Base identidad, orden de columnas y normalización de todos los fixtures."""

from dataclasses import replace
from fractions import Fraction

from plapp.io_json import load_problem
from plapp.linalg import identity
from plapp.model import Constraint, LPProblem
from plapp.mvalue import MValue
from plapp.standard_form import to_standard_form
from tests.conftest import PROBLEMS


def test_all_fixtures(fixture_problem):
    problem, _ = fixture_problem
    standard = to_standard_form(problem)
    assert standard.row_signs == tuple(-1 if row.rhs < 0 else 1 for row in problem.constraints)
    assert all(value >= 0 for value in standard.b)
    assert tuple(tuple(row[j] for j in standard.basis) for row in standard.a) == identity(
        len(problem.constraints)
    )
    expected = {"original": len(problem.objective), "holgura": 0, "exceso": 0, "artificial": 0}
    for row, sign in zip(problem.constraints, standard.row_signs, strict=True):
        relation = row.relation
        if sign < 0:
            relation = {"<=": ">=", ">=": "<=", "=": "="}[relation]
        if relation != "=":
            expected["holgura" if relation == "<=" else "exceso"] += 1
        if relation != "<=":
            expected["artificial"] += 1
    for kind, count in expected.items():
        assert standard.column_types.count(kind) == count
    assert standard.column_names[: len(problem.objective)] == problem.variable_names
    assert len(set(standard.column_names)) == len(standard.column_names)
    for kind, cost in zip(standard.column_types, standard.c, strict=True):
        if kind == "artificial":
            assert cost == MValue(b=Fraction(-1 if problem.sense == "max" else 1))


def test_mixed_order_and_signs():
    problem = load_problem(PROBLEMS / "ejemplo_2.json")
    result = to_standard_form(problem)
    assert result.column_names == ("x1", "x2", "e2", "s3", "a1", "a2")
    assert result.row_signs == (1, 1, -1)
    assert result.basis == (4, 5, 3)
    assert result.a[2] == (1, 2, 0, 1, 0, 0)
    assert problem.constraints[2].rhs == -4
    assert to_standard_form(replace(problem, sense="max")).c[-1] == MValue(b=Fraction(-1))


def test_names_and_negative_equality():
    problem = LPProblem(
        (Fraction(1), Fraction(2), Fraction(3)),
        (
            Constraint((Fraction(1), Fraction(1), Fraction(1)), "<=", Fraction(2)),
            Constraint((Fraction(-1), Fraction(-1), Fraction(-1)), "=", Fraction(-2)),
        ),
        variable_names=("s1", "s1_1", "a2"),
    )
    result = to_standard_form(problem)
    assert result.column_names == ("s1", "s1_1", "a2", "s1_2", "a2_1")
    assert result.row_signs == (1, -1)
    assert result.a[1][:3] == (1, 1, 1)
