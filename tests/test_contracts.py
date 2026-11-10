"""Pruebas ejecutables de los contratos que implementará el equipo."""

from fractions import Fraction
from operator import add, eq, ge, gt, le, lt, mul, sub, truediv

import pytest

from plapp.export_pdf import export_steps_pdf
from plapp.io_json import load_problem
from plapp.mvalue import MValue
from plapp.result import Solution, Status
from plapp.standard_form import to_standard_form
from tests.conftest import PROBLEMS


@pytest.mark.parametrize(
    ("operation", "expected"),
    [
        (add, (4, 1)),
        (sub, (2, -5)),
    ],
)
def test_mvalue_binary(operation, expected):
    result = operation(MValue(Fraction(3), Fraction(-2)), MValue(Fraction(1), Fraction(3)))
    assert (result.a, result.b) == tuple(map(Fraction, expected))


@pytest.mark.parametrize(("operation", "expected"), [(mul, (6, -4)), (truediv, ("3/2", -1))])
def test_mvalue_scalar(operation, expected):
    result = operation(MValue(Fraction(3), Fraction(-2)), Fraction(2))
    assert (result.a, result.b) == tuple(map(Fraction, expected))


@pytest.mark.parametrize(
    ("operation", "expected"),
    [
        (lt, True),
        (le, True),
        (gt, False),
        (ge, False),
        (eq, False),
    ],
)
def test_mvalue_lexicographic(operation, expected):
    assert (
        operation(MValue(Fraction(10**30), Fraction(-1)), MValue(Fraction(-(10**30)), Fraction(1)))
        is expected
    )


def test_mvalue_tie_and_string():
    assert MValue(Fraction(2), Fraction(3)) < MValue(Fraction(4), Fraction(3))
    assert MValue(Fraction(2), Fraction(3)) == MValue(Fraction(2), Fraction(3))
    assert str(MValue(Fraction(3), Fraction(-2))) == "3 - 2M"


def test_mvalue_division_by_zero():
    with pytest.raises(ZeroDivisionError):
        MValue(Fraction(1)) / Fraction(0)


def test_standard_form(example_one):
    result = to_standard_form(example_one)
    assert result.column_names[:2] == ("x1", "x2")
    assert result.column_types == ("original", "original", "holgura", "holgura", "holgura")
    assert result.b == (100, 90, 40)
    assert result.basis == (2, 3, 4)
    assert all(isinstance(value, Fraction) for row in result.a for value in row)


def test_standard_form_mixed_min():
    result = to_standard_form(load_problem(PROBLEMS / "ejemplo_2.json"))
    assert all(value >= 0 for value in result.b)
    assert result.column_types.count("artificial") == 2
    assert result.column_types.count("exceso") == 1
    assert result.column_types.count("holgura") == 1
    assert any("R3" in message and "negativo" in message for message in result.transformations)
    for kind, cost in zip(result.column_types, result.c, strict=True):
        if kind == "artificial":
            assert cost.b == 1


@pytest.mark.xfail(raises=NotImplementedError, strict=False, reason="Exportación PDF pendiente")
def test_pdf_output(tmp_path):
    solution = Solution("big_m", Status.OPTIMAL, "Solución óptima", objective_value=Fraction(0))
    path = tmp_path / "pasos.pdf"
    export_steps_pdf(solution, path)
    assert path.read_bytes().startswith(b"%PDF-")
