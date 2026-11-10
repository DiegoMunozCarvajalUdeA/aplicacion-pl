"""Informe Unicode de la evidencia existente; nunca vuelve a ejecutar el solver."""

from fractions import Fraction
from pathlib import Path

from fontTools.ttLib import TTFont
from fpdf import FPDF
from fpdf.fonts import FontFace

from plapp.formatting import NumberFormat, format_expression, format_number
from plapp.linalg import column, matvec
from plapp.model import LPProblem
from plapp.mvalue import MValue
from plapp.result import Iteration, Solution, StandardForm, Status
from plapp.sensitivity import sensitivity_analysis, sensitivity_interpretations

FONT_DIR = Path(__file__).parent / "assets/fonts"
if not FONT_DIR.is_dir():
    FONT_DIR = Path(__file__).resolve().parents[2] / "assets/fonts"


class _Report:
    """Centralizar formato, glifos y paginación para no perder celdas del informe."""

    def __init__(self, mode: NumberFormat, decimals: int) -> None:
        """Cargar las fuentes incluidas tanto en el repositorio como en el wheel."""
        format_number(Fraction(0), mode, decimals)
        self.mode, self.decimals = mode, decimals
        self.pdf = FPDF(orientation="L", format="A4")
        self.pdf.set_margins(12, 12, 12)
        self.pdf.set_auto_page_break(True, margin=12)
        self.glyphs: set[int] = set()
        for style, name in (("", "DejaVuSans.ttf"), ("B", "DejaVuSans-Bold.ttf")):
            path = FONT_DIR / name
            self.pdf.add_font("DejaVu", style=style, fname=path)
            with TTFont(path) as font:
                supported = set(font.getBestCmap())
            self.glyphs = self.glyphs & supported if self.glyphs else supported
        self.pdf.add_page()

    def safe_text(self, text: str) -> str:
        """Comprobar cada carácter y explicitar los ajenos a la fuente, sin omitirlos."""
        return "".join(
            character
            if character == "\n" or ord(character) in self.glyphs
            else " "
            if character == "\t"
            else f"[U+{ord(character):04X}]"
            for character in text
        )

    def number(self, value: Fraction | MValue) -> str:
        """Redondear únicamente la representación del dato exacto."""
        return format_number(value, self.mode, self.decimals)

    def text(self, text: str, heading: bool = False) -> None:
        """Ajustar el texto por caracteres y evitar títulos aislados al pie de página."""
        if heading and self.pdf.will_page_break(16):
            self.pdf.add_page()
        self.pdf.set_font("DejaVu", "B" if heading else "", 12 if heading else 9)
        self.pdf.multi_cell(
            0,
            6 if heading else 4.5,
            self.safe_text(text),
            new_x="LMARGIN",
            new_y="NEXT",
            wrapmode="WORD",
        )
        self.pdf.ln(2 if heading else 1)

    def table(
        self, headers: list[str], rows: list[list[str]], pivot: tuple[int, int] | None = None
    ) -> None:
        """Dividir columnas en bloques repitiendo la primera y los encabezados por página."""
        blocks = [
            list(range(1, len(headers)))[start : start + 8]
            for start in range(0, len(headers) - 1, 8)
        ] or [[]]
        for block_number, block in enumerate(blocks, 1):
            columns = [0, *block]
            if self.pdf.will_page_break(20):
                self.pdf.add_page()
            if len(blocks) > 1:
                self.text(
                    f"Bloque de columnas {block_number}/{len(blocks)}; se repite {headers[0]}."
                )
            self.pdf.set_font("DejaVu", size=8)
            with self.pdf.table(
                width=self.pdf.epw,
                col_widths=(1.4, *(1 for _ in block)),
                text_align="LEFT",
                line_height=4.5,
                padding=1.2,
                wrapmode="CHAR",
                repeat_headings=1,
                headings_style=FontFace(fill_color=(226, 232, 240)),
            ) as table:
                header = table.row()
                for j in columns:
                    header.cell(self.safe_text(headers[j]))
                for i, values in enumerate(rows):
                    row = table.row()
                    for j in columns:
                        style = FontFace(fill_color=(254, 240, 138)) if pivot == (i, j) else None
                        row.cell(self.safe_text(values[j]), style=style)
            self.pdf.ln(3)


