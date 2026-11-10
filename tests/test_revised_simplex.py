"""Equivalencia de métodos y certificados independientes de cada B⁻¹."""

import json
from dataclasses import replace
from fractions import Fraction

import pytest

from plapp import revised_simplex
from plapp.big_m import solve_big_m
from plapp.io_json import load_problem
from plapp.linalg import column, identity, invert, matmul, matvec
from plapp.mvalue import MValue
from plapp.result import Status
from plapp.revised_simplex import solve_revised, update_inverse
from plapp.sensitivity import sensitivity_analysis
from tests.test_simplex_traces import TRACES


@pytest.mark.parametrize("case", TRACES, ids=lambda case: case["case"])
def test_same_path_and_inverse_certificates(case, monkeypatch):
    """La inversa se comprueba con Gauss-Jordan, sin reutilizar la actualización E."""
    original = load_problem(json.dumps(case["problem"]))
    big_m = solve_big_m(original)
    products = []

    def track_product(left, right):
        """Contar reconstrucciones completas para detectar un tablero mantenido por error."""
        products.append((left, right))
        return matmul(left, right)

    monkeypatch.setattr(revised_simplex, "matmul", track_product)
    revised = solve_revised(original)
    assert replace(revised, method="big_m", iterations=big_m.iterations) == big_m
    assert len(revised.iterations) == len(big_m.iterations)
    standard = revised.standard_form
    for state, tableau_state in zip(revised.iterations, big_m.iterations, strict=True):
        # Todo salvo la representación del estado debe coincidir, incluso las decisiones.
        assert (
            replace(
                state,
                tableau=tableau_state.tableau,
                b_inverse=None,
                basic_values=(),
                multipliers=(),
            )
            == tableau_state
        )
        basis_matrix = tuple(tuple(row[j] for j in state.basis) for row in standard.a)
        assert state.tableau is None
        assert state.b_inverse == invert(basis_matrix)
        assert matmul(basis_matrix, state.b_inverse) == identity(len(state.basis))
        assert state.basic_values == matvec(state.b_inverse, standard.b)
        assert state.basic_values == tuple(row[-1] for row in tableau_state.tableau)
        expected_y = tuple(
            sum(
                (standard.c[basic] * state.b_inverse[k][i] for k, basic in enumerate(state.basis)),
                MValue(),
            )
            for i in range(len(state.basis))
        )
        assert state.multipliers == expected_y
        assert all(isinstance(y, MValue) for y in state.multipliers)
        if state.pivot:
            d = matvec(state.b_inverse, column(standard.a, state.pivot.column))
            assert d[state.pivot.row] == state.pivot.value
            assert (
                update_inverse(state.b_inverse, d, state.pivot.row)
                == revised.iterations[state.number + 1].b_inverse
            )
    # B⁻¹A solo se construye para retiro de artificiales y posproceso, nunca por pivote normal.
    postprocess_states = sum(
        i.entering_variable is None
        and revised.status == Status.OPTIMAL
        or any("Retiro de artificial" in note for note in i.notes)
        for i in revised.iterations
    )
    assert len(products) == postprocess_states
    if revised.status == Status.OPTIMAL:
        assert sensitivity_analysis(original, revised) == sensitivity_analysis(original, big_m)


@pytest.mark.parametrize("direction,row", [((2, -1, 3), 0), ((1, -2, 0), 1)])
def test_elementary_matrix_product(direction, row):
    """Construir E explícitamente para comprobar el producto, también con pivote negativo."""
    inverse = invert(tuple(tuple(map(Fraction, r)) for r in ((1, 2, 0), (0, 1, 1), (1, 0, 1))))
    d = tuple(map(Fraction, direction))
    elementary = tuple(
        tuple(
            (Fraction(1) if i == row else -d[i]) / d[row] if j == row else Fraction(i == j)
            for j in range(3)
        )
        for i in range(3)
    )
    assert update_inverse(inverse, d, row) == matmul(elementary, inverse)


def test_zero_pivot_and_iteration_limit(example_one, monkeypatch):
    """Rechazar actualizaciones indefinidas y conservar una protección explícita."""
    with pytest.raises(ValueError, match="pivote cero"):
        update_inverse(identity(1), (Fraction(0),), 0)
    monkeypatch.setattr(revised_simplex, "MAX_ITERATIONS", 1)
    with pytest.raises(ValueError, match="límite de 1 iteraciones"):
        solve_revised(example_one)
