"""Comparación reproducible con redundancia y lados derechos frecuentemente nulos."""

import argparse
import json
import random
from dataclasses import replace
from fractions import Fraction

from plapp.big_m import solve_big_m
from plapp.model import Constraint, LPProblem
from plapp.result import Method
from plapp.revised_simplex import solve_revised

if __package__:
    from scripts.verify import OracleInconclusiveError, compare_solution, verify_with_scipy
else:
    from verify import OracleInconclusiveError, compare_solution, verify_with_scipy


def random_problem(rng: random.Random) -> LPProblem:
    """Generar filas independientes o copias escaladas, conservando su sentido."""
    n = rng.randint(2, 4)
    rows = []
    for _ in range(rng.randint(1, 6)):
        if rows and rng.random() < 0.35:
            previous = rng.choice(rows)
            scale = rng.choice((1, 2, -1))
            relation = previous.relation
            if scale < 0:
                relation = {"<=": ">=", ">=": "<=", "=": "="}[relation]
            rows.append(
                replace(
                    previous,
                    coefficients=tuple(scale * a for a in previous.coefficients),
                    rhs=scale * previous.rhs,
                    relation=relation,
                )
            )
        else:
            coefficients = tuple(Fraction(rng.randint(-5, 5)) for _ in range(n))
            if not any(coefficients):
                coefficients = (Fraction(1),) + coefficients[1:]
            rows.append(
                Constraint(
                    coefficients,
                    rng.choice(("<=", ">=", "=")),
                    Fraction(0 if rng.random() < 0.6 else rng.randint(-6, 6)),
                )
            )
    return LPProblem(
        tuple(Fraction(rng.randint(-5, 5)) for _ in range(n)),
        tuple(rows),
        sense=rng.choice(("max", "min")),
    )


def run_stress(seed: int, count: int, method: Method = "big_m") -> dict[str, int]:
    """Contar por separado errores propios, diferencias y oráculos excluidos."""
    rng = random.Random(seed)
    solver = {"big_m": solve_big_m, "revised": solve_revised}[method]
    totals = dict(seed=seed, count=count, checked=0, errors=0, differences=0, inconclusive=0)
    for _ in range(count):
        problem = random_problem(rng)
        try:
            oracle = verify_with_scipy(problem)
        except OracleInconclusiveError:
            totals["inconclusive"] += 1
            continue
        totals["checked"] += 1
        try:
            own = solver(problem)
        except (ValueError, ArithmeticError):
            totals["errors"] += 1
            continue
        if compare_solution(problem, own, oracle):
            totals["differences"] += 1
    return totals


def main() -> int:
    """Emitir un resumen JSON y fallar si el método propio discrepa o falla."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20261110)
    parser.add_argument("--count", type=int, default=3000)
    parser.add_argument("--method", choices=("big_m", "revised", "both"), default="both")
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count debe ser positivo")
    methods = ("big_m", "revised") if args.method == "both" else (args.method,)
    reports = {method: run_stress(args.seed, args.count, method) for method in methods}
    print(json.dumps(reports, ensure_ascii=False))
    return int(any(report["errors"] or report["differences"] for report in reports.values()))


if __name__ == "__main__":
    raise SystemExit(main())
