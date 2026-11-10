"""Exportación de las iteraciones pendiente de implementación."""

from pathlib import Path

from plapp.result import Solution


def export_steps_pdf(solution: Solution, path: Path) -> None:
    """Exportar evidencia con fpdf2 sin recalcular el método.

    1. Crear FPDF, agregar página y cargar una fuente Unicode con licencia citada.
    2. Escribir forma estándar, transformaciones, estado y solución en español.
    3. Por iteración, escribir razones, decisiones, pivote, tablero o B⁻¹.
    4. Formatear fracciones y M simbólica; paginar tablas sin cortar encabezados.
    5. Guardar con FPDF.output(path); comunicar fallos de escritura a la interfaz.
    """
    raise NotImplementedError("Pendiente de implementar: exportación PDF")
