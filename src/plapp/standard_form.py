"""Conversión a forma estándar pendiente de implementación por el equipo."""

from plapp.model import LPProblem
from plapp.result import StandardForm


def to_standard_form(problem: LPProblem) -> StandardForm:
    """Construir la forma estándar exacta y su base inicial.

    1. Si b es negativo, multiplicar la fila por −1 e invertir <= y >=.
    2. Agregar holgura a <=; exceso con −1 y artificial a >=; artificial a =.
    3. Penalizar artificiales con −M en Max y +M en Min usando MValue.
    4. Registrar nombres, tipos de columna, base inicial y cada transformación.
    5. Conservar Fraction en A y b; no modificar el problema original.
    """
    raise NotImplementedError("Pendiente de implementar: forma estándar")
