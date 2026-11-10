"""Álgebra lineal pequeña y exacta para los métodos propios."""

from fractions import Fraction

from plapp.result import Matrix


def _width(matrix: Matrix) -> int:
    """Rechazar filas desiguales antes de cualquier operación."""
    width = len(matrix[0]) if matrix else 0
    if any(len(row) != width for row in matrix):
        raise ValueError("La matriz debe ser rectangular.")
    return width


def identity(n: int) -> Matrix:
    """Construir la identidad n × n con Fraction."""
    if n < 0:
        raise ValueError("El tamaño de la identidad no puede ser negativo.")
    return tuple(tuple(Fraction(i == j) for j in range(n)) for i in range(n))


def column(matrix: Matrix, j: int) -> tuple[Fraction, ...]:
    """Extraer una columna sin alterar la matriz."""
    if not 0 <= j < _width(matrix):
        raise ValueError("El índice de columna está fuera de la matriz.")
    return tuple(Fraction(row[j]) for row in matrix)


def matvec(matrix: Matrix, vector: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    """Multiplicar A por un vector columna de dimensión compatible."""
    if _width(matrix) != len(vector):
        raise ValueError("Dimensiones incompatibles para matriz por vector.")
    return tuple(
        sum((Fraction(a) * b for a, b in zip(row, vector, strict=True)), Fraction(0))
        for row in matrix
    )


def vecmat(vector: tuple[Fraction, ...], matrix: Matrix) -> tuple[Fraction, ...]:
    """Multiplicar un vector fila por A."""
    width = _width(matrix)
    if len(vector) != len(matrix):
        raise ValueError("Dimensiones incompatibles para vector por matriz.")
    return tuple(
        sum((Fraction(vector[i]) * matrix[i][j] for i in range(len(matrix))), Fraction(0))
        for j in range(width)
    )


def matmul(left: Matrix, right: Matrix) -> Matrix:
    """Multiplicar matrices por productos de filas y columnas."""
    width = _width(right)
    if _width(left) != len(right):
        raise ValueError("Dimensiones incompatibles para el producto de matrices.")
    return tuple(
        tuple(
            sum((Fraction(a) * b for a, b in zip(row, column(right, j), strict=True)), Fraction(0))
            for j in range(width)
        )
        for row in left
    )


def invert(matrix: Matrix) -> Matrix:
    """Reducir [A | I] con Gauss-Jordan; intercambiar filas si el pivote es cero."""
    n = len(matrix)
    if _width(matrix) != n:
        raise ValueError("Solo se puede invertir una matriz cuadrada.")
    augmented = [
        list(map(Fraction, row + unit)) for row, unit in zip(matrix, identity(n), strict=True)
    ]
    for j in range(n):
        pivot_row = next((i for i in range(j, n) if augmented[i][j] != 0), None)
        if pivot_row is None:
            raise ValueError("La matriz es singular: no tiene inversa.")
        augmented[j], augmented[pivot_row] = augmented[pivot_row], augmented[j]
        pivot = augmented[j][j]
        augmented[j] = [value / pivot for value in augmented[j]]
        for i in range(n):
            if i != j:
                factor = augmented[i][j]
                augmented[i] = [
                    value - factor * basis_value
                    for value, basis_value in zip(augmented[i], augmented[j], strict=True)
                ]
    return tuple(tuple(row[n:]) for row in augmented)