def _problem(report: _Report, problem: LPProblem, standard: StandardForm) -> None:
    """Incluir el modelo original y todas las transformaciones con el formato elegido."""
    report.text("Programación lineal: paso a paso", heading=True)
    report.text(problem.name)
    expression = format_expression(
        problem.objective, problem.variable_names, report.mode, report.decimals
    )
    report.text(f"{problem.sense.upper()} Z = {expression}")
    symbols = {"<=": "≤", ">=": "≥", "=": "="}
    for row in problem.constraints:
        expression = format_expression(
            row.coefficients, problem.variable_names, report.mode, report.decimals
        )
        report.text(f"{row.name}: {expression} {symbols[row.relation]} {report.number(row.rhs)}")
    report.text(", ".join(problem.variable_names) + " ≥ 0")
    report.text("Forma estándar", heading=True)
    for note in standard.transformations:
        for row in problem.constraints:
            if row.rhs < 0:
                note = note.replace(
                    f"({row.rhs}): se multiplicó", f"({report.number(row.rhs)}): se multiplicó"
                )
        report.text(note)
    report.table(
        ["Columna", "Tipo", "Costo"],
        [
            [name, kind, report.number(cost)]
            for name, kind, cost in zip(
                standard.column_names, standard.column_types, standard.c, strict=True
            )
        ],
    )
    report.table(
        ["Restricción", *standard.column_names, "Lado derecho"],
        [
            [constraint.name, *(report.number(v) for v in row), report.number(rhs)]
            for constraint, row, rhs in zip(
                problem.constraints, standard.a, standard.b, strict=True
            )
        ],
    )
    report.text("Base inicial: " + ", ".join(standard.column_names[j] for j in standard.basis))


def _status_message(report: _Report, problem: LPProblem, solution: Solution) -> str:
    """Presentar el estado sin incorporar fracciones literales ajenas al formato elegido."""
    if solution.status == Status.OPTIMAL:
        return "Se encontró una solución óptima."
    if solution.status == Status.INFEASIBLE:
        return solution.message
    point = ", ".join(report.number(solution.unbounded_origin[n]) for n in problem.variable_names)
    direction = ", ".join(
        report.number(solution.unbounded_direction[n]) for n in problem.variable_names
    )
    change = "crece" if problem.sense == "max" else "decrece"
    return (
        "El problema tiene solución no acotada: "
        "su columna entrante no tiene coeficientes positivos. "
        f"Z {change} sin límite a lo largo de ({', '.join(problem.variable_names)}) "
        f"= ({point}) + t·({direction}), t ≥ 0."
    )


