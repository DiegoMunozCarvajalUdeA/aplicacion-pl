"""Aritmética exacta de a + b·M, con M positiva y dominante."""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True, eq=False)
class MValue:
    """Comparar primero b y luego a sin asignar un valor numérico a M."""

    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    def __post_init__(self) -> None:
        """Normalizar enteros a fracciones y rechazar aproximaciones decimales."""
        if not isinstance(self.a, (int, Fraction)) or not isinstance(self.b, (int, Fraction)):
            raise TypeError("Las partes de MValue deben ser enteros o Fraction.")
        object.__setattr__(self, "a", Fraction(self.a))
        object.__setattr__(self, "b", Fraction(self.b))

    @staticmethod
    def _coerce(other: object) -> "MValue | None":
        """Tratar un escalar exacto como una expresión sin parte M."""
        if isinstance(other, MValue):
            return other
        if isinstance(other, (int, Fraction)):
            return MValue(Fraction(other))
        return None

    def __add__(self, other: "MValue | Fraction | int") -> "MValue":
        """Sumar independientemente las partes racional y simbólica."""
        value = self._coerce(other)
        if value is None:
            return NotImplemented
        return MValue(self.a + value.a, self.b + value.b)

    def __radd__(self, other: "MValue | Fraction | int") -> "MValue":
        """Permitir sumas iniciadas por un escalar, incluido sum()."""
        return self + other

    def __neg__(self) -> "MValue":
        """Cambiar el signo de ambas partes."""
        return MValue(-self.a, -self.b)

    def __sub__(self, other: "MValue | Fraction | int") -> "MValue":
        """Restar ambas partes sin introducir productos de M."""
        value = self._coerce(other)
        if value is None:
            return NotImplemented
        return self + (-value)

    def __rsub__(self, other: "MValue | Fraction | int") -> "MValue":
        """Permitir que el minuendo sea un escalar exacto."""
        return -self + other

    def __mul__(self, scalar: Fraction | int) -> "MValue":
        """Escalar ambas partes; M por M queda fuera de esta representación."""
        if not isinstance(scalar, (int, Fraction)):
            return NotImplemented
        return MValue(self.a * scalar, self.b * scalar)

    def __rmul__(self, scalar: Fraction | int) -> "MValue":
        """Permitir el escalar a la izquierda."""
        return self * scalar

    def __truediv__(self, scalar: Fraction | int) -> "MValue":
        """Dividir ambas partes por un escalar exacto no nulo."""
        if not isinstance(scalar, (int, Fraction)):
            return NotImplemented
        if scalar == 0:
            raise ZeroDivisionError("No se puede dividir MValue entre cero.")
        return MValue(self.a / scalar, self.b / scalar)

    def __eq__(self, other: object) -> bool:
        """Exigir igualdad exacta de ambas partes, también frente a escalares."""
        value = self._coerce(other)
        if value is None:
            return NotImplemented
        return self.a == value.a and self.b == value.b

    def __hash__(self) -> int:
        """Compartir hash con Fraction cuando no hay parte simbólica."""
        return hash(self.a) if self.b == 0 else hash((self.a, self.b))

    def __lt__(self, other: "MValue | Fraction | int") -> bool:
        """La parte M domina cualquier diferencia racional finita."""
        value = self._coerce(other)
        if value is None:
            return NotImplemented
        return (self.b, self.a) < (value.b, value.a)

    def __le__(self, other: "MValue | Fraction | int") -> bool:
        """Aceptar orden estricto o igualdad exacta."""
        value = self._coerce(other)
        if value is None:
            return NotImplemented
        return (self.b, self.a) <= (value.b, value.a)

    def __gt__(self, other: "MValue | Fraction | int") -> bool:
        """Comparar lexicográficamente en sentido mayor."""
        value = self._coerce(other)
        if value is None:
            return NotImplemented
        return (self.b, self.a) > (value.b, value.a)

    def __ge__(self, other: "MValue | Fraction | int") -> bool:
        """Aceptar orden mayor o igualdad exacta."""
        value = self._coerce(other)
        if value is None:
            return NotImplemented
        return (self.b, self.a) >= (value.b, value.a)

    def is_zero(self) -> bool:
        """Reconocer el cero exacto en ambas partes."""
        return self == 0

    def is_positive(self) -> bool:
        """Reconocer mejora positiva bajo el orden simbólico."""
        return self > 0

    def is_negative(self) -> bool:
        """Reconocer mejora negativa bajo el orden simbólico."""
        return self < 0

    def __str__(self) -> str:
        """Omitir ceros y simplificar los coeficientes ±1 de M."""
        if self.b == 0:
            return str(self.a)
        term = "M" if abs(self.b) == 1 else f"{abs(self.b)}M"
        if self.a == 0:
            return ("-" if self.b < 0 else "") + term
        return f"{self.a} {'-' if self.b < 0 else '+'} {term}"
