"""Gran M con tablero exacto y evidencia anterior a cada pivote."""

from collections import deque
from dataclasses import replace
from fractions import Fraction

from plapp.linalg import invert
from plapp.model import LPProblem
from plapp.mvalue import MValue
from plapp.result import Iteration, Matrix, Pivot, RatioRow, Solution, StandardForm, Status
from plapp.standard_form import to_standard_form

MAX_ITERATIONS = 1000
MAX_ALTERNATIVE_BASES = 1000


def _reduced_costs(
    tableau: Matrix, basis: tuple[int, ...], costs: tuple[MValue, ...]
) -> tuple[MValue, ...]:
    """Canonizar r = c − c_B·tablero; las columnas básicas quedan en cero."""
    return tuple(
        cost
        - sum((costs[basic] * row[j] for basic, row in zip(basis, tableau, strict=True)), MValue())
        for j, cost in enumerate(costs)
    )


def _snapshot(
    tableau: Matrix, basis: tuple[int, ...], costs: tuple[MValue, ...], number: int
) -> Iteration:
    """Guardar una copia inmutable del estado antes de decidir el siguiente paso."""
    objective = sum(
        (costs[basic] * row[-1] for basic, row in zip(basis, tableau, strict=True)), MValue()
    )
    return Iteration(
        number=number,
        basis=basis,
        tableau=tableau,
        reduced_costs=_reduced_costs(tableau, basis, costs),
        objective_value=objective,
    )


