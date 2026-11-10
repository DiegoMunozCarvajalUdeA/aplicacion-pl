"""Método propio de la Gran M; contrato y guía para el equipo."""

from plapp.model import LPProblem
from plapp.result import Solution


def solve_big_m(problem: LPProblem) -> Solution:
    """Resolver con M simbólica conservando la evidencia de cada pivote.

    1. Convertir a forma estándar y canonizar la fila objetivo respecto a la base.
    2. Con r = c − c_B B⁻¹ A, elegir r positivo en Max o negativo en Min.
       Comparar MValue lexicográficamente, primero b y luego a.
    3. Calcular b_i / a_ij solo para a_ij > 0 y explicar las exclusiones.
       Ante empates o ciclos usar Bland: menor índice elegible al entrar y salir.
    4. Si no hay coeficiente positivo en la entrante, informar no acotada.
    5. Pivotear con Fraction y registrar base, tablero, razones y justificaciones.
    6. Al terminar, una artificial básica positiva indica infactibilidad.
       Quitar artificiales nulas de la base si es posible y filas redundantes.
    7. Buscar óptimos alternos con costo reducido cero en no básicas originales
       o auxiliares no artificiales; exigir un desplazamiento factible no nulo.
       Una básica cero o un empate en razón mínima marca degeneración.
    8. Devolver x, Z original, holguras/excesos, B⁻¹ final y mensajes en español.
    """
    raise NotImplementedError("Pendiente de implementar: Gran M")
