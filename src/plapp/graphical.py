"""Geometría del método gráfico pendiente de implementación."""

from plapp.model import LPProblem
from plapp.result import GraphicalResult


def graphical_method(problem: LPProblem) -> GraphicalResult:
    """Calcular región, vértices e isoutilidad sin librerías de optimización.

    1. Si n != 2, devolver applicable=False y explicar por qué no aplica.
    2. Intersecar pares de rectas de restricciones y ejes; tratar paralelas e iguales.
    3. Filtrar por todas las restricciones y x >= 0, deduplicar con Fraction.
    4. Detectar vacío y direcciones de recesión; distinguir región no acotada
       de objetivo no acotado (puede haber un óptimo finito en región no acotada).
    5. Ordenar vértices alrededor del centroide. Manejar segmentos y puntos aislados.
    6. Recortar regiones no acotadas con una caja mayor al vértice más lejano;
       conservar separados los vértices reales y los puntos artificiales del recorte.
    7. Evaluar Z en vértices, identificar puntos/segmentos óptimos y recortar
       rectas rotuladas e isoutilidad para que la UI únicamente las dibuje.
    """
    raise NotImplementedError("Pendiente de implementar: método gráfico")
