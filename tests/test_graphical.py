"""Contratos geométricos de regiones acotadas, vacías y no acotadas."""

from fractions import Fraction

import pytest
from hypothesis import given, settings

from plapp.big_m import solve_big_m
from plapp.graphical import graphical_method
from plapp.io_json import load_problem
from plapp.result import Status
from tests.conftest import PROBLEMS
from tests.test_big_m import problem
from tests.test_oracle_scipy import small_problems


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
    assert len(result.lines) == 2 and all(line.points for line in result.lines)


def test_optimal_segment():
    result = graphical_method(load_problem(PROBLEMS / "ejemplo_6.json"))
    assert result.status == Status.OPTIMAL and result.objective_value == 10
    assert set(result.optimal_points) == {(0, Fraction(5, 2)), (3, 1)}
    assert not result.optimal_rays


def test_unbounded_objective():
    original = load_problem(PROBLEMS / "ejemplo_5.json")
    result = graphical_method(original)
    own = solve_big_m(original)
    assert result.status == Status.UNBOUNDED and result.objective_value is None
    assert not result.optimal_points and result.objective_line is None
    assert result.improving_direction == tuple(own.unbounded_direction.values()) == (1, 1)
    assert len(result.improvement_segment) == 2
    assert any(result.improvement_segment[-1][i] == result.drawing_bounds[i] for i in (0, 1))


def test_degenerate_vertex():
    result = graphical_method(load_problem(PROBLEMS / "ejemplo_7.json"))
    assert result.optimal_points == ((0, 2),) and result.objective_value == 18
    assert len(result.vertices) == 3


@pytest.mark.parametrize(
    ("rows", "vertices"),
    [
        ([((1, 1), "=", 4)], {(0, 4), (4, 0)}),
        ([((1, 0), "=", 2), ((0, 1), "<=", 3)], {(2, 0), (2, 3)}),
        ([((1, 1), "=", 0), ((2, 2), "=", 0)], {(0, 0)}),
        ([((1, 1), "=", 1), ((2, 2), "=", 3)], set()),
        ([((1, 0), "<=", 2), ((2, 0), "<=", 4)], {(0, 0), (2, 0)}),
    ],
)
def test_equalities_vertical_parallel_and_coincident(rows, vertices):
    result = graphical_method(problem((1, 2), rows))
    assert {v.point for v in result.vertices} == vertices
    assert result.empty == (not vertices)
    assert all(isinstance(value, Fraction) for v in result.vertices for value in v.point)


def test_optimal_ray_and_box_corners_are_not_vertices():
    result = graphical_method(problem((1, 0), [((1, 0), "<=", 1)]))
    assert not result.bounded and result.status == Status.OPTIMAL
    assert result.objective_value == 1 and result.optimal_rays == ((0, 1),)
    assert result.optimal_points == ((1, 0),)
    assert len(result.feasible_polygon) == 4 and len(result.vertices) == 2
    assert result.optimal_ray_segments[0][0] == (1, 0)


def test_constant_objective_and_asymmetric_scale():
    result = graphical_method(problem((0, 0), [((1, 0), "<=", 10000), ((0, 1), "<=", 1)]))
    assert result.status == Status.OPTIMAL and result.objective_value == 0
    assert len(result.optimal_points) == 4 and result.objective_line is None
    assert result.drawing_bounds[0] / result.drawing_bounds[1] == 10000


def test_consistent_two_variable_fixtures(fixture_problem):
    original, _ = fixture_problem
    if len(original.objective) != 2:
        return
    _assert_consistent(original)


def _assert_consistent(original):
    """Comparar estado y Z exactos; cada método calcula sus propios certificados."""
    graph = graphical_method(original)
    own = solve_big_m(original)
    assert graph.status == own.status
    assert graph.objective_value == own.objective_value
    if graph.status == Status.OPTIMAL:
        assert bool(len(graph.optimal_points) > 1 or graph.optimal_rays) == own.multiple_optima


@settings(max_examples=250, deadline=None, derandomize=True)
@given(small_problems(n=2))
def test_graphical_against_big_m(original):
    _assert_consistent(original)
