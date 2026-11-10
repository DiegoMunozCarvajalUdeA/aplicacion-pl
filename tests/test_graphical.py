"""Contratos geométricos de regiones acotadas, vacías y no acotadas."""

from fractions import Fraction

import pytest

from plapp.graphical import graphical_method
from plapp.io_json import load_problem
from tests.conftest import PROBLEMS

pytestmark = pytest.mark.xfail(
    raises=NotImplementedError, strict=False, reason="Geometría pendiente"
)


def test_example_one_vertices(example_one):
    result = graphical_method(example_one)
    assert result.applicable and result.bounded and not result.empty
    assert {vertex.point for vertex in result.vertices} == {(0, 0), (50, 0), (42, 16), (0, 30)}
    assert {(vertex.point, vertex.objective_value) for vertex in result.vertices} == {
        ((0, 0), 0),
        ((50, 0), 2500),
        ((42, 16), 3380),
        ((0, 30), 2400),
    }
    assert result.optimal_points == ((Fraction(42), Fraction(16)),)
    assert result.objective_line is not None
    assert len(result.lines) == 3
    # R3: x2 <= 40 no corta la región ni agrega vértices.
    assert all(vertex.point[1] < 40 for vertex in result.vertices)


def test_three_variables_not_applicable():
    result = graphical_method(load_problem(PROBLEMS / "ejemplo_3.json"))
    assert not result.applicable
    assert "no aplica" in result.reason.lower()


def test_unbounded_region_finite_optimum():
    result = graphical_method(load_problem(PROBLEMS / "extra_1.json"))
    assert result.applicable and result.bounded is False and result.empty is False
    assert (Fraction(2), Fraction(1)) in result.optimal_points
    assert result.feasible_polygon


def test_empty_region():
    result = graphical_method(load_problem(PROBLEMS / "extra_3.json"))
    assert result.applicable and result.empty
    assert not result.vertices and not result.optimal_points
