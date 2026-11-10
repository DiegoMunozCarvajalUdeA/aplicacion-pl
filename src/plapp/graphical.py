"""Método gráfico independiente: intersecciones y recesión con Fraction."""

from fractions import Fraction
from itertools import combinations

from plapp.formatting import format_expression
from plapp.model import Constraint, LPProblem
from plapp.result import GraphicalResult, GraphLine, GraphVertex, Point, Status

AXES = (((Fraction(1), Fraction(0)), Fraction(0)), ((Fraction(0), Fraction(1)), Fraction(0)))


def _dot(a: Point, b: Point) -> Fraction:
    """Evaluar una fila o la función objetivo sin redondear."""
    return a[0] * b[0] + a[1] * b[1]


def _intersection(a: Point, b: Fraction, c: Point, d: Fraction) -> Point | None:
    """Aplicar Cramer; paralelas o coincidentes no aportan un punto aislado."""
    determinant = a[0] * c[1] - a[1] * c[0]
    if determinant == 0:
        return None
    return ((b * c[1] - a[1] * d) / determinant, (a[0] * d - b * c[0]) / determinant)


def _satisfies(point: Point, rows: tuple[Constraint, ...], homogeneous: bool = False) -> bool:
    """Comprobar el modelo original o el cono de recesión homogéneo."""
    if any(value < 0 for value in point):
        return False
    for row in rows:
        activity = _dot(row.coefficients, point)
        rhs = Fraction(0) if homogeneous else row.rhs
        if (
            (row.relation == "<=" and activity > rhs)
            or (row.relation == ">=" and activity < rhs)
            or (row.relation == "=" and activity != rhs)
        ):
            return False
    return True


def _ordered(points: set[Point]) -> tuple[Point, ...]:
    """Ordenar el contorno convexo con productos cruzados exactos."""
    if len(points) < 3:
        return tuple(sorted(points))

    def cross(o: Point, a: Point, b: Point) -> Fraction:
        """El signo positivo representa un giro antihorario."""
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for chain, ordered in ((lower, sorted(points)), (upper, sorted(points, reverse=True))):
        for point in ordered:
            while len(chain) >= 2 and cross(chain[-2], chain[-1], point) <= 0:
                chain.pop()
            chain.append(point)
    return tuple(lower[:-1] + upper[:-1])


def _recession(rows: tuple[Constraint, ...]) -> tuple[Point, ...]:
    """Buscar rayos extremos entre ejes y perpendiculares a las restricciones."""
    candidates = {(Fraction(1), Fraction(0)), (Fraction(0), Fraction(1))}
    for row in rows:
        a, b = row.coefficients
        candidates.update(((b, -a), (-b, a)))
    # Normalizar elimina direcciones iguales obtenidas de filas escaladas.
    return tuple(
        sorted(
            {
                (d[0] / max(d), d[1] / max(d))
                for d in candidates
                if any(d) and _satisfies(d, rows, homogeneous=True)
            }
        )
    )


def _box_edges(bounds: Point) -> tuple[tuple[Point, Fraction], ...]:
    """Las caras superiores se agregan solo para recortar el dibujo."""
    return AXES + ((AXES[0][0], bounds[0]), (AXES[1][0], bounds[1]))


def _clip_line(a: Point, b: Fraction, bounds: Point) -> tuple[Point, ...]:
    """Intersecar una recta con las cuatro caras de la caja, incluidas verticales."""
    points = set()
    for c, d in _box_edges(bounds):
        point = _intersection(a, b, c, d)
        if point is not None and all(0 <= point[i] <= bounds[i] for i in (0, 1)):
            points.add(point)
    ordered = sorted(points)
    return tuple(ordered if len(ordered) < 2 else (ordered[0], ordered[-1]))


def _clip_ray(origin: Point, direction: Point, bounds: Point) -> tuple[Point, ...]:
    """Terminar un rayo no negativo en la primera cara superior de la caja."""
    step = min((bounds[i] - origin[i]) / direction[i] for i in (0, 1) if direction[i] > 0)
    return origin, (origin[0] + step * direction[0], origin[1] + step * direction[1])


