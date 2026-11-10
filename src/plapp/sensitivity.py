"""Sensibilidad exacta de una base óptima, independiente del tablero del solver."""

from dataclasses import replace
from fractions import Fraction

from plapp.formatting import NumberFormat, format_number
from plapp.linalg import invert, matmul, matvec, vecmat
from plapp.model import LPProblem
from plapp.result import Bounds, SensitivityReport, Solution, Status


def _interval(conditions: list[tuple[Fraction, Fraction]]) -> Bounds:
    """Intersecar desigualdades valor + pendiente·Δ ≥ 0 con extremos infinitos."""
    lower = upper = None
    for value, slope in conditions:
        if slope > 0:
            bound = -value / slope
            lower = bound if lower is None else max(lower, bound)
        elif slope < 0:
            bound = -value / slope
            upper = bound if upper is None else min(upper, bound)
        elif value < 0:
            raise ValueError("La base suministrada no es factible y óptima para este modelo.")
    if lower is not None and upper is not None and lower > upper:
        raise ValueError("Los rangos de la base suministrada son incompatibles.")
    return lower, upper


def _translate(bounds: Bounds, current: Fraction) -> Bounds:
    """Pasar de intervalos de Δ a valores del dato original."""
    return tuple(None if bound is None else current + bound for bound in bounds)


def sensitivity_interpretations(
    problem: LPProblem,
    report: SensitivityReport,
    mode: NumberFormat = "fraction",
    decimals: int = 4,
) -> dict[str, str]:
    """Explicar los datos exactos con el mismo formato numérico de las tablas."""

    def number(value: Fraction) -> str:
        return format_number(value, mode, decimals)

    def interval(bounds: Bounds) -> str:
        low, high = bounds
        lower = number(low) if low is not None else "−∞"
        upper = number(high) if high is not None else "+∞"
        return f"entre {lower} y {upper}"

    descriptions = {}
    for row in problem.constraints:
        if row.name not in report.rhs_ranges:
            descriptions[f"b:{row.name}"] = (
                f"{row.name}: precio sombra no único: fila redundante. Se elige y = 0 "
                "como representante dual; no se informa rango para este lado derecho. "
                "Cambiarlo por separado puede romper la dependencia y hacer el modelo infactible."
            )
            continue
        price = report.shadow_prices[row.name]
        change = (
            f"aumenta Z en {number(price)}"
            if price > 0
            else f"disminuye Z en {number(-price)}"
            if price < 0
            else "no cambia Z"
        )
        bounds = report.rhs_ranges[row.name]
        descriptions[f"b:{row.name}"] = (
            f"Cada unidad adicional de {row.name} {change} mientras su lado derecho esté "
            f"{interval(bounds)}, variando solo ese dato y conservando esta base."
        )
        if bounds == (row.rhs, row.rhs):
            descriptions[f"b:{row.name}"] += (
                " El intervalo se reduce al valor actual: no admite una perturbación "
                "aislada no nula; el precio es un representante dual."
            )
    for name in problem.variable_names:
        descriptions[f"c:{name}"] = (
            f"El coeficiente de {name} puede variar {interval(report.objective_ranges[name])} "
            "manteniendo los demás datos y esta base óptima. "
            "Los extremos pueden admitir otro óptimo."
        )
        condition = "≤ 0" if problem.sense == "max" else "≥ 0"
        descriptions[f"r:{name}"] = (
            f"{name}: costo reducido {number(report.reduced_costs[name])}, con r = c − yA; "
            f"la optimalidad exige r {condition}. Mide el cambio marginal de Z "
            "al introducir una variable no básica."
        )
    return descriptions


