"""Decisiones simplex y posproceso compartidos, independientes del almacenamiento."""

from collections import deque
from dataclasses import replace
from fractions import Fraction

from plapp.linalg import invert
from plapp.model import LPProblem
from plapp.mvalue import MValue
from plapp.result import Iteration, Matrix, Method, Pivot, RatioRow, Solution, StandardForm, Status

MAX_ALTERNATIVE_BASES = 1000


def initial_notes(sign: int) -> tuple[str, ...]:
    """Explicar la penalización inicial y por qué las artificiales no reentran."""
    operation = "sumó" if sign == 1 else "restó"
    return (
        f"Canonización de la fila Z: se {operation} M veces cada fila con "
        "artificial básica a la fila de costos reducidos cⱼ − zⱼ. "
        "Las básicas tienen costo reducido cero; Z incluye su penalización.",
        "Una artificial que sale de la base nunca vuelve a entrar: se descarta "
        "como candidata, igual que al retirar su columna al finalizar la fase I.",
    )


def bland_rule(basis: tuple[int, ...], seen: set[tuple[int, ...]], bland: bool) -> tuple[bool, str]:
    """Activar Bland permanentemente al repetirse una base, sin modificar el historial."""
    if basis in seen and not bland:
        return True, (
            "Se repitió una base: se activa la regla de Bland hasta terminar para evitar ciclos."
        )
    return bland, ""


def candidate_columns(basis: tuple[int, ...], column_types: tuple[str, ...]) -> list[int]:
    """Excluir básicas y artificiales para que una artificial retirada no reentre."""
    return [j for j, kind in enumerate(column_types) if j not in basis and kind != "artificial"]


def infeasibility_message(
    reduced: tuple[MValue, ...],
    basic_values: tuple[Fraction, ...],
    basis: tuple[int, ...],
    standard: StandardForm,
    sign: int,
) -> str:
    """Una artificial positiva sin mejora simbólica certifica fase I infactible."""
    nonbasic = candidate_columns(basis, standard.column_types)
    m_improvement = any(sign * reduced[j].b > 0 for j in nonbasic)
    positive_artificials = [
        standard.column_names[j]
        for j, value in zip(basis, basic_values, strict=True)
        if standard.column_types[j] == "artificial" and value > 0
    ]
    if not m_improvement and positive_artificials:
        return (
            "El problema no tiene solución factible: no hay mejora en la parte M "
            "y siguen positivas las artificiales " + ", ".join(positive_artificials) + "."
        )
    return ""


def choose_entering(
    reduced: tuple[MValue, ...],
    basis: tuple[int, ...],
    column_types: tuple[str, ...],
    sign: int,
    bland: bool,
) -> tuple[int | None, str]:
    """Elegir mejor costo simbólico, o menor índice favorable cuando rige Bland."""
    eligible = [j for j in candidate_columns(basis, column_types) if sign * reduced[j] > 0]
    if not eligible:
        return None, ""
    if bland:
        return min(eligible), "Regla de Bland: menor índice entre los costos reducidos favorables."
    entering = min(eligible, key=lambda j: (-sign * reduced[j], j))
    reason = (
        "Mayor costo reducido positivo en Max; en empate, menor índice."
        if sign == 1
        else "Menor costo reducido negativo en Min; en empate, menor índice."
    )
    return entering, reason