def graphical_method(problem: LPProblem) -> GraphicalResult:
    """Resolver en dos variables con geometría independiente de los solvers.

    Las intersecciones factibles de restricciones y ejes dan los vértices reales.
    Como x ≥ 0, toda región no vacía contiene un vértice. El cono de recesión
    certifica acotación y mejora ilimitada; las caras de la caja solo dibujan.
    """
    if len(problem.objective) != 2:
        return GraphicalResult(False, "El método gráfico no aplica: requiere dos variables.")
    boundaries = tuple((row.coefficients, row.rhs) for row in problem.constraints) + AXES
    intersections = {
        point
        for (a, b), (c, d) in combinations(boundaries, 2)
        if (point := _intersection(a, b, c, d)) is not None
    }
    vertices = _ordered({p for p in intersections if _satisfies(p, problem.constraints)})
    # Por eje: vértices e interceptos no negativos, con 20 % de margen.
    reference = set(vertices) | {
        p for p in intersections if min(p) >= 0 and (p[0] == 0 or p[1] == 0)
    }
    bounds = tuple(max([Fraction(1), *(p[i] for p in reference)]) * Fraction(6, 5) for i in (0, 1))
    symbols = {"<=": "≤", ">=": "≥", "=": "="}
    lines = tuple(
        GraphLine(
            f"{row.name}: {format_expression(row.coefficients, problem.variable_names)} "
            f"{symbols[row.relation]} {row.rhs}",
            row.coefficients,
            row.rhs,
            _clip_line(row.coefficients, row.rhs, bounds),
        )
        for row in problem.constraints
    )
    if not vertices:
        return GraphicalResult(
            True,
            "El problema no tiene solución factible: la región está vacía.",
            lines=lines,
            empty=True,
            status=Status.INFEASIBLE,
            drawing_bounds=bounds,
        )
    clipped = {
        point
        for (a, b), (c, d) in combinations(boundaries + _box_edges(bounds)[2:], 2)
        if (point := _intersection(a, b, c, d)) is not None
        and _satisfies(point, problem.constraints)
        and all(point[i] <= bounds[i] for i in (0, 1))
    }
    directions = _recession(problem.constraints)
    evaluated = tuple(GraphVertex(p, _dot(problem.objective, p)) for p in vertices)
    sign = 1 if problem.sense == "max" else -1
    improving = next((d for d in directions if sign * _dot(problem.objective, d) > 0), None)
    common = dict(
        lines=lines,
        feasible_polygon=_ordered(clipped),
        vertices=evaluated,
        bounded=not directions,
        empty=False,
        recession_directions=directions,
        drawing_bounds=bounds,
    )
    if improving is not None:
        return GraphicalResult(
            True,
            "El problema tiene solución no acotada: una dirección factible mejora Z sin límite.",
            status=Status.UNBOUNDED,
            improving_direction=improving,
            improvement_segment=_clip_ray(vertices[0], improving, bounds),
            **common,
        )
    objective = max(sign * vertex.objective_value for vertex in evaluated) * sign
    optima = tuple(v.point for v in evaluated if v.objective_value == objective)
    rays = tuple(d for d in directions if _dot(problem.objective, d) == 0)
    reason = "Se encontró una solución óptima por el método gráfico."
    if rays:
        reason += " Hay un rayo de soluciones óptimas múltiples."
    elif len(optima) > 1:
        reason += " Hay un segmento de soluciones óptimas múltiples."
    objective_line = (
        GraphLine(
            f"Isoutilidad: Z = {objective}",
            problem.objective,
            objective,
            _clip_line(problem.objective, objective, bounds),
        )
        if any(problem.objective)
        else None
    )
    return GraphicalResult(
        True,
        reason,
        optimal_points=optima,
        objective_line=objective_line,
        status=Status.OPTIMAL,
        objective_value=objective,
        optimal_rays=rays,
        optimal_ray_segments=tuple(_clip_ray(optima[0], d, bounds) for d in rays),
        **common,
    )
