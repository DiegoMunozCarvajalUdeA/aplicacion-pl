"""Presentación de fracciones y coeficientes simbólicos, sin resolver el problema."""

from decimal import Decimal, localcontext
from fractions import Fraction
from typing import Literal

from plapp.mvalue import MValue

NumberFormat = Literal["fraction", "decimal"]


def format_number(
    value: Fraction | MValue, mode: NumberFormat = "fraction", decimals: int = 4
) -> str:
    """Mostrar un valor exacto o a + bM sin depender de operaciones de MValue."""
    if mode not in ("fraction", "decimal"):
        raise ValueError("El formato debe ser fraction o decimal.")
    if not isinstance(decimals, int) or isinstance(decimals, bool) or not 0 <= decimals <= 12:
        raise ValueError("El número de decimales debe estar entre 0 y 12.")
    if isinstance(value, MValue):
        if value.b == 0:
            return format_number(value.a, mode, decimals)
        magnitude = abs(value.b)
        term = "M" if magnitude == 1 else f"{format_number(magnitude, mode, decimals)}M"
        if value.a == 0:
            return ("-" if value.b < 0 else "") + term
        sign = "-" if value.b < 0 else "+"
        return f"{format_number(value.a, mode, decimals)} {sign} {term}"
    if mode == "fraction":
        return str(value)
    with localcontext() as context:
        context.prec = (
            max(len(str(abs(value.numerator))), len(str(value.denominator))) + decimals + 10
        )
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
        rendered = f"{decimal:.{decimals}f}"
    if Decimal(rendered) == 0:
        return "0"
    return rendered.rstrip("0").rstrip(".") if "." in rendered else rendered


def format_expression(
    coefficients: tuple[Fraction, ...],
    names: tuple[str, ...],
    mode: NumberFormat = "fraction",
    decimals: int = 4,
) -> str:
    """Omitir ceros y coeficientes unitarios exactos para facilitar la lectura."""
    terms = []
    for value, name in zip(coefficients, names, strict=True):
        if value == 0:
            continue
        magnitude = abs(value)
        term = name if magnitude == 1 else f"{format_number(magnitude, mode, decimals)}·{name}"
        sign = ("-" if value < 0 else "") if not terms else (" - " if value < 0 else " + ")
        terms.append(sign + term)
    return "".join(terms) or "0"
