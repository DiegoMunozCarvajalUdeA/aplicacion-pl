"""Gran M con tablero exacto y evidencia anterior a cada pivote."""

from dataclasses import replace

from plapp import simplex_rules as rules
from plapp.model import LPProblem
from plapp.mvalue import MValue
from plapp.result import Iteration, Matrix, Pivot, Solution, Status
from plapp.standard_form import to_standard_form

MAX_ITERATIONS = 1000


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
        reduced_costs=rules.reduced_costs(tableau, basis, costs),
        objective_value=objective,
    )


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
        state_notes = list(rules.initial_notes(sign)) if not iterations else []
        bland, note = rules.bland_rule(basis, seen, bland)
        if note:
            state_notes.append(note)
            notes.append(note)
        seen.add(basis)
        state = replace(state, notes=tuple(state_notes))
        basic_values = tuple(row[-1] for row in tableau)
        message = rules.infeasibility_message(
            state.reduced_costs, basic_values, basis, standard, sign
        )
        if message:
            iterations.append(replace(state, entering_reason=message))
            return Solution(
                "big_m",
                Status.INFEASIBLE,
                message,
                standard_form=standard,
                iterations=tuple(iterations),
                notes=tuple(dict.fromkeys(notes)),
            )
        entering, entering_reason = rules.choose_entering(
            state.reduced_costs, basis, standard.column_types, sign, bland
        )
        if entering is None:
            final_step = rules.optimality_step(
                state, standard, problem.sense, tuple(row[:-1] for row in tableau), basic_values
            )
            iterations.append(final_step)
            notes.extend(note for note in final_step.notes if note not in state.notes)
            if final_step.pivot is not None:
                pivot = final_step.pivot
                tableau, basis = rules.pivot_tableau(tableau, basis, pivot.row, pivot.column)
                continue
            return rules.optimal_solution(
                problem, standard, tableau, basis, iterations, degenerate, notes
            )
        direction = tuple(row[entering] for row in tableau)
        ratios = rules.ratio_rows(direction, basic_values, basis, standard.column_names)
        leaving, leaving_reason, tied = rules.choose_leaving(ratios, basis)
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
            return rules.unbounded_solution(
                problem,
                standard,
                state,
                basic_values,
                direction,
                entering,
                iterations,
                notes,
                "big_m",
            )
        iterations.append(
            replace(
                state,
                leaving_variable=standard.column_names[basis[leaving]],
                pivot=Pivot(leaving, entering, tableau[leaving][entering]),
            )
        )
        tableau, basis = rules.pivot_tableau(tableau, basis, leaving, entering)
    raise ValueError(
        f"Se alcanzó el límite de {MAX_ITERATIONS} iteraciones de Gran M; "
        "revise el problema antes de continuar."
    )
