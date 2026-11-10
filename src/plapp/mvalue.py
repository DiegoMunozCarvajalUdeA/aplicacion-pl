"""Contrato de la Gran M simbólica; el equipo implementará las operaciones."""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True, eq=False)
class MValue:
    """Representar a + b·M con dos fracciones, sin sustituir M por un número."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __add__(self, other: "MValue") -> "MValue":
        """1. Sumar partes a. 2. Sumar partes b. 3. Devolver un nuevo MValue."""
        raise NotImplementedError("Pendiente de implementar: suma de MValue")

    def __sub__(self, other: "MValue") -> "MValue":
        """1. Restar partes a. 2. Restar partes b. 3. Devolver un nuevo MValue."""
        raise NotImplementedError("Pendiente de implementar: resta de MValue")

    def __mul__(self, scalar: Fraction) -> "MValue":
        """1. Exigir un escalar Fraction. 2. Multiplicar a y b por el escalar."""
        raise NotImplementedError("Pendiente de implementar: producto de MValue")

    def __truediv__(self, scalar: Fraction) -> "MValue":
        """1. Rechazar escalar cero. 2. Dividir a y b por la misma fracción."""
        raise NotImplementedError("Pendiente de implementar: división de MValue")

    def __eq__(self, other: object) -> bool:
        """1. Verificar el tipo. 2. Comparar ambas partes exactas, a y b."""
        raise NotImplementedError("Pendiente de implementar: igualdad de MValue")

    def __lt__(self, other: "MValue") -> bool:
        """1. Comparar b. 2. Solo si empatan, comparar a: orden lexicográfico."""
        raise NotImplementedError("Pendiente de implementar: comparación de MValue")

    def __le__(self, other: "MValue") -> bool:
        """1. Comparar b. 2. En empate, aceptar a menor o igual."""
        raise NotImplementedError("Pendiente de implementar: comparación de MValue")

    def __gt__(self, other: "MValue") -> bool:
        """1. Comparar b. 2. En empate, aceptar a mayor."""
        raise NotImplementedError("Pendiente de implementar: comparación de MValue")

    def __ge__(self, other: "MValue") -> bool:
        """1. Comparar b. 2. En empate, aceptar a mayor o igual."""
        raise NotImplementedError("Pendiente de implementar: comparación de MValue")

    def __str__(self) -> str:
        """1. Omitir partes cero. 2. Simplificar ±1M. 3. Unir a y bM con su signo."""
        raise NotImplementedError("Pendiente de implementar: texto de MValue")
