"""Operaciones exactas y rechazo de matrices inválidas."""

from fractions import Fraction

import pytest

from plapp.linalg import column, identity, invert, matmul, matvec, vecmat


@pytest.mark.parametrize("rows", [((0, 2), (3, 4)), ((2, 1, 0), (1, 3, 0), (0, 1, 1))])
def test_inverse_both_products(rows):
    matrix = tuple(tuple(map(Fraction, row)) for row in rows)
    inverse = invert(matrix)
    assert matmul(matrix, inverse) == matmul(inverse, matrix) == identity(len(rows))
    assert all(isinstance(value, Fraction) for row in inverse for value in row)


def test_products_and_column():
    matrix = ((Fraction(1), Fraction(2)), (Fraction(3), Fraction(4)))
    assert column(matrix, 1) == (2, 4)
    assert matvec(matrix, (Fraction(2), Fraction(3))) == (8, 18)
    assert vecmat((Fraction(2), Fraction(3)), matrix) == (11, 16)
    assert identity(0) == invert(()) == ()


def test_singular():
    with pytest.raises(ValueError, match="singular"):
        invert(((Fraction(1), Fraction(2)), (Fraction(2), Fraction(4))))


@pytest.mark.parametrize(
    "operation",
    [
        lambda: invert(((Fraction(1), Fraction(2)),)),
        lambda: matvec(((Fraction(1),), ()), (Fraction(1),)),
        lambda: matvec(identity(2), (Fraction(1),)),
        lambda: vecmat((Fraction(1),), identity(2)),
        lambda: matmul(identity(2), identity(3)),
        lambda: column(identity(2), -1),
        lambda: identity(-1),
    ],
)
def test_invalid_dimensions(operation):
    with pytest.raises(ValueError):
        operation()