def unbounded_solution(
    problem: LPProblem,
    standard: StandardForm,
    state: Iteration,
    basic_values: tuple[Fraction, ...],
    direction_column: tuple[Fraction, ...],
    entering: int,
    iterations: list[Iteration],
    notes: list[str],
    method: Method,
) -> Solution:
    """Certificar un rayo factible y conservar un solo estado terminal con razones."""
    origin = original_values(problem, basic_values, state.basis)
    direction = original_direction(problem, direction_column, state.basis, entering)
    coordinates = ", ".join(problem.variable_names)
    point = ", ".join(map(str, origin.values()))
    ray = ", ".join(map(str, direction.values()))
    change = "crece" if problem.sense == "max" else "decrece"
    message = (
        "El problema tiene solución no acotada: "
        + standard.column_names[entering]
        + " puede crecer sin límite y mejorar Z; "
        "su columna no tiene coeficientes positivos. "
        f"Z {change} sin límite a lo largo de "
        f"({coordinates}) = ({point}) + t·({ray}), t ≥ 0."
    )
    return Solution(
        method,
        Status.UNBOUNDED,
        message,
        standard_form=standard,
        iterations=(*iterations, replace(state, leaving_reason=message)),
        notes=tuple(dict.fromkeys(notes)),
        unbounded_origin=origin,
        unbounded_direction=direction,
    )


def reduced_costs(
    tableau: Matrix, basis: tuple[int, ...], costs: tuple[MValue, ...]
) -> tuple[MValue, ...]:
    """Canonizar r = c − c_B·tablero; las columnas básicas quedan en cero."""
    return tuple(
        cost
        - sum((costs[basic] * row[j] for basic, row in zip(basis, tableau, strict=True)), MValue())
        for j, cost in enumerate(costs)
    )


def pivot_tableau(
    tableau: Matrix, basis: tuple[int, ...], row_index: int, entering: int
) -> tuple[Matrix, tuple[int, ...]]:
    """Reducir la columna entrante a identidad mediante operaciones de fila."""
    pivot = tableau[row_index][entering]
    normalized = tuple(value / pivot for value in tableau[row_index])
    rows = []
    for i, row in enumerate(tableau):
        rows.append(
            normalized
            if i == row_index
            else tuple(
                value - row[entering] * pivot_value
                for value, pivot_value in zip(row, normalized, strict=True)
            )
        )
    new_basis = tuple(entering if i == row_index else basic for i, basic in enumerate(basis))
    return tuple(rows), new_basis


def ratio_rows(
    direction: tuple[Fraction, ...],
    basic_values: tuple[Fraction, ...],
    basis: tuple[int, ...],
    names: tuple[str, ...],
) -> tuple[RatioRow, ...]:
    """Excluir coeficientes no positivos: no limitan el aumento de la entrante."""
    result = []
    for i, (coefficient, rhs, basic) in enumerate(zip(direction, basic_values, basis, strict=True)):
        exclusion = ""
        if coefficient == 0:
            exclusion = "Excluida: coeficiente cero; la básica no disminuye."
        elif coefficient < 0:
            exclusion = "Excluida: coeficiente negativo; la básica aumenta."
        result.append(
            RatioRow(
                i,
                names[basic],
                rhs,
                coefficient,
                rhs / coefficient if coefficient > 0 else None,
                exclusion,
            )
        )
    return tuple(result)


def choose_leaving(
    ratios: tuple[RatioRow, ...], basis: tuple[int, ...]
) -> tuple[int | None, str, bool]:
    """En empate de razón mínima sale la básica de menor índice, según Bland."""
    eligible = [row for row in ratios if row.ratio is not None]
    if not eligible:
        return None, "Ningún coeficiente es positivo; no hay variable saliente.", False
    minimum = min(row.ratio for row in eligible)
    tied = [row.row for row in eligible if row.ratio == minimum]
    leaving = min(tied, key=lambda i: basis[i])
    reason = "Menor razón no negativa entre filas con coeficiente positivo."
    if len(tied) > 1:
        reason += " Empate: sale la básica de menor índice (Bland); se detectó degeneración."
    return leaving, reason, len(tied) > 1


def original_values(
    problem: LPProblem, values: tuple[Fraction, ...], basis: tuple[int, ...]
) -> dict[str, Fraction]:
    """Recuperar solo las variables originales; las no básicas valen cero."""
    basic_values = dict(zip(basis, values, strict=True))
    return {name: basic_values.get(j, Fraction(0)) for j, name in enumerate(problem.variable_names)}


