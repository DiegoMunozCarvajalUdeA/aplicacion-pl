"""Simplex revisado propio; contrato compatible con la Gran M."""

from plapp.model import LPProblem
from plapp.result import Solution


def solve_revised(problem: LPProblem) -> Solution:
    """Resolver manteniendo una base explícita y aritmética exacta.

    1. Obtener forma estándar y una base factible mediante artificiales simbólicas.
    2. Formar B con las columnas básicas e invertirla con operaciones Fraction.
    3. Calcular x_B = B⁻¹b, y = c_B B⁻¹ y r = c − yA en cada iteración.
    4. Elegir r favorable según Max/Min; aplicar Bland ante empates o ciclos.
    5. Obtener d = B⁻¹a_j y razones x_Bi/d_i solo si d_i > 0.
    6. Sin d_i positivo, informar no acotada; de otro modo sustituir la saliente.
    7. Registrar B⁻¹, base, costos reducidos, razones, pivote y explicaciones.
    8. Detectar artificiales positivas, multiplicidad y degeneración como en Gran M.
       Retirar artificiales nulas y filas redundantes antes de la base final.
    9. Devolver el contrato Solution en el sentido original del problema.
    """
    raise NotImplementedError("Pendiente de implementar: simplex revisado")