def _pivot(
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


def _ratios(
    tableau: Matrix, basis: tuple[int, ...], entering: int, names: tuple[str, ...]
) -> tuple[RatioRow, ...]:
    """Excluir coeficientes no positivos: no limitan el aumento de la entrante."""
    result = []
    for i, (row, basic) in enumerate(zip(tableau, basis, strict=True)):
        coefficient, rhs = row[entering], row[-1]
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


def _choose_leaving(
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


def _values(problem: LPProblem, tableau: Matrix, basis: tuple[int, ...]) -> dict[str, Fraction]:
    """Recuperar solo las variables originales; las no básicas valen cero."""
    basic_values = {basic: row[-1] for basic, row in zip(basis, tableau, strict=True)}
    return {name: basic_values.get(j, Fraction(0)) for j, name in enumerate(problem.variable_names)}


def _direction(
    problem: LPProblem, tableau: Matrix, basis: tuple[int, ...], entering: int
) -> dict[str, Fraction]:
    """Proyectar d_entrante = 1, d_B = −columna a las variables originales."""
    direction = {j: -row[entering] for j, row in zip(basis, tableau, strict=True)}
    direction[entering] = Fraction(1)
    return {name: direction.get(j, Fraction(0)) for j, name in enumerate(problem.variable_names)}


def _alternatives(
    problem: LPProblem, standard: StandardForm, tableau: Matrix, basis: tuple[int, ...]
) -> tuple[tuple[dict[str, Fraction], ...], tuple[dict[str, Fraction], ...]]:
    """Buscar un punto distinto o rayo óptimo, recorriendo también pivotes degenerados.

    Un costo reducido cero no basta: puede conducir solo al mismo punto. Se
    exploran las bases vecinas con paso cero antes de descartar multiplicidad.
    Basta un segundo punto para certificar un segmento, o una dirección para
    certificar un rayo. El límite explícito evita una búsqueda combinatoria muda.
    """
    initial = _values(problem, tableau, basis)
    pending = deque([(tableau, basis)])
    # El orden de filas no crea otra base: contar conjuntos evita explorar
    # permutaciones del mismo sistema en vértices muy degenerados.
    seen = {frozenset(basis)}
    while pending:
        rows, current_basis = pending.popleft()
        reduced = _reduced_costs(rows, current_basis, standard.c)
        for j, cost in enumerate(reduced):
            if j in current_basis or standard.column_types[j] == "artificial" or cost != 0:
                continue
            ratios = _ratios(rows, current_basis, j, standard.column_names)
            eligible = [row for row in ratios if row.ratio is not None]
            if not eligible:
                ray = _direction(problem, rows, current_basis, j)
                if any(ray.values()):
                    point = {name: initial[name] + ray[name] for name in initial}
                    return (point,), (ray,)
                continue
            minimum = min(row.ratio for row in eligible)
            for ratio in eligible:
                if ratio.ratio != minimum:
                    continue
                new_rows, new_basis = _pivot(rows, current_basis, ratio.row, j)
                point = _values(problem, new_rows, new_basis)
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


def _optimal_solution(
    problem: LPProblem,
    standard: StandardForm,
    tableau: Matrix,
    basis: tuple[int, ...],
    iterations: list[Iteration],
    degenerate: bool,
    notes: list[str],
) -> Solution:
    """Comprobar Z original, holguras e inversa de la base de la forma estándar."""
    values = _values(problem, tableau, basis)
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
    alternatives, rays = _alternatives(problem, standard, tableau, basis)
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
        method="big_m",
        status=Status.OPTIMAL,
        message=message,
        values=values,
        objective_value=objective,
        slacks=slacks,
        standard_form=standard,
        iterations=tuple(iterations),
        final_basis=basis,
        final_b_inverse=invert(tuple(tuple(row[j] for j in basis) for row in standard.a)),
        multiple_optima=bool(alternatives or rays),
        degenerate=degenerate or bool(zero_basics),
        alternative_solutions=alternatives,
        notes=tuple(dict.fromkeys(notes)),
        alternative_rays=rays,
    )


def _cleanup_pivot(
    tableau: Matrix, basis: tuple[int, ...], standard: StandardForm
) -> tuple[int, int] | None:
    """Una artificial nula puede salir incluso con pivote negativo: el paso es cero."""
    for i, basic in enumerate(basis):
        if standard.column_types[basic] == "artificial" and tableau[i][-1] == 0:
            for j, kind in enumerate(standard.column_types):
                if kind != "artificial" and j not in basis and tableau[i][j] != 0:
                    return i, j
    return None


def _optimality_step(state: Iteration, standard: StandardForm, sense: str) -> Iteration:
    """Preparar el retiro de una artificial nula o certificar la terminación."""
    tableau, basis = state.tableau, state.basis
    cleanup = _cleanup_pivot(tableau, basis, standard)
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
            pivot=Pivot(i, entering, tableau[i][entering]),
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
    reason = (
        "Todos los cⱼ − zⱼ ≤ 0 en Max: la solución actual es óptima."
        if sense == "max"
        else "Todos los cⱼ − zⱼ ≥ 0 en Min: la solución actual es óptima."
    )
    return replace(state, entering_reason=reason, notes=tuple(dict.fromkeys(notes)))


def solve_big_m(problem: LPProblem) -> Solution:
    """Resolver con M simbólica conservando la evidencia de cada pivote.

    1. Canonizar r = c − c_B·tablero y Z = c_B·b en cada estado.
    2. Sin mejora en la parte M, una artificial positiva prueba infactibilidad.
    3. Elegir el mejor costo favorable; si se repite base, usar Bland hasta terminar.
    4. Aplicar razón mínima con desempate por índice de la básica y pivotear.
    5. Sin saliente, informar no acotación; sin mejora, retirar artificiales nulas.
    6. Confirmar óptimos alternos, degeneración, Z original e inversa de B final.
    """
    standard = to_standard_form(problem)
    tableau = tuple(row + (rhs,) for row, rhs in zip(standard.a, standard.b, strict=True))
    basis = standard.basis
    iterations, notes = [], []
    seen = set()
    bland = degenerate = False
    sign = 1 if problem.sense == "max" else -1
    for _ in range(MAX_ITERATIONS):
        state = _snapshot(tableau, basis, standard.c, len(iterations))
        state_notes = []
        if not iterations:
            operation = "sumó" if sign == 1 else "restó"
            state_notes.append(
                f"Canonización de la fila Z: se {operation} M veces cada fila con "
                "artificial básica a la fila de costos reducidos cⱼ − zⱼ. "
                "Las básicas tienen costo reducido cero; Z incluye su penalización."
            )
            state_notes.append(
                "Una artificial que sale de la base nunca vuelve a entrar: se descarta "
                "como candidata, igual que al retirar su columna al finalizar la fase I."
            )
        if basis in seen and not bland:
            bland = True
            note = (
                "Se repitió una base: se activa la regla de Bland "
                "hasta terminar para evitar ciclos."
            )
            state_notes.append(note)
            notes.append(note)
        seen.add(basis)
        state = replace(state, notes=tuple(state_notes))
        reduced = state.reduced_costs
        nonbasic = [
            j
            for j in range(len(reduced))
            if j not in basis and standard.column_types[j] != "artificial"
        ]
        m_improvement = any(sign * reduced[j].b > 0 for j in nonbasic)
        positive_artificials = [
            standard.column_names[j]
            for j, row in zip(basis, tableau, strict=True)
            if standard.column_types[j] == "artificial" and row[-1] > 0
        ]
        if not m_improvement and positive_artificials:
            message = (
                "El problema no tiene solución factible: no hay mejora en la parte M "
                "y siguen positivas las artificiales " + ", ".join(positive_artificials) + "."
            )
            iterations.append(replace(state, entering_reason=message))
            return Solution(
                "big_m",
                Status.INFEASIBLE,
                message,
                standard_form=standard,
                iterations=tuple(iterations),
                notes=tuple(dict.fromkeys(notes)),
            )
        eligible = [j for j in nonbasic if sign * reduced[j] > 0]
        if not eligible:
            final_step = _optimality_step(state, standard, problem.sense)
            iterations.append(final_step)
            notes.extend(note for note in final_step.notes if note not in state.notes)
            if final_step.pivot is not None:
                pivot = final_step.pivot
                tableau, basis = _pivot(tableau, basis, pivot.row, pivot.column)
                continue
            return _optimal_solution(
                problem, standard, tableau, basis, iterations, degenerate, notes
            )
        if bland:
            entering = min(eligible)
            entering_reason = "Regla de Bland: menor índice entre los costos reducidos favorables."
        else:
            entering = min(eligible, key=lambda j: (-sign * reduced[j], j))
            entering_reason = (
                "Mayor costo reducido positivo en Max; en empate, menor índice."
                if sign == 1
                else "Menor costo reducido negativo en Min; en empate, menor índice."
            )
        ratios = _ratios(tableau, basis, entering, standard.column_names)
        leaving, leaving_reason, tied = _choose_leaving(ratios, basis)
        degenerate |= tied
        if tied:
            notes.append(
                "Degeneración: hubo empate en la razón mínima; se aplicó Bland para la salida."
            )
        state = replace(
            state,
            entering_variable=standard.column_names[entering],
            entering_reason=entering_reason,
            ratios=ratios,
            leaving_reason=leaving_reason,
        )
        if leaving is None:
            origin = _values(problem, tableau, basis)
            direction = _direction(problem, tableau, basis, entering)
            coordinates = ", ".join(problem.variable_names)
            point = ", ".join(map(str, origin.values()))
            ray = ", ".join(map(str, direction.values()))
            change = "crece" if sign == 1 else "decrece"
            message = (
                "El problema tiene solución no acotada: "
                + standard.column_names[entering]
                + " puede crecer sin límite y mejorar Z; "
                "su columna no tiene coeficientes positivos. "
                f"Z {change} sin límite a lo largo de "
                f"({coordinates}) = ({point}) + t·({ray}), t ≥ 0."
            )
            iterations.append(replace(state, leaving_reason=message))
            return Solution(
                "big_m",
                Status.UNBOUNDED,
                message,
                standard_form=standard,
                iterations=tuple(iterations),
                notes=tuple(dict.fromkeys(notes)),
                unbounded_origin=origin,
                unbounded_direction=direction,
            )
        iterations.append(
            replace(
                state,
                leaving_variable=standard.column_names[basis[leaving]],
                pivot=Pivot(leaving, entering, tableau[leaving][entering]),
            )
        )
        tableau, basis = _pivot(tableau, basis, leaving, entering)
    raise ValueError(
        f"Se alcanzó el límite de {MAX_ITERATIONS} iteraciones de Gran M; "
        "revise el problema antes de continuar."
    )
