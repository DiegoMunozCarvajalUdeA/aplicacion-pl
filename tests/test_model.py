"""Validación de números, dimensiones y ubicaciones de errores."""

from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from plapp.io_json import problem_to_dict
from plapp.model import Constraint, LPProblem, parse_number, validate


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("  -3  ", Fraction(-3)),
        ("2,5", Fraction(5, 2)),
        ("2.5", Fraction(5, 2)),
        (" 2 / 5 ", Fraction(2, 5)),
        ("-2/5", Fraction(-2, 5)),
        (0, Fraction(0)),
        (0.1, Fraction(1, 10)),
        (Fraction(2, 3), Fraction(2, 3)),
    ],
)
def test_parse_number(text, expected):
    assert parse_number(text) == expected


@pytest.mark.parametrize("text", ["", "  ", "hola", "1/0", "1,2,3", None, True, [], "NaN", "inf"])
def test_invalid_number(text):
    with pytest.raises(ValueError, match="número|Número|vacío"):
        parse_number(text)


@given(st.integers(-(10**9), 10**9), st.integers(1, 10**9))
def test_fraction_round_trip(numerator, denominator):
    value = Fraction(numerator, denominator)
    assert parse_number(str(value)) == value


def test_defaults():
    problem = LPProblem((Fraction(1),), (Constraint((Fraction(1),), "<=", Fraction(2)),))
    assert problem.variable_names == ("x1",)
    assert problem.constraints[0].name == "R1"


def test_valid_model(example_one):
    problem, issues = validate(problem_to_dict(example_one))
    assert not issues
    assert problem == example_one
    assert all(isinstance(value, Fraction) for value in problem.objective)


@pytest.mark.parametrize(
    ("field", "value", "location"),
    [
        ("objetivo", [], "objetivo"),
        ("restricciones", [], "restricciones"),
        ("sentido", "MAX", "sentido"),
        ("variables", ["x1"], "variables"),
        ("variables", ["x1", "x1"], "variables"),
        ("variables", ["", "x2"], "variables"),
        ("n", 0, "n"),
        ("n", 3, "n"),
        ("m", -1, "m"),
        ("m", True, "m"),
        ("nombre", "", "nombre"),
        ("objetivo", "12", "objetivo"),
    ],
)
def test_invalid_fields(example_one, field, value, location):
    raw = problem_to_dict(example_one)
    raw[field] = value
    problem, issues = validate(raw)
    assert problem is None
    assert any(issue.location == location for issue in issues)


def test_all_cell_errors(example_one):
    raw = problem_to_dict(example_one)
    raw["objetivo"][0] = ""
    raw["restricciones"][1]["coeficientes"][1] = "abc"
    raw["restricciones"][0]["rhs"] = "1/0"
    problem, issues = validate(raw)
    assert problem is None
    assert {issue.location for issue in issues} == {
        "objetivo, x1",
        "restricción 2, x2",
        "lado derecho de R1",
    }


@pytest.mark.parametrize(
    "change",
    [
        {"coeficientes": ["1"]},
        {"coeficientes": ["0", "0"]},
        {"signo": "<"},
        {"nombre": ""},
        {"rhs": None},
    ],
)
def test_invalid_constraint(example_one, change):
    raw = problem_to_dict(example_one)
    raw["restricciones"][0].update(change)
    assert validate(raw)[0] is None


@pytest.mark.parametrize("raw", [None, [], "texto", {"objetivo": None, "restricciones": [None]}])
def test_malformed_shape(raw):
    problem, issues = validate(raw)
    assert problem is None and issues
