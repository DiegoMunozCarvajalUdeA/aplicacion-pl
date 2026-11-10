"""Forma estándar con base inicial identidad y penalización simbólica."""

from fractions import Fraction

from plapp.model import LPProblem
from plapp.mvalue import MValue
from plapp.result import StandardForm


def _unique_name(candidate: str, names: list[str]) -> str:
    """Evitar colisiones con nombres originales o auxiliares ya asignados."""
    name, suffix = candidate, 1
    while name in names:
        name = f"{candidate}_{suffix}"
        suffix += 1
    return name


def to_standard_form(problem: LPProblem) -> StandardForm:
    """Normalizar signos y agregar auxiliares sin cambiar el modelo original.

    1. Multiplicar las filas con b negativo por −1 e invertir la desigualdad.
    2. Agregar holguras y excesos en orden de fila; después, las artificiales.
    3. Elegir holgura o artificial como básica y penalizar con −M/Max o +M/Min.
    4. Registrar el signo aplicado para recuperar derivadas del modelo original.
    """
    signs = tuple(-1 if row.rhs < 0 else 1 for row in problem.constraints)
    relations = []
    transformations = []
    names = list(problem.variable_names)
    kinds = ["original"] * len(names)
    columns = []
    basis = [-1] * len(signs)
    symbol = {"<=": "≤", ">=": "≥", "=": "="}
    for i, (row, sign) in enumerate(zip(problem.constraints, signs, strict=True)):
        relation = row.relation
        if sign == -1:
            relation = {"<=": ">=", ">=": "<=", "=": "="}[relation]
            transformations.append(
                f"{row.name} tenía lado derecho negativo ({row.rhs}): se multiplicó por −1 "
                f"y {symbol[row.relation]} pasó a {symbol[relation]}."
            )
        relations.append(relation)
        if relation != "=":
            kind, prefix, coefficient = (
                ("holgura", "s", 1) if relation == "<=" else ("exceso", "e", -1)
            )
            name = _unique_name(f"{prefix}{i + 1}", names)
            if relation == "<=":
                basis[i] = len(names)
            names.append(name)
            kinds.append(kind)
            columns.append((i, coefficient))
            transformations.append(
                f"{row.name}: se agregó {kind} {name} con coeficiente {coefficient}."
            )
    for i, relation in enumerate(relations):
        if relation != "<=":
            name = _unique_name(f"a{i + 1}", names)
            basis[i] = len(names)
            names.append(name)
            kinds.append("artificial")
            columns.append((i, 1))
            penalty = "−M" if problem.sense == "max" else "+M"
            transformations.append(
                f"{problem.constraints[i].name}: se agregó artificial {name}, con costo {penalty}."
            )
    a = tuple(
        tuple(sign * value for value in row.coefficients)
        + tuple(Fraction(value if i == owner else 0) for owner, value in columns)
        for i, (row, sign) in enumerate(zip(problem.constraints, signs, strict=True))
    )
    c = tuple(MValue(value) for value in problem.objective) + tuple(
        MValue(b=Fraction(-1 if problem.sense == "max" else 1))
        if kind == "artificial"
        else MValue()
        for kind in kinds[len(problem.objective) :]
    )
    transformations.append("Todas las variables de la forma estándar son no negativas.")
    return StandardForm(
        column_names=tuple(names),
        column_types=tuple(kinds),
        a=a,
        b=tuple(sign * row.rhs for sign, row in zip(signs, problem.constraints, strict=True)),
        c=c,
        basis=tuple(basis),
        transformations=tuple(transformations),
        row_signs=signs,
    )
