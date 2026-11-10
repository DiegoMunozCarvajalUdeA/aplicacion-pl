"""Aceptación de ambos métodos sobre todos los problemas de referencia."""

from fractions import Fraction

import pytest

from plapp.big_m import solve_big_m
from plapp.result import Status
from plapp.revised_simplex import solve_revised


def on_segment(point, segment):
    """Aceptar cualquier óptimo alterno: debe ser combinación convexa de los extremos."""
    start, end = ([Fraction(value) for value in vertex] for vertex in segment)
    direction = [b - a for a, b in zip(start, end, strict=True)]
    index = next(i for i, value in enumerate(direction) if value)
    t = (point[index] - start[index]) / direction[index]
    return 0 <= t <= 1 and all(
        a + t * d == x for a, d, x in zip(start, direction, point, strict=True)
    )


@pytest.mark.parametrize(
    "solver",
    [
        pytest.param(solve_big_m, id="gran_m"),
        pytest.param(
            solve_revised,
            id="revisado",
        ),
    ],
)
def test_examples(fixture_problem, solver):
    problem, expected = fixture_problem
    solution = solver(problem)
    assert solution.status.value == expected["estado"]
    assert solution.message.strip()
    if solution.status != Status.OPTIMAL:
        assert expected["mensaje"] in solution.message.lower()
        return
    assert solution.objective_value == Fraction(expected["z"])
    assert set(solution.values) == set(problem.variable_names)
    values = [solution.values[name] for name in problem.variable_names]
    assert all(isinstance(value, Fraction) and value >= 0 for value in values)
    assert (
        sum(c * x for c, x in zip(problem.objective, values, strict=True))
        == solution.objective_value
    )
    for row in problem.constraints:
        activity = sum(a * x for a, x in zip(row.coefficients, values, strict=True))
        slack = activity - row.rhs if row.relation == ">=" else row.rhs - activity
        assert slack == 0 if row.relation == "=" else slack >= 0
        assert solution.slacks[row.name] == slack
    if expected["multiples"]:
        assert solution.multiple_optima
        assert on_segment(values, expected["segmento"])
    else:
        assert solution.values == {name: Fraction(value) for name, value in expected["x"].items()}
        assert not solution.multiple_optima
    if expected["degenerado"]:
        assert solution.degenerate
