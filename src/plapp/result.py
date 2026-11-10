"""Contratos compartidos de ambos métodos y de las vistas de resultados.

Los índices de base y pivote empiezan en cero. Un tablero incluye la columna
derecha; column_names de StandardForm contiene solo columnas de variables.
Los costos reducidos siguen r = c - c_B B⁻¹ A, en el sentido original de Z.
"""

from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Literal

from plapp.mvalue import MValue

Matrix = tuple[tuple[Fraction, ...], ...]
Point = tuple[Fraction, Fraction]
Bounds = tuple[Fraction | None, Fraction | None]
Method = Literal["big_m", "revised"]


class Status(Enum):
    """Estados terminales; multiplicidad y degeneración son banderas separadas."""

    OPTIMAL = "optimo"
    INFEASIBLE = "infactible"
    UNBOUNDED = "no_acotado"


@dataclass(frozen=True)
class StandardForm:
    """Forma estándar exacta y trazabilidad de cada transformación."""

    column_names: tuple[str, ...]
    column_types: tuple[Literal["original", "holgura", "exceso", "artificial"], ...]
    a: Matrix
    b: tuple[Fraction, ...]
    c: tuple[MValue, ...]
    basis: tuple[int, ...]
    transformations: tuple[str, ...]
    row_signs: tuple[int, ...] = ()


@dataclass(frozen=True)
class RatioRow:
    """Una fila de la razón mínima; None requiere explicar la exclusión."""

    row: int
    basic_variable: str
    rhs: Fraction
    coefficient: Fraction
    ratio: Fraction | None
    exclusion_reason: str = ""


@dataclass(frozen=True)
class Pivot:
    """Ubicación y valor exacto del pivote, con índices desde cero."""

    row: int
    column: int
    value: Fraction


@dataclass(frozen=True)
class Iteration:
    """Estado anterior al pivote y justificaciones para reproducir una iteración."""

    number: int
    basis: tuple[int, ...]
    tableau: tuple[tuple[Fraction | MValue, ...], ...] | None = None
    b_inverse: Matrix | None = None
    reduced_costs: tuple[Fraction | MValue, ...] = ()
    entering_variable: str | None = None
    entering_reason: str = ""
    ratios: tuple[RatioRow, ...] = ()
    leaving_variable: str | None = None
    leaving_reason: str = ""
    pivot: Pivot | None = None
    objective_value: Fraction | MValue | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Solution:
    """Resultado común; Z y valores pueden faltar cuando no hay óptimo."""

    method: Method
    status: Status
    message: str
    values: dict[str, Fraction] = field(default_factory=dict)
    objective_value: Fraction | None = None
    slacks: dict[str, Fraction] = field(default_factory=dict)
    standard_form: StandardForm | None = None
    iterations: tuple[Iteration, ...] = ()
    final_basis: tuple[int, ...] = ()
    final_b_inverse: Matrix | None = None
    multiple_optima: bool = False
    degenerate: bool = False
    alternative_solutions: tuple[dict[str, Fraction], ...] = ()
    notes: tuple[str, ...] = ()
    alternative_rays: tuple[dict[str, Fraction], ...] = ()
    unbounded_origin: dict[str, Fraction] = field(default_factory=dict)
    unbounded_direction: dict[str, Fraction] = field(default_factory=dict)


@dataclass(frozen=True)
class SensitivityReport:
    """Derivadas de Z original; None indica infinito en los límites de rangos."""

    shadow_prices: dict[str, Fraction]
    reduced_costs: dict[str, Fraction]
    objective_ranges: dict[str, Bounds]
    rhs_ranges: dict[str, Bounds]
    interpretations: dict[str, str]


@dataclass(frozen=True)
class GraphLine:
    """Recta exacta; puntos ya recortados para dibujar sin calcular geometría en UI."""

    label: str
    coefficients: Point
    rhs: Fraction
    points: tuple[Point, ...] = ()


@dataclass(frozen=True)
class GraphVertex:
    """Vértice factible y valor de la función objetivo."""

    point: Point
    objective_value: Fraction


@dataclass(frozen=True)
class GraphicalResult:
    """La región recortada para dibujo no prueba acotación ni agrega vértices reales."""

    applicable: bool
    reason: str = ""
    lines: tuple[GraphLine, ...] = ()
    feasible_polygon: tuple[Point, ...] = ()
    vertices: tuple[GraphVertex, ...] = ()
    bounded: bool | None = None
    empty: bool | None = None
    optimal_points: tuple[Point, ...] = ()
    objective_line: GraphLine | None = None
    status: Status | None = None
    objective_value: Fraction | None = None
    recession_directions: tuple[Point, ...] = ()
    optimal_rays: tuple[Point, ...] = ()
    improving_direction: Point | None = None
    drawing_bounds: Point = (Fraction(1), Fraction(1))
    improvement_segment: tuple[Point, ...] = ()
    optimal_ray_segments: tuple[tuple[Point, ...], ...] = ()
