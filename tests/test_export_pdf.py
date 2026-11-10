"""Leer los PDF generados y comprobar contenido, Unicode y celdas dentro de página."""

from dataclasses import replace
from fractions import Fraction
from io import BytesIO

import pytest
from pypdf import PdfReader

from plapp import export_pdf
from plapp.big_m import solve_big_m
from plapp.export_pdf import _Report, export_steps_pdf
from plapp.formatting import format_number
from plapp.io_json import load_problem
from plapp.result import Solution, Status
from plapp.revised_simplex import solve_revised
from plapp.sensitivity import sensitivity_analysis
from tests.conftest import PROBLEMS
from tests.test_big_m import problem


def read_pdf(data):
    """Parsear un documento real, en lugar de comprobar únicamente su cabecera."""
    assert isinstance(data, bytes) and data.startswith(b"%PDF-")
    reader = PdfReader(BytesIO(data), strict=True)
    assert reader.pages
    return reader, "\n".join(page.extract_text() for page in reader.pages)


@pytest.mark.parametrize("solver", [solve_big_m, solve_revised])
@pytest.mark.parametrize("mode", ["fraction", "decimal"])
def test_all_fixtures_export_content(fixture_problem, solver, mode, monkeypatch):
    """Comprobar cada informe y que sensibilidad reciba la misma solución ya calculada."""
    original, _ = fixture_problem
    solution = solver(original)
    calls = []

    def check_sensitivity(model, result):
        """Exigir la identidad del resultado para descartar una resolución oculta."""
        assert model is original and result is solution
        calls.append(result)
        return sensitivity_analysis(model, result)

    monkeypatch.setattr(export_pdf, "sensitivity_analysis", check_sensitivity)
    reader, text = read_pdf(export_steps_pdf(original, solution, mode))
    assert original.name in text
    assert "Forma estándar" in text and "Resultado final" in text
    assert text.index("Resultado final") < text.index("Notas del documento") < text.index("Fuente:")
    assert ("Gran M" if solution.method == "big_m" else "Simplex revisado") in text
    for state in solution.iterations:
        assert f"Iteración {state.number}\n" in text
        assert (
            state.entering_variable in text
            if state.entering_variable
            else state.entering_reason in text
        )
    assert "[U+" not in text.replace("[U+XXXX]", "")
    if solution.status == Status.OPTIMAL:
        assert len(calls) == 1 and "Análisis de sensibilidad" in text
        assert "Z = " + format_number(solution.objective_value, mode) in text
        assert all(
            label in text
            for label in [
                "Precios sombra",
                "Costos reducidos",
                "Rangos de coeficientes",
                "Rangos de lados derechos",
            ]
        )
    else:
        assert not calls and "Análisis de sensibilidad" not in text
        assert (
            "no tiene solución factible" in text
            if solution.status == Status.INFEASIBLE
            else "solución no acotada" in text
        )
    if solution.method == "revised":
        assert "B⁻¹ y x_B = B⁻¹b" in text and "Multiplicadores y = c_B B⁻¹" in text
    if solution.multiple_optima:
        assert "Solución alterna 1" in text
        assert "segmento" in text or "Rayo óptimo" in text
    for page in reader.pages:
        assert float(page.mediabox.width) > float(page.mediabox.height)


@pytest.mark.parametrize("solver", [solve_big_m, solve_revised])
@pytest.mark.parametrize("mode", ["fraction", "decimal"])
def test_wide_tables_stay_inside_page(solver, mode):
    """Ocho variables y seis filas obligan a dividir columnas sin recortar celdas."""
    original = problem(
        tuple(range(1, 9)),
        [(tuple(int(j == i or j >= 6) for j in range(8)), "<=", 5 + i) for i in range(6)],
    )
    reader, text = read_pdf(export_steps_pdf(original, solver(original), mode))
    assert "Bloque de columnas 1/" in text and "Bloque de columnas 2/" in text
    assert all(name in text for name in original.variable_names)
    assert "Resultado final" in text and "Rangos de lados derechos" in text
    rectangles = []
    for page in reader.pages:
        width, height = float(page.mediabox.width), float(page.mediabox.height)

        def check_rectangle(
            operator, operands, current_matrix, text_matrix, width=width, height=height
        ):
            """Comprobar límites geométricos de las celdas en el PDF ya serializado."""
            if operator != b"re":
                return
            x, y, w, h = map(float, operands)
            rectangles.append((x, y, w, h))
            assert -0.1 <= min(x, x + w) <= max(x, x + w) <= width + 0.1
            assert -0.1 <= min(y, y + h) <= max(y, y + h) <= height + 0.1

        page.extract_text(visitor_operand_before=check_rectangle)
    assert len(rectangles) > 100


def test_decimal_pdf_and_special_certificates():
    """Conservar fracciones exactas en memoria, formato decimal y certificados especiales."""
    original = load_problem(PROBLEMS / "ejemplo_2.json")
    solution = solve_revised(original)
    _, text = read_pdf(export_steps_pdf(original, solution, "decimal", 2))
    assert "Z = 3.4" in text and "17/5" not in text
    assert solution.values == {"x1": Fraction(2, 5), "x2": Fraction(9, 5)}
    duplicate = problem((1, 2), [((1, 1), "=", 4)] * 2)
    _, text = read_pdf(export_steps_pdf(duplicate, solve_revised(duplicate)))
    assert "No disponible (fila redundante)" in text and "Advertencia:" in text
    assert text.count("Cada unidad adicional de R1 ") == 1
    assert text.count("R2: precio sombra no único: fila redundante. Se elige") == 1
    ray = problem((1, 0), [((1, 0), "<=", 1)])
    _, text = read_pdf(export_steps_pdf(ray, solve_big_m(ray)))
    assert "Rayo óptimo: (1, 0) + t·(0, 1)" in text
    cleanup = problem((0,), [((-1,), "=", 0)], "min")
    _, text = read_pdf(export_steps_pdf(cleanup, solve_revised(cleanup)))
    assert "Columna d del retiro artificial" in text and "valor -1" in text


def test_glyphs_unicode_fallback_and_invalid_input(example_one):
    """Validar los símbolos usados y representar explícitamente caracteres desconocidos."""
    report = _Report("fraction", 4)
    symbols = "≤≥−⁻¹ⱼ∂∞·²Δ"
    assert report.safe_text(symbols) == symbols
    assert report.safe_text("\U0010ffff") == "[U+10FFFF]"
    named = replace(example_one, name="Modelo \U0010ffff")
    _, text = read_pdf(export_steps_pdf(named, solve_big_m(named)))
    assert "Modelo [U+10FFFF]" in text
    with pytest.raises(ValueError, match="forma estándar e iteraciones"):
        export_steps_pdf(example_one, Solution("big_m", Status.OPTIMAL, "Sin evidencia"))
    with pytest.raises(ValueError, match="formato"):
        export_steps_pdf(example_one, solve_big_m(example_one), "otro")


@pytest.mark.parametrize("mode", ["fraction", "decimal"])
def test_readable_original_model(mode):
    """El enunciado simplifica coeficientes; las tablas conservan sus ceros y unos."""
    original = load_problem(PROBLEMS / "ejemplo_2.json")
    _, text = read_pdf(export_steps_pdf(original, solve_big_m(original), mode))
    assert "MIN Z = 4·x1 + x2" in text
    assert "R3: -x1 - 2·x2 ≥ -4" in text
