"""Simplex revisado exacto: mantener B⁻¹ y calcular solo la columna necesaria."""

from dataclasses import replace
from fractions import Fraction

from plapp import simplex_rules as rules
from plapp.linalg import column, identity, matmul, matvec
from plapp.model import LPProblem
from plapp.mvalue import MValue
from plapp.result import Iteration, Matrix, Pivot, Solution, StandardForm, Status
from plapp.standard_form import to_standard_form

MAX_ITERATIONS = 1000


def update_inverse(inverse: Matrix, direction: tuple[Fraction, ...], row: int) -> Matrix:
    """Aplicar E·B⁻¹ en O(m²), sin invertir otra vez la nueva base.

    E es identidad excepto en su columna row: E[row,row]=1/d[row] y
    E[i,row]=−d[i]/d[row] para i distinto de row. El producto equivale a
    normalizar esa fila de B⁻¹ y restar d[i] veces la fila normalizada.
    Admite el pivote negativo usado para retirar artificiales nulas.
    """
    pivot = direction[row]
    if pivot == 0:
        raise ValueError("No se puede actualizar B⁻¹ con un pivote cero.")
    normalized = tuple(value / pivot for value in inverse[row])
    return tuple(
        normalized
        if i == row
        else tuple(
            value - direction[i] * factor for value, factor in zip(values, normalized, strict=True)
        )
        for i, values in enumerate(inverse)
    )


def _snapshot(
    standard: StandardForm, basis: tuple[int, ...], inverse: Matrix, number: int
) -> Iteration:
    """Calcular x_B, y simbólico y r sin construir B⁻¹A completo."""
    basic_values = matvec(inverse, standard.b)
    multipliers = tuple(
        sum((standard.c[j] * inverse[k][i] for k, j in enumerate(basis)), MValue())
        for i in range(len(basis))
    )
    reduced = tuple(
        cost - sum((y * row[j] for y, row in zip(multipliers, standard.a, strict=True)), MValue())
        for j, cost in enumerate(standard.c)
    )
    objective = sum(
        (standard.c[j] * value for j, value in zip(basis, basic_values, strict=True)), MValue()
    )
    return Iteration(
        number=number,
        basis=basis,
        b_inverse=inverse,
        basic_values=basic_values,
        multipliers=multipliers,
        reduced_costs=reduced,
        objective_value=objective,
    )


def solve_revised(problem: LPProblem) -> Solution:
    """Resolver con las reglas compartidas y actualización elemental de B⁻¹.

    La base inicial es identidad por construcción de la forma estándar.
    Cada estado calcula x_B=B⁻¹b, y=c_B B⁻¹, r=c−yA y d=B⁻¹a_j.
    Solo al retirar artificiales o buscar alternativas se obtienen las filas
    transformadas completas; no se mantienen ni se guardan como tablero.
    """
    standard = to_standard_form(problem)
    basis = standard.basis
    inverse = identity(len(basis))
    iterations, notes = [], []
    seen = set()
    bland = degenerate = False
    sign = 1 if problem.sense == "max" else -1
    for _ in range(MAX_ITERATIONS):
        state = _snapshot(standard, basis, inverse, len(iterations))
        state_notes = list(rules.initial_notes(sign)) if not iterations else []
        bland, note = rules.bland_rule(basis, seen, bland)
        if note:
            state_notes.append(note)
            notes.append(note)
        seen.add(basis)
        state = replace(state, notes=tuple(state_notes))
        message = rules.infeasibility_message(
            state.reduced_costs, state.basic_values, basis, standard, sign
        )
        if message:
            return Solution(
                "revised",
                Status.INFEASIBLE,
                message,
                standard_form=standard,
                iterations=(*iterations, replace(state, entering_reason=message)),
                notes=tuple(dict.fromkeys(notes)),
            )
        entering, entering_reason = rules.choose_entering(
            state.reduced_costs, basis, standard.column_types, sign, bland
        )
        if entering is None:
            coefficients = matmul(inverse, standard.a)
            final_step = rules.optimality_step(
                state, standard, problem.sense, coefficients, state.basic_values
            )
            iterations.append(final_step)
            notes.extend(note for note in final_step.notes if note not in state.notes)
            if final_step.pivot is not None:
                pivot = final_step.pivot
                direction = column(coefficients, pivot.column)
                inverse = update_inverse(inverse, direction, pivot.row)
                basis = tuple(pivot.column if i == pivot.row else j for i, j in enumerate(basis))
                continue
            rows = tuple(
                row + (value,) for row, value in zip(coefficients, state.basic_values, strict=True)
            )
            return rules.optimal_solution(
                problem, standard, rows, basis, iterations, degenerate, notes, "revised", inverse
            )
        direction = matvec(inverse, column(standard.a, entering))
        ratios = rules.ratio_rows(direction, state.basic_values, basis, standard.column_names)
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
                state.basic_values,
                direction,
                entering,
                iterations,
                notes,
                "revised",
            )
        iterations.append(
            replace(
                state,
                leaving_variable=standard.column_names[basis[leaving]],
                pivot=Pivot(leaving, entering, direction[leaving]),
            )
        )
        inverse = update_inverse(inverse, direction, leaving)
        basis = tuple(entering if i == leaving else j for i, j in enumerate(basis))
    raise ValueError(
        f"Se alcanzó el límite de {MAX_ITERATIONS} iteraciones del simplex revisado; "
        "revise el problema antes de continuar."
    )
