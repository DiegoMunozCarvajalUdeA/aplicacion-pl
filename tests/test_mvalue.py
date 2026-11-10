"""Escalares exactos, orden dominante y hash compatible con igualdad."""

from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from plapp.mvalue import MValue


def test_scalars_and_signs():
    value = MValue(3, -2)
    assert isinstance(value.a, Fraction) and isinstance(value.b, Fraction)
    assert -value == MValue(-3, 2)
    assert 2 + value == value + 2 == MValue(5, -2)
    assert 2 - value == MValue(-1, 2)
    assert value - 2 == MValue(1, -2)
    assert 2 * value == value * 2 == MValue(6, -4)
    assert value / 2 == MValue(Fraction(3, 2), -1)
    assert value.is_negative() and not value.is_zero() and not value.is_positive()
    assert MValue(10**100, -1) < 0 < MValue(-(10**100), 1)
    assert MValue().is_zero() and MValue() >= 0 and 0 <= MValue()
    assert sum((value, -value)).is_zero()


@given(st.integers(), st.integers())
def test_hash_and_equality(a, b):
    value = MValue(a, b)
    assert value == MValue(Fraction(a), Fraction(b))
    assert hash(value) == hash(MValue(a, b))
    if b == 0:
        assert value == a == Fraction(a)
        assert hash(value) == hash(a) == hash(Fraction(a))
    assert {value: "valor"}[MValue(a, b)] == "valor"


@pytest.mark.parametrize(
    ("value", "expected"),
    [(MValue(0, -1), "-M"), (MValue(0, 1), "M"), (MValue(5), "5"), (MValue(), "0")],
)
def test_strings(value, expected):
    assert str(value) == expected


def test_unsupported_types():
    assert MValue() != "0"
    for operation in (lambda: MValue(0.1), lambda: MValue() * MValue(), lambda: MValue() < "0"):
        with pytest.raises(TypeError):
            operation()
