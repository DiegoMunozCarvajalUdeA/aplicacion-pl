"""Análisis de sensibilidad pendiente de implementación por el equipo."""

from plapp.model import LPProblem
from plapp.result import SensitivityReport, Solution


def sensitivity_analysis(problem: LPProblem, solution: Solution) -> SensitivityReport:
    """Obtener rangos que conservan la base óptima, variando un dato a la vez.

    1. Exigir estado óptimo y base final sin artificiales; advertir sobre degeneración.
    2. Calcular y = c_B B⁻¹ y r = c − yA con Fraction.
    3. Deshacer cambios de signo de filas para reportar ∂Z*/∂b original.
    4. Para un c_j no básico, variar r_j conservando r <= 0 en Max o >= 0 en Min.
    5. Para un c_j básico, variar c_B y exigir esos signos en todos los r no básicos.
    6. Para b_i, resolver B⁻¹(b + Δe_i) >= 0 y trasladar Δ al b_i original.
    7. Expresar extremos infinitos con None y explicar cada precio y rango;
       los intervalos conservan una base, no garantizan unicidad en sus extremos.
    """
    raise NotImplementedError("Pendiente de implementar: sensibilidad")
