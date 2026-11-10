"""Oráculo externo: SciPy solo verifica resultados, nunca alimenta la interfaz.

linprog minimiza: en Max se niega c. Una fila >= se transforma con −1.
Precio sombra original = signo_objetivo * signo_fila * marginal_de_highs.
Representa ∂Z*/∂b_i en el sentido y la restricción originales.
"""

import argparse
import json
from dataclasses import asdict, dataclass
from fractions import Fraction
from pathlib import Path

from scipy.optimize import linprog

from plapp.big_m import solve_big_m
from plapp.io_json import load_problem
from plapp.model import LPProblem
from plapp.result import Solution, Status
from plapp.revised_simplex import solve_revised


@dataclass(frozen=True)
class OracleResult:
    """Resultados aproximados de HiGHS expresados en el modelo original."""

    status: str
    values: dict[str, float]
    objective_value: float | None
    slacks: dict[str, float]
    shadow_prices: dict[str, float]
    reduced_costs: dict[str, float]


def scipy_inputs(problem: LPProblem) -> dict:
    """Transformar signos conservando el orden relativo de cada clase de fila."""
    a_ub, b_ub, a_eq, b_eq = [], [], [], []
    sign = -1 if problem.sense == "max" else 1
    for row in problem.constraints:
        if row.relation == "=":
            a_eq.append([float(value) for value in row.coefficients])
            b_eq.append(float(row.rhs))
        else:
            multiplier = -1 if row.relation == ">=" else 1
            a_ub.append([multiplier * float(value) for value in row.coefficients])
            b_ub.append(multiplier * float(row.rhs))
    return {
        "c": [sign * float(value) for value in problem.objective],
        "A_ub": a_ub or None,
        "b_ub": b_ub or None,
        "A_eq": a_eq or None,
        "b_eq": b_eq or None,
        "bounds": (0, None),
    }


def verify_with_scipy(problem: LPProblem) -> OracleResult:
    """Resolver para verificar; rechazar resultados numéricos no concluyentes."""
    inputs = scipy_inputs(problem)
    result = linprog(**inputs, method="highs")
    if result.status in (3, 4):
        # Sin presolve se distingue infactibilidad de no acotación ambigua.
        result = linprog(**inputs, method="highs", options={"presolve": False})
    statuses = {0: "optimo", 2: "infactible", 3: "no_acotado"}
    if result.status not in statuses:
        raise ValueError(f"SciPy no obtuvo un resultado verificable (estado {result.status}).")
    status = statuses[result.status]
    if status != "optimo":
        return OracleResult(status, {}, None, {}, {}, {})
    sign = -1 if problem.sense == "max" else 1
    values = dict(zip(problem.variable_names, map(float, result.x), strict=True))
    slacks, prices = {}, {}
    inequality_index = equality_index = 0
    for row in problem.constraints:
        activity = sum(float(a) * x for a, x in zip(row.coefficients, result.x, strict=True))
        multiplier = -1 if row.relation == ">=" else 1
        slacks[row.name] = multiplier * (float(row.rhs) - activity)
        if row.relation == "=":
            marginal = result.eqlin.marginals[equality_index]
            equality_index += 1
        else:
            marginal = result.ineqlin.marginals[inequality_index]
            inequality_index += 1
        prices[row.name] = float(sign * multiplier * marginal)
    reduced = dict(
        zip(
            problem.variable_names,
            map(lambda value: float(sign * value), result.lower.marginals),
            strict=True,
        )
    )
    return OracleResult(status, values, float(sign * result.fun), slacks, prices, reduced)


def compare_solution(problem: LPProblem, own: Solution, oracle: OracleResult) -> list[str]:
    """Comparar estado y Z; aceptar cualquier punto óptimo factible."""
    differences = []
    if own.status.value != oracle.status:
        differences.append(f"estado propio {own.status.value}; SciPy {oracle.status}")
        return differences
    if own.status != Status.OPTIMAL:
        return differences
    if own.objective_value is None or oracle.objective_value is None:
        return ["falta el valor de Z en una solución óptima"]
    if abs(float(own.objective_value) - oracle.objective_value) > 1e-7:
        differences.append(f"Z propio {own.objective_value}; SciPy {oracle.objective_value}")
    if set(own.values) != set(problem.variable_names):
        return differences + ["las variables devueltas no coinciden con el modelo"]
    x = [own.values[name] for name in problem.variable_names]
    if any(value < 0 for value in x):
        differences.append("hay variables negativas")
    for row in problem.constraints:
        activity = sum(a * value for a, value in zip(row.coefficients, x, strict=True))
        if (
            (row.relation == "<=" and activity > row.rhs)
            or (row.relation == ">=" and activity < row.rhs)
            or (row.relation == "=" and activity != row.rhs)
        ):
            differences.append(f"el punto propio viola {row.name}")
    z = sum(c * value for c, value in zip(problem.objective, x, strict=True))
    if z != own.objective_value:
        differences.append("Z propio no coincide con c·x")
    return differences


def _display(value: float) -> str:
    """Reconstruir una fracción legible de una aproximación, solo para el informe."""
    return str(Fraction(value).limit_denominator(1_000_000_000))


def main() -> int:
    """Imprimir la verificación de un archivo y comparar los métodos disponibles."""
    parser = argparse.ArgumentParser(
        description="Verificar un problema con SciPy (oráculo externo)."
    )
    parser.add_argument("file", type=Path, help="Ruta del archivo JSON")
    parser.add_argument(
        "--json", action="store_true", help="Emitir solo el resultado de SciPy en JSON"
    )
    args = parser.parse_args()
    try:
        problem = load_problem(args.file)
        oracle = verify_with_scipy(problem)
    except ValueError as error:
        print(f"Error de verificación: {error}")
        return 1
    if args.json:
        print(json.dumps(asdict(oracle), ensure_ascii=False, indent=2))
        return 0
    messages = {"infactible": "no tiene solución factible", "no_acotado": "solución no acotada"}
    print(f"Estado: {oracle.status}")
    if oracle.status != "optimo":
        print(messages[oracle.status])
    else:
        for name, value in oracle.values.items():
            print(f"{name} = {_display(value)}")
        print(f"Z = {_display(oracle.objective_value)}")
        for name, value in oracle.slacks.items():
            print(f"Holgura/exceso {name} = {_display(value)}")
        for name, value in oracle.shadow_prices.items():
            print(f"Precio sombra {name} = {_display(value)}")
        print(
            "Precios sombra: ∂Z*/∂b original; cifras reconstruidas desde aproximaciones de SciPy."
        )
    failed = False
    for label, solver in (("Gran M", solve_big_m), ("Simplex revisado", solve_revised)):
        try:
            differences = compare_solution(problem, solver(problem), oracle)
        except NotImplementedError:
            print(f"{label}: pendiente de implementar")
            continue
        except Exception:
            print(f"{label}: error inesperado; revise el método propio con las pruebas.")
            failed = True
            continue
        failed |= bool(differences)
        print(f"{label}: " + ("; ".join(differences) if differences else "coincide con SciPy"))
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
