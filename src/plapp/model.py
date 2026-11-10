"""Modelo exacto y validación de los datos ingresados por el usuario."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from fractions import Fraction
from typing import Literal

Sense = Literal["max", "min"]
Relation = Literal["<=", ">=", "="]


@dataclass(frozen=True)
class ValidationIssue:
    """Ubicación y explicación de un dato inválido."""

    location: str
    message: str


@dataclass(frozen=True)
class Constraint:
    """Restricción lineal con coeficientes exactos."""

    coefficients: tuple[Fraction, ...]
    relation: Relation
    rhs: Fraction
    name: str = ""


@dataclass(frozen=True)
class LPProblem:
    """Problema lineal; todas las variables son no negativas."""

    objective: tuple[Fraction, ...]
    constraints: tuple[Constraint, ...]
    name: str = "Problema sin nombre"
    sense: Sense = "max"
    variable_names: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Asignar nombres por defecto sin modificar el problema original."""
        if not self.variable_names:
            names = tuple(f"x{i + 1}" for i in range(len(self.objective)))
            object.__setattr__(self, "variable_names", names)
        constraints = tuple(
            row if row.name else replace(row, name=f"R{i + 1}")
            for i, row in enumerate(self.constraints)
        )
        object.__setattr__(self, "constraints", constraints)


def parse_number(text: str | int | float | Fraction) -> Fraction:
    """Leer enteros, decimales con punto o coma y fracciones, sin redondear."""
    if isinstance(text, bool) or not isinstance(text, (str, int, float, Fraction)):
        raise ValueError("Ingrese un número entero, decimal o una fracción como 2/5.")
    value = str(text).strip()
    if not value:
        raise ValueError("El campo está vacío; ingrese un número.")
    try:
        return Fraction(value.replace(",", "."))
    except (ValueError, ZeroDivisionError, OverflowError) as error:
        raise ValueError(
            "Número inválido; use 2, -3, 2,5 o 2/5, con denominador no nulo."
        ) from error


def _is_list(value: object) -> bool:
    """Reconocer secuencias de campos, excluyendo texto."""
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes))


def _numbers(values: Sequence, location: str, issues: list[ValidationIssue]) -> tuple:
    """Leer una fila y acumular errores por celda."""
    parsed = []
    for index, value in enumerate(values, 1):
        try:
            parsed.append(parse_number(value))
        except ValueError as error:
            issues.append(ValidationIssue(f"{location}, x{index}", str(error)))
    return tuple(parsed)


def validate(raw: object) -> tuple[LPProblem | None, list[ValidationIssue]]:
    """Validar el esquema JSON español y devolver todos los errores detectables."""
    issues: list[ValidationIssue] = []
    if not isinstance(raw, Mapping):
        return None, [
            ValidationIssue("problema", "Se esperaba un objeto con los datos del problema.")
        ]
    objective = raw.get("objetivo", [])
    rows = raw.get("restricciones", [])
    if not _is_list(objective) or len(objective) < 1:
        issues.append(ValidationIssue("objetivo", "Debe haber al menos una variable (n ≥ 1)."))
        objective = []
    if not _is_list(rows) or len(rows) < 1:
        issues.append(
            ValidationIssue("restricciones", "Debe haber al menos una restricción (m ≥ 1).")
        )
        rows = []
    n = len(objective)
    for key, size in (("n", n), ("m", len(rows))):
        if key in raw and (type(raw[key]) is not int or raw[key] < 1 or raw[key] != size):
            issues.append(
                ValidationIssue(key, "La dimensión debe ser positiva y coincidir con los datos.")
            )
    sense = raw.get("sentido", "max")
    if sense not in ("max", "min"):
        issues.append(ValidationIssue("sentido", "Seleccione max o min."))
    names = raw.get("variables", [f"x{i + 1}" for i in range(n)])
    if (
        not _is_list(names)
        or len(names) != n
        or any(not isinstance(name, str) or not name.strip() for name in names)
    ):
        issues.append(ValidationIssue("variables", "Ingrese un nombre no vacío por variable."))
        names = []
    names = [name.strip() for name in names]
    if len(set(names)) != len(names):
        issues.append(
            ValidationIssue("variables", "Los nombres de las variables no pueden repetirse.")
        )
    parsed_objective = _numbers(objective, "objetivo", issues)
    constraints = []
    for index, row in enumerate(rows, 1):
        location = f"restricción {index}"
        if not isinstance(row, Mapping):
            issues.append(
                ValidationIssue(location, "Se esperaba un objeto con coeficientes, signo y rhs.")
            )
            continue
        name = row.get("nombre", f"R{index}")
        if not isinstance(name, str) or not name.strip():
            issues.append(
                ValidationIssue(location, "El nombre de la restricción no puede estar vacío.")
            )
            name = f"R{index}"
        name = name.strip()
        coefficients = row.get("coeficientes", [])
        if not _is_list(coefficients) or len(coefficients) != n:
            issues.append(ValidationIssue(location, f"Se esperaban {n} coeficientes."))
            coefficients = []
        parsed = _numbers(coefficients, location, issues)
        if parsed and len(parsed) == n and all(value == 0 for value in parsed):
            issues.append(ValidationIssue(location, "No todos los coeficientes pueden ser cero."))
        relation = row.get("signo")
        if relation not in ("<=", ">=", "="):
            issues.append(ValidationIssue(f"{location}, signo", "Use <=, >= o =."))
        try:
            rhs = parse_number(row.get("rhs", ""))
        except ValueError as error:
            issues.append(ValidationIssue(f"lado derecho de {name}", str(error)))
            rhs = Fraction(0)
        constraints.append(Constraint(parsed, relation, rhs, name))
    if len({row.name for row in constraints}) != len(constraints):
        issues.append(
            ValidationIssue("restricciones", "Los nombres de las restricciones deben ser únicos.")
        )
    name = raw.get("nombre", "Problema sin nombre")
    if not isinstance(name, str) or not name.strip():
        issues.append(ValidationIssue("nombre", "Ingrese un nombre para el problema."))
    if issues:
        return None, issues
    return LPProblem(parsed_objective, tuple(constraints), name.strip(), sense, tuple(names)), []