def original_direction(
    problem: LPProblem, column: tuple[Fraction, ...], basis: tuple[int, ...], entering: int
) -> dict[str, Fraction]:
    """Proyectar d_entrante = 1, d_B = −columna a las variables originales."""
    direction = {j: -value for j, value in zip(basis, column, strict=True)}
    direction[entering] = Fraction(1)
    return {name: direction.get(j, Fraction(0)) for j, name in enumerate(problem.variable_names)}


def find_alternatives(
    problem: LPProblem, standard: StandardForm, tableau: Matrix, basis: tuple[int, ...]
) -> tuple[tuple[dict[str, Fraction], ...], tuple[dict[str, Fraction], ...]]:
    """Buscar un punto distinto o rayo óptimo, recorriendo también pivotes degenerados.

    Un costo reducido cero no basta: puede conducir solo al mismo punto. Se
    exploran las bases vecinas con paso cero antes de descartar multiplicidad.
    Basta un segundo punto para certificar un segmento, o una dirección para
    certificar un rayo. El límite explícito evita una búsqueda combinatoria muda.
    """
    initial = original_values(problem, tuple(row[-1] for row in tableau), basis)
    pending = deque([(tableau, basis)])
    # El orden de filas no crea otra base: contar conjuntos evita explorar
    # permutaciones del mismo sistema en vértices muy degenerados.
    seen = {frozenset(basis)}
    while pending:
        rows, current_basis = pending.popleft()
        reduced = reduced_costs(rows, current_basis, standard.c)
        for j, cost in enumerate(reduced):
            if j in current_basis or standard.column_types[j] == "artificial" or cost != 0:
                continue
            ratios = ratio_rows(
                tuple(row[j] for row in rows),
                tuple(row[-1] for row in rows),
                current_basis,
                standard.column_names,
            )
            eligible = [row for row in ratios if row.ratio is not None]
            if not eligible:
                ray = original_direction(problem, tuple(row[j] for row in rows), current_basis, j)
                if any(ray.values()):
                    point = {name: initial[name] + ray[name] for name in initial}
                    return (point,), (ray,)
                continue
            minimum = min(row.ratio for row in eligible)
            for ratio in eligible:
                if ratio.ratio != minimum:
                    continue
                new_rows, new_basis = pivot_tableau(rows, current_basis, ratio.row, j)
                point = original_values(problem, tuple(row[-1] for row in new_rows), new_basis)
                if point != initial:
                    return (point,), ()
                basis_key = frozenset(new_basis)
                if basis_key not in seen:
                    if len(seen) >= MAX_ALTERNATIVE_BASES:
                        raise ValueError(
                            "Se alcanzó el límite de bases al buscar óptimos alternos; "
                            "no se pudo concluir la multiplicidad."
                        )
                    seen.add(basis_key)
                    pending.append((new_rows, new_basis))
    return (), ()