def _iteration(report: _Report, problem: LPProblem, solution: Solution, state: Iteration) -> None:
    """Escribir la evidencia anterior al pivote, con sus razones y exclusiones."""
    standard = solution.standard_form
    report.pdf.add_page()
    report.text(f"Iteración {state.number}", heading=True)
    basics = [standard.column_names[j] for j in state.basis]
    report.text("Base: " + ", ".join(basics))
    for note in state.notes:
        report.text(note)
    if state.tableau is not None:
        report.text("Tablero; cⱼ − zⱼ y Z en la última fila", heading=True)
        rows = [
            [name, *(report.number(v) for v in row)]
            for name, row in zip(basics, state.tableau, strict=True)
        ]
        rows.append(
            [
                "cⱼ − zⱼ",
                *(report.number(v) for v in state.reduced_costs),
                report.number(state.objective_value),
            ]
        )
        pivot = (state.pivot.row, state.pivot.column + 1) if state.pivot else None
        report.table(["Básica", *standard.column_names, "Lado derecho / Z"], rows, pivot)
    else:
        report.text("B⁻¹ y x_B = B⁻¹b", heading=True)
        report.table(
            ["Básica", *(r.name for r in problem.constraints), "x_B"],
            [
                [name, *(report.number(v) for v in row), report.number(value)]
                for name, row, value in zip(
                    basics, state.b_inverse, state.basic_values, strict=True
                )
            ],
        )
        report.text("Multiplicadores y = c_B B⁻¹ (filas normalizadas)")
        report.table(
            ["Vector", *(r.name for r in problem.constraints)],
            [["y", *(report.number(v) for v in state.multipliers)]],
        )
        report.table(
            ["Fila", *standard.column_names],
            [["cⱼ − zⱼ", *(report.number(v) for v in state.reduced_costs)]],
        )
    report.text(f"Z = {report.number(state.objective_value)}")
    report.text(
        f"Entrante: {state.entering_variable}. {state.entering_reason}"
        if state.entering_variable
        else "Terminación: " + state.entering_reason
    )
    _ratios(report, standard, state)
    if state.leaving_variable:
        report.text(f"Saliente: {state.leaving_variable}. {state.leaving_reason}")
    elif state.leaving_reason:
        message = (
            _status_message(report, problem, solution)
            if solution.status == Status.UNBOUNDED
            else state.leaving_reason
        )
        report.text(message)
    if state.pivot:
        p = state.pivot
        report.text(
            f"Pivote resaltado: fila {p.row + 1}, columna {standard.column_names[p.column]}, "
            f"valor {report.number(p.value)}."
        )


def _ratios(report: _Report, standard: StandardForm, state: Iteration) -> None:
    """Resaltar d_p en el revisado y explicar el retiro de paso cero sin razón mínima."""
    if state.ratios:
        report.text("Prueba de la razón mínima", heading=True)
        report.table(
            [
                "Básica",
                "x_B",
                "d = B⁻¹aⱼ" if state.tableau is None else "Coeficiente",
                "Razón",
                "Exclusión",
            ],
            [
                [
                    r.basic_variable,
                    report.number(r.rhs),
                    report.number(r.coefficient),
                    report.number(r.ratio) if r.ratio is not None else "—",
                    r.exclusion_reason,
                ]
                for r in state.ratios
            ],
            (state.pivot.row, 2) if state.pivot else None,
        )
    elif state.b_inverse is not None and state.pivot:
        report.text("Columna d del retiro artificial; no requiere razón mínima.")
        direction = matvec(state.b_inverse, column(standard.a, state.pivot.column))
        report.table(
            ["Básica", "d = B⁻¹aⱼ"],
            [
                [standard.column_names[j], report.number(value)]
                for j, value in zip(state.basis, direction, strict=True)
            ],
            (state.pivot.row, 1),
        )


