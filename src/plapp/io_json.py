"""Carga y guardado JSON con números escritos como texto exacto."""

import json
from pathlib import Path

from plapp.model import LPProblem, validate


def problem_to_dict(problem: LPProblem) -> dict:
    """Serializar solo el modelo; los resultados esperados pertenecen a las pruebas."""
    return {
        "nombre": problem.name,
        "sentido": problem.sense,
        "variables": list(problem.variable_names),
        "objetivo": [str(value) for value in problem.objective],
        "restricciones": [
            {
                "nombre": row.name,
                "coeficientes": [str(value) for value in row.coefficients],
                "signo": row.relation,
                "rhs": str(row.rhs),
            }
            for row in problem.constraints
        ],
    }


def load_problem(source: str | bytes | Path) -> LPProblem:
    """Leer un Path, texto JSON o bytes UTF-8; informar errores en español."""
    try:
        text = source.read_text(encoding="utf-8") if isinstance(source, Path) else source
        raw = json.loads(text)
    except (OSError, ValueError, UnicodeError, TypeError) as error:
        raise ValueError(
            "No se pudo leer el archivo: use un JSON válido con codificación UTF-8."
        ) from error
    problem, issues = validate(raw)
    if issues:
        raise ValueError("; ".join(f"{issue.location}: {issue.message}" for issue in issues))
    assert problem is not None
    return problem


def save_problem(problem: LPProblem, path: Path | None = None) -> str:
    """Devolver JSON y, si se solicita, escribirlo en un archivo UTF-8."""
    text = json.dumps(problem_to_dict(problem), ensure_ascii=False, indent=2) + "\n"
    if path is not None:
        try:
            path.write_text(text, encoding="utf-8")
        except OSError as error:
            raise ValueError("No se pudo guardar el archivo JSON en la ruta indicada.") from error
    return text
