"""Presentación exacta y decimal independiente de los algoritmos pendientes."""

from fractions import Fraction

import pytest

from plapp.formatting import format_expression, format_number
from plapp.mvalue import MValue


@pytest.mark.parametrize(
    ("value", "text"),
    [
        (Fraction(2, 5), "2/5"),
        (Fraction(-2), "-2"),
        (Fraction(0), "0"),
        (MValue(Fraction(3), Fraction(-2)), "3 - 2M"),
        (MValue(Fraction(0), Fraction(1)), "M"),
        (MValue(Fraction(0), Fraction(-1)), "-M"),
        (MValue(Fraction(2, 3), Fraction(1, 2)), "2/3 + 1/2M"),
        (MValue(Fraction(0), Fraction(0)), "0"),
    ],
)
def test_fraction_format(value, text):
    assert format_number(value) == text


def test_decimal_format():
    assert format_number(Fraction(2, 3), "decimal", 3) == "0.667"
    assert format_number(Fraction(-1, 10000), "decimal", 2) == "0"
    assert format_number(MValue(Fraction(1, 3), Fraction(-2)), "decimal", 2) == "0.33 - 2M"
    assert format_number(Fraction(4), "decimal", 4) == "4"
    assert format_number(Fraction(-3, 2), "decimal", 4) == "-1.5"
    assert format_number(Fraction(10), "decimal", 0) == "10"
    assert format_number(Fraction(10**100, 3), "decimal", 2).endswith(".33")


@pytest.mark.parametrize(("mode", "decimals"), [("otro", 2), ("decimal", -1), ("decimal", 13)])
def test_invalid_format(mode, decimals):
    with pytest.raises(ValueError):
        format_number(Fraction(1), mode, decimals)


def test_expression():
    assert format_expression((Fraction(2), Fraction(-1)), ("x1", "x2")) == "2·x1 - 1·x2"