def _result(report: _Report, problem: LPProblem, solution: Solution) -> None:
    """Conservar certificados de resultado, multiplicidad y no acotación."""
    report.pdf.add_page()
    report.text("Resultado final", heading=True)
    report.text(_status_message(report, problem, solution))
    if solution.objective_value is not None:
        report.text("Z = " + report.number(solution.objective_value))
        report.table(
            ["Variable", "Valor"], [[n, report.number(v)] for n, v in solution.values.items()]
        )
        kinds = {"<=": "Holgura", ">=": "Exceso", "=": "Igualdad"}
        report.table(
            ["Restricción", "Tipo", "Valor"],
            [
                [r.name, kinds[r.relation], report.number(solution.slacks[r.name])]
                for r in problem.constraints
            ],
        )
    for note in solution.notes:
        report.text(note)
    point = "(" + ", ".join(report.number(v) for v in solution.values.values()) + ")"
    for index, alternative in enumerate(solution.alternative_solutions, 1):
        report.text(f"Solución alterna {index}", heading=True)
        report.table(["Variable", "Valor"], [[n, report.number(v)] for n, v in alternative.items()])
        if not solution.alternative_rays:
            other = "(" + ", ".join(report.number(alternative[n]) for n in solution.values) + ")"
            report.text(
                f"Z = {report.number(solution.objective_value)} en todo el segmento "
                f"entre {point} y {other}."
            )
    for ray in solution.alternative_rays:
        direction = ", ".join(report.number(ray[n]) for n in solution.values)
        report.text(
            f"Rayo óptimo: {point} + t·({direction}), t ≥ 0; "
            f"Z = {report.number(solution.objective_value)}."
        )
    if solution.unbounded_direction:
        report.table(
            ["Variable", "Origen factible", "Dirección de no acotamiento"],
            [
                [
                    n,
                    report.number(solution.unbounded_origin[n]),
                    report.number(solution.unbounded_direction[n]),
                ]
                for n in problem.variable_names
            ],
        )


def _sensitivity(report: _Report, problem: LPProblem, solution: Solution) -> None:
    """Derivar sensibilidad de la base ya resuelta, sin volver a llamar a un método."""
    sensitivity = sensitivity_analysis(problem, solution)
    interpretations = sensitivity_interpretations(
        problem, sensitivity, solution, report.mode, report.decimals
    )
    report.text("Análisis de sensibilidad", heading=True)
    for warning in sensitivity.warnings:
        report.text("Advertencia: " + warning)
    report.text("Precios sombra")
    report.table(
        ["Restricción", "Precio sombra ∂Z*/∂b"],
        [[n, report.number(v)] for n, v in sensitivity.shadow_prices.items()],
    )
    report.text("Costos reducidos")
    report.table(
        ["Variable", "cⱼ − zⱼ"],
        [[n, report.number(v)] for n, v in sensitivity.reduced_costs.items()],
    )
    for name in problem.variable_names:
        report.text(interpretations[f"r:{name}"])
    for label, names, ranges, prefix in (
        ("Rangos de coeficientes", problem.variable_names, sensitivity.objective_ranges, "c"),
        (
            "Rangos de lados derechos",
            tuple(r.name for r in problem.constraints),
            sensitivity.rhs_ranges,
            "b",
        ),
    ):
        report.text(label, heading=True)
        rows = []
        for name in names:
            if name not in ranges:
                rows.append(
                    [name, "No disponible (fila redundante)", "No disponible (fila redundante)"]
                )
            else:
                lower, upper = ranges[name]
                rows.append(
                    [
                        name,
                        report.number(lower) if lower is not None else "−∞",
                        report.number(upper) if upper is not None else "+∞",
                    ]
                )
        report.table(["Dato", "Inferior", "Superior"], rows)
        for name in names:
            report.text(interpretations[f"{prefix}:{name}"])


def export_steps_pdf(
    problem: LPProblem, solution: Solution, mode: NumberFormat = "fraction", decimals: int = 4
) -> bytes:
    """Exportar modelo, evidencia y sensibilidad con fuentes locales y formato elegido."""
    if solution.standard_form is None or not solution.iterations:
        raise ValueError("El PDF requiere una solución con forma estándar e iteraciones.")
    report = _Report(mode, decimals)
    _problem(report, problem, solution.standard_form)
    method = "Gran M" if solution.method == "big_m" else "Simplex revisado"
    report.text("Método: " + method)
    for state in solution.iterations:
        _iteration(report, problem, solution, state)
    _result(report, problem, solution)
    if solution.status == Status.OPTIMAL:
        _sensitivity(report, problem, solution)
    report.text("Notas del documento", heading=True)
    report.text("Fuente: DejaVu Sans 2.37. Un carácter sin glifo se representa como [U+XXXX].")
    return bytes(report.pdf.output())