def optimal_solution(
    problem: LPProblem,
    standard: StandardForm,
    tableau: Matrix,
    basis: tuple[int, ...],
    iterations: list[Iteration],
    degenerate: bool,
    notes: list[str],
    method: Method = "big_m",
    b_inverse: Matrix | None = None,
) -> Solution:
    """Comprobar Z original, holguras e inversa de la base de la forma estándar."""
    values = original_values(problem, tuple(row[-1] for row in tableau), basis)
    objective = sum(
        (
            cost * values[name]
            for name, cost in zip(problem.variable_names, problem.objective, strict=True)
        ),
        Fraction(0),
    )
    if iterations[-1].objective_value != objective:
        raise ArithmeticError("La fila Z no coincide con la función objetivo original.")
    slacks = {}
    for row in problem.constraints:
        activity = sum(
            (
                a * values[name]
                for a, name in zip(row.coefficients, problem.variable_names, strict=True)
            ),
            Fraction(0),
        )
        slacks[row.name] = (
            Fraction(0)
            if row.relation == "="
            else activity - row.rhs
            if row.relation == ">="
            else row.rhs - activity
        )
    zero_basics = [
        standard.column_names[j] for j, row in zip(basis, tableau, strict=True) if row[-1] == 0
    ]
    if zero_basics:
        notes.append("Degeneración: variables básicas en 0: " + ", ".join(zero_basics) + ".")
    alternatives, rays = find_alternatives(problem, standard, tableau, basis)
    message = "Se encontró una solución óptima."
    if rays:
        direction = ", ".join(str(rays[0][name]) for name in problem.variable_names)
        point = ", ".join(str(values[name]) for name in problem.variable_names)
        message += f" Z = {objective} en todo el rayo desde ({point}), con dirección ({direction})."
    elif alternatives:
        point = ", ".join(str(values[name]) for name in problem.variable_names)
        other = ", ".join(str(alternatives[0][name]) for name in problem.variable_names)
        message += f" Z = {objective} en todo el segmento entre ({point}) y ({other})."
    return Solution(
        method=method,
        status=Status.OPTIMAL,
        message=message,
        values=values,
        objective_value=objective,
        slacks=slacks,
        standard_form=standard,
        iterations=tuple(iterations),
        final_basis=basis,
        final_b_inverse=b_inverse
        if b_inverse is not None
        else invert(tuple(tuple(row[j] for j in basis) for row in standard.a)),
        multiple_optima=bool(alternatives or rays),
        degenerate=degenerate or bool(zero_basics),
        alternative_solutions=alternatives,
        notes=tuple(dict.fromkeys(notes)),
        alternative_rays=rays,
    )


def cleanup_pivot(
    coefficients: Matrix,
    basic_values: tuple[Fraction, ...],
    basis: tuple[int, ...],
    column_types: tuple[str, ...],
) -> tuple[int, int] | None:
    """Una artificial nula puede salir incluso con pivote negativo: el paso es cero."""
    for i, basic in enumerate(basis):
        if column_types[basic] == "artificial" and basic_values[i] == 0:
            for j, kind in enumerate(column_types):
                if kind != "artificial" and j not in basis and coefficients[i][j] != 0:
                    return i, j
    return None


def optimality_step(
    state: Iteration,
    standard: StandardForm,
    sense: str,
    coefficients: Matrix,
    basic_values: tuple[Fraction, ...],
) -> Iteration:
    """Preparar el retiro de una artificial nula o certificar la terminación."""
    basis = state.basis
    cleanup = cleanup_pivot(coefficients, basic_values, basis, standard.column_types)
    if cleanup is not None:
        i, entering = cleanup
        note = (
            "Retiro de artificial básica en 0: pivote sin desplazamiento; no requiere razón mínima."
        )
        return replace(
            state,
            entering_variable=standard.column_names[entering],
            entering_reason=(
                "Columna no artificial con coeficiente no nulo para retirar una artificial en 0."
            ),
            leaving_variable=standard.column_names[basis[i]],
            leaving_reason=note,
            pivot=Pivot(i, entering, coefficients[i][entering]),
            notes=state.notes + (note,),
        )
    notes = list(state.notes)
    for i, basic in enumerate(basis):
        if standard.column_types[basic] == "artificial":
            notes.append(
                f"Fila transformada {i + 1} redundante: {standard.column_names[basic]} "
                "queda básica en 0 porque no hay columna no artificial para retirarla. "
                "Se conserva para mantener B cuadrada; "
                "sensibilidad requiere tratar la redundancia."
            )
    condition = "≤ 0 en Max" if sense == "max" else "≥ 0 en Min"
    reason = (
        f"Los cⱼ − zⱼ de columnas no artificiales cumplen {condition}: "
        "la solución actual es óptima."
    )
    return replace(state, entering_reason=reason, notes=tuple(dict.fromkeys(notes)))