def sensitivity_analysis(problem: LPProblem, solution: Solution) -> SensitivityReport:
    """Calcular y, costos reducidos y rangos variando un solo dato a la vez.

    Se reconstruye B desde A y final_basis, sin consultar iteraciones ni la
    inversa guardada por el solver. Las artificiales básicas nulas identifican
    igualdades redundantes: se retiran su columna y su fila original para
    obtener un representante dual con precio cero en esas filas. Los rangos de
    las filas conservadas también respetan las dependencias del sistema completo.
    """
    if solution.status != Status.OPTIMAL or solution.standard_form is None:
        raise ValueError(
            "El análisis de sensibilidad requiere una solución óptima y forma estándar."
        )
    standard, basis = solution.standard_form, solution.final_basis
    if len(basis) != len(standard.a) or len(set(basis)) != len(basis):
        raise ValueError("La base final debe tener una columna distinta por restricción.")
    full_inverse = invert(tuple(tuple(row[j] for j in basis) for row in standard.a))
    full_values = matvec(full_inverse, standard.b)
    if any(value < 0 for value in full_values):
        raise ValueError("La base final no es factible.")
    artificial_positions = [
        k for k, j in enumerate(basis) if standard.column_types[j] == "artificial"
    ]
    if any(full_values[k] != 0 for k in artificial_positions):
        raise ValueError(
            "Una artificial positiva impide analizar sensibilidad de un óptimo factible."
        )
    # Cada artificial es un vector unitario de una fila original. Se elimina
    # esa fila, que puede diferir de la posición de la artificial en el tablero.
    removed_rows = {
        next(i for i, row in enumerate(standard.a) if row[basis[k]] != 0)
        for k in artificial_positions
    }
    kept_rows = [i for i in range(len(standard.a)) if i not in removed_rows]
    reduced_basis = tuple(j for k, j in enumerate(basis) if k not in artificial_positions)
    a = tuple(standard.a[i] for i in kept_rows)
    b = tuple(standard.b[i] for i in kept_rows)
    inverse = invert(tuple(tuple(row[j] for j in reduced_basis) for row in a))
    values = matvec(inverse, b)
    transformed = matmul(inverse, a)
    dual = vecmat(tuple(standard.c[j].a for j in reduced_basis), inverse)
    normalized_prices = {i: dual[k] for k, i in enumerate(kept_rows)}
    signs = standard.row_signs or tuple(-1 if row.rhs < 0 else 1 for row in problem.constraints)
    prices = {
        row.name: signs[i] * normalized_prices.get(i, Fraction(0))
        for i, row in enumerate(problem.constraints)
    }
    reduced = tuple(
        cost.a - sum((dual[k] * a[k][j] for k in range(len(a))), Fraction(0))
        for j, cost in enumerate(standard.c)
    )
    nonbasic = [
        j
        for j, kind in enumerate(standard.column_types)
        if j not in reduced_basis and kind != "artificial"
    ]
    # Todos los costos reducidos de no básicas deben ser no negativos en Min
    # o no positivos en Max. Las artificiales retiradas no restringen los rangos.
    sign = Fraction(-1 if problem.sense == "max" else 1)
    _interval([(sign * reduced[j], Fraction(0)) for j in nonbasic])
    objective_ranges = {}
    for j, name in enumerate(problem.variable_names):
        position = reduced_basis.index(j) if j in reduced_basis else None
        conditions = []
        for column in nonbasic:
            slope = (
                -transformed[position][column] if position is not None else Fraction(column == j)
            )
            conditions.append((sign * reduced[column], sign * slope))
        objective_ranges[name] = _translate(_interval(conditions), problem.objective[j])
    rhs_ranges = {}
    for position, i in enumerate(kept_rows):
        conditions = [(value, signs[i] * inverse[k][position]) for k, value in enumerate(values)]
        # Una artificial nula debe seguir exactamente en cero, no solo ≥ 0.
        # Esto preserva las igualdades omitidas al perturbar otra fila original.
        if any(full_inverse[k][i] != 0 for k in artificial_positions):
            conditions.extend([(Fraction(0), Fraction(1)), (Fraction(0), Fraction(-1))])
        row = problem.constraints[i]
        rhs_ranges[row.name] = _translate(_interval(conditions), row.rhs)
    warnings = [
        f"{problem.constraints[i].name}: precio sombra no único: fila redundante. "
        "Se adopta y = 0 y no se informa rango para su lado derecho."
        for i in sorted(removed_rows)
    ]
    if solution.degenerate or any(value == 0 for value in full_values):
        warnings.append(
            "Degeneración: los precios sombra pueden no ser únicos y un extremo "
            "del rango puede coincidir con el valor actual."
        )
    report = SensitivityReport(
        shadow_prices=prices,
        reduced_costs={name: reduced[j] for j, name in enumerate(problem.variable_names)},
        objective_ranges=objective_ranges,
        rhs_ranges=rhs_ranges,
        interpretations={},
        warnings=tuple(warnings),
    )
    return replace(report, interpretations=sensitivity_interpretations(problem, report))
