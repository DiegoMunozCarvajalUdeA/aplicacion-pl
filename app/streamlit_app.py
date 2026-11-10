"""Interfaz base; solo los métodos del equipo podrán producir soluciones."""

from fractions import Fraction
from itertools import zip_longest
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from plapp.big_m import solve_big_m
from plapp.export_pdf import export_steps_pdf
from plapp.formatting import format_expression, format_number
from plapp.graphical import graphical_method
from plapp.io_json import load_problem, problem_to_dict, save_problem
from plapp.linalg import column as matrix_column
from plapp.linalg import matvec
from plapp.model import LPProblem, validate
from plapp.result import GraphicalResult, Iteration, Solution, StandardForm, Status
from plapp.revised_simplex import solve_revised
from plapp.sensitivity import sensitivity_analysis, sensitivity_interpretations
from plapp.standard_form import to_standard_form

FIXTURES = Path(__file__).resolve().parents[1] / "tests/fixtures/problems"
METHODS = {"Gran M": solve_big_m, "Simplex revisado": solve_revised}


def invalidate() -> None:
    """Descartar resultados al editar para no mostrar una solución de otros datos."""
    st.session_state.pop("validated", None)
    st.session_state["solutions"] = {}
    st.session_state["notices"] = {}


def replace_problem(problem: LPProblem) -> None:
    """Cargar un modelo y crear una nueva identidad para sus editores."""
    st.session_state["raw"] = problem_to_dict(problem)
    st.session_state["sense"] = problem.sense
    st.session_state["revision"] = st.session_state.get("revision", 0) + 1
    invalidate()


def resize(kind: str, change: int) -> None:
    """Modificar dimensiones conservando las celdas que siguen existiendo."""
    raw = st.session_state["raw"]
    if kind == "variable":
        if change > 0:
            index = 1
            while f"x{index}" in raw["variables"]:
                index += 1
            raw["variables"].append(f"x{index}")
            raw["objetivo"].append("0")
            for row in raw["restricciones"]:
                row["coeficientes"].append("0")
        elif len(raw["variables"]) > 1:
            raw["variables"].pop()
            raw["objetivo"].pop()
            for row in raw["restricciones"]:
                row["coeficientes"].pop()
    elif change > 0:
        index = 1
        while any(row["nombre"] == f"R{index}" for row in raw["restricciones"]):
            index += 1
        raw["restricciones"].append(
            {
                "nombre": f"R{index}",
                "coeficientes": ["0"] * len(raw["variables"]),
                "signo": "<=",
                "rhs": "0",
            }
        )
    elif len(raw["restricciones"]) > 1:
        raw["restricciones"].pop()
    st.session_state["revision"] += 1
    invalidate()


def apply_edits(key: str, objective: bool) -> None:
    """Guardar cambios por celda antes de cualquier acción que reconstruya la tabla."""
    raw = st.session_state["raw"]
    for index, edits in st.session_state[key]["edited_rows"].items():
        for column, value in edits.items():
            text = "" if value is None else str(value)
            if column.startswith("x"):
                position = int(column[1:]) - 1
                target = (
                    raw["objetivo"]
                    if objective
                    else raw["restricciones"][int(index)]["coeficientes"]
                )
                target[position] = text
            elif not objective and column in ("signo", "rhs"):
                raw["restricciones"][int(index)][column] = text
    invalidate()


def change_sense() -> None:
    """Aplicar el sentido elegido y limpiar resultados anteriores."""
    st.session_state["raw"]["sentido"] = st.session_state["sense"]
    invalidate()


def load_example() -> None:
    """Cargar solo los datos de entrada del ejemplo seleccionado."""
    try:
        replace_problem(load_problem(FIXTURES / st.session_state["example"]))
    except ValueError as error:
        st.session_state["load_error"] = str(error)


def upload_problem() -> None:
    """Leer el archivo subido sin sustituir el problema si la carga falla."""
    uploaded = st.session_state.get("upload")
    if uploaded is not None:
        try:
            replace_problem(load_problem(uploaded.getvalue()))
        except ValueError as error:
            st.session_state["load_error"] = str(error)


def number(value) -> str:
    """Usar el formato de presentación seleccionado."""
    mode = "fraction" if st.session_state["format"] == "Fracciones" else "decimal"
    return format_number(value, mode, st.session_state["decimals"])


def render_summary(problem: LPProblem) -> None:
    """Mostrar el problema validado sin convertirlo a forma estándar."""
    mode = "fraction" if st.session_state["format"] == "Fracciones" else "decimal"
    decimals = st.session_state["decimals"]
    expression = format_expression(problem.objective, problem.variable_names, mode, decimals)
    st.write(f"{problem.sense.upper()} Z = {expression}")
    for row in problem.constraints:
        expression = format_expression(row.coefficients, problem.variable_names, mode, decimals)
        relation = {"<=": "≤", ">=": "≥", "=": "="}[row.relation]
        st.write(f"{row.name}: {expression} {relation} {number(row.rhs)}")
    st.write(", ".join(problem.variable_names) + " ≥ 0")


def render_alternatives(solution: Solution) -> None:
    """Presentar los puntos y rayos certificados con el formato elegido."""
    st.info("Hay soluciones óptimas múltiples.")
    names = tuple(solution.values)
    point = "(" + ", ".join(number(solution.values[name]) for name in names) + ")"
    for index, alternative in enumerate(solution.alternative_solutions, 1):
        st.write(f"Solución alterna {index}")
        st.table([{"Variable": name, "Valor": number(alternative[name])} for name in names])
    if solution.alternative_rays:
        for ray in solution.alternative_rays:
            direction = "(" + ", ".join(number(ray[name]) for name in names) + ")"
            st.write(
                f"Z = {number(solution.objective_value)} en todo el rayo desde {point}, "
                f"con dirección {direction}; el parámetro es no negativo."
            )
    else:
        for alternative in solution.alternative_solutions:
            other = "(" + ", ".join(number(alternative[name]) for name in names) + ")"
            st.write(
                f"Z = {number(solution.objective_value)} en todo el segmento "
                f"entre {point} y {other}."
            )


def render_solution(problem: LPProblem, solution: Solution) -> None:
    """Presentar resultados originales, alternativas y notas del método propio."""
    # El mensaje de multiplicidad se reconstruye con datos exactos para respetar decimales.
    if solution.status == Status.UNBOUNDED and solution.unbounded_direction:
        point = ", ".join(
            number(solution.unbounded_origin[name]) for name in problem.variable_names
        )
        ray = ", ".join(
            number(solution.unbounded_direction[name]) for name in problem.variable_names
        )
        change = "crece" if problem.sense == "max" else "decrece"
        st.write(
            "El problema tiene solución no acotada. "
            f"Z {change} sin límite a lo largo de ({', '.join(problem.variable_names)}) "
            f"= ({point}) + t·({ray}), t ≥ 0."
        )
    else:
        st.write(
            "Se encontró una solución óptima." if solution.multiple_optima else solution.message
        )
    if solution.status == Status.OPTIMAL:
        st.table(
            [{"Variable": name, "Valor": number(value)} for name, value in solution.values.items()]
        )
        if solution.objective_value is not None:
            st.write(f"Z = {number(solution.objective_value)}")
        kinds = {"<=": "Holgura", ">=": "Exceso", "=": "Igualdad"}
        st.table(
            [
                {
                    "Restricción": row.name,
                    "Tipo": kinds[row.relation],
                    "Valor": number(solution.slacks[row.name]),
                }
                for row in problem.constraints
            ]
        )
        if solution.multiple_optima:
            render_alternatives(solution)
        if solution.degenerate:
            st.info("Se detectó degeneración.")
    for note in solution.notes:
        st.write(note)


def render_iteration_tables(
    problem: LPProblem, standard: StandardForm, iteration: Iteration
) -> None:
    """Rotular tableros y B⁻¹; el resaltado usa coordenadas del pivote registrado."""
    basic_names = [standard.column_names[j] for j in iteration.basis]
    if iteration.tableau:
        rows = [[number(value) for value in row] for row in iteration.tableau]
        labels = basic_names.copy()
        if iteration.reduced_costs:
            rows.append(
                [number(value) for value in iteration.reduced_costs]
                + [
                    number(iteration.objective_value)
                    if iteration.objective_value is not None
                    else "—"
                ]
            )
            labels.append("cⱼ − zⱼ (Z en lado derecho)")
        frame = pd.DataFrame(rows, index=labels, columns=[*standard.column_names, "Lado derecho"])
        frame.index.name = "Variable básica"
        st.write("Tablero")
        if iteration.pivot:

            def highlight(data):
                """Colorear solo la celda pivote, sin tocar los valores del tablero."""
                styles = pd.DataFrame("", index=data.index, columns=data.columns)
                styles.iloc[iteration.pivot.row, iteration.pivot.column] = (
                    "background-color: #fef08a; color: #111827; font-weight: bold"
                )
                return styles

            st.table(frame.style.apply(highlight, axis=None))
        else:
            st.table(frame)
    if iteration.b_inverse:
        st.write("B⁻¹")
        st.table(
            pd.DataFrame(
                [[number(value) for value in row] for row in iteration.b_inverse],
                index=basic_names,
                columns=[row.name for row in problem.constraints],
            )
        )
        if iteration.basic_values:
            st.write("Valores básicos x_B = B⁻¹b")
            st.table(
                pd.DataFrame(
                    {"x_B": [number(value) for value in iteration.basic_values]}, index=basic_names
                )
            )
        if iteration.multipliers:
            st.write("Multiplicadores y = c_B B⁻¹ (filas normalizadas)")
            st.table(
                pd.DataFrame(
                    [[number(value) for value in iteration.multipliers]],
                    index=["y"],
                    columns=[row.name for row in problem.constraints],
                )
            )
    if iteration.reduced_costs and iteration.tableau is None:
        st.write("Costos reducidos")
        st.table(
            pd.DataFrame(
                [[number(value) for value in iteration.reduced_costs]],
                index=["cⱼ − zⱼ"],
                columns=standard.column_names,
            )
        )
    if iteration.objective_value is not None:
        st.write(f"Z = {number(iteration.objective_value)}")


def highlight_pivot(data: pd.DataFrame, row: int, column: int) -> pd.DataFrame:
    """Resaltar el coeficiente d ya certificado por el método revisado."""
    styles = pd.DataFrame("", index=data.index, columns=data.columns)
    styles.iloc[row, column] = "background-color: #fef08a; color: #111827; font-weight: bold"
    return styles


def render_iteration(problem: LPProblem, standard: StandardForm, iteration: Iteration) -> None:
    """Mostrar decisiones y pruebas que permiten reproducir el pivote."""
    with st.expander(f"Iteración {iteration.number}", expanded=True):
        st.write("Base: " + ", ".join(standard.column_names[j] for j in iteration.basis))
        for note in iteration.notes:
            st.write(note)
        render_iteration_tables(problem, standard, iteration)
        if iteration.entering_variable is None:
            st.write("Terminación: " + iteration.entering_reason)
        else:
            st.write(f"Entrante: {iteration.entering_variable}. {iteration.entering_reason}")
        if iteration.ratios:
            st.write("Prueba de la razón mínima")
            coefficient_label = "d = B⁻¹aⱼ" if iteration.tableau is None else "Coeficiente"
            ratios = pd.DataFrame(
                [
                    {
                        "Fila": row.row + 1,
                        "Básica": row.basic_variable,
                        "Lado derecho": number(row.rhs),
                        coefficient_label: number(row.coefficient),
                        "Razón": number(row.ratio) if row.ratio is not None else "—",
                        "Exclusión": row.exclusion_reason,
                    }
                    for row in iteration.ratios
                ]
            )
            if iteration.tableau is None and iteration.pivot:
                st.table(
                    ratios.style.apply(
                        highlight_pivot,
                        axis=None,
                        row=iteration.pivot.row,
                        column=ratios.columns.get_loc(coefficient_label),
                    )
                )
            else:
                st.table(ratios)
        elif iteration.b_inverse and iteration.pivot:
            st.write("Columna d para el retiro de artificial en 0; no requiere razón mínima.")
            direction = matvec(
                iteration.b_inverse, matrix_column(standard.a, iteration.pivot.column)
            )
            frame = pd.DataFrame(
                {"d = B⁻¹aⱼ": [number(v) for v in direction]},
                index=[standard.column_names[j] for j in iteration.basis],
            )
            st.table(
                frame.style.apply(highlight_pivot, axis=None, row=iteration.pivot.row, column=0)
            )
        if iteration.leaving_variable is not None:
            st.write(f"Saliente: {iteration.leaving_variable}. {iteration.leaving_reason}")
        elif iteration.leaving_reason:
            st.write(iteration.leaving_reason)
        if iteration.pivot:
            pivot = iteration.pivot
            st.write(
                f"Pivote: fila {pivot.row + 1}, columna {standard.column_names[pivot.column]}, "
                f"valor {number(pivot.value)} (celda resaltada)."
            )


def render_steps(problem: LPProblem, solution: Solution | None, step_mode: bool) -> None:
    """Reservar forma estándar e iteraciones para el modo paso a paso."""
    if not step_mode:
        st.info("Seleccione Paso a paso para ver la forma estándar y las iteraciones.")
        return
    st.subheader("Forma estándar")
    try:
        standard = solution.standard_form if solution else None
        standard = standard or to_standard_form(problem)
        st.table(
            [
                {"Columna": name, "Tipo": kind, "Costo": number(cost)}
                for name, kind, cost in zip(
                    standard.column_names, standard.column_types, standard.c, strict=True
                )
            ]
        )
        for message in standard.transformations:
            for row in problem.constraints:
                if row.rhs < 0:
                    message = message.replace(
                        f"({row.rhs}): se multiplicó", f"({number(row.rhs)}): se multiplicó"
                    )
            st.write(message)
        st.table(
            pd.DataFrame(
                [
                    [number(value) for value in row] + [number(rhs)]
                    for row, rhs in zip(standard.a, standard.b, strict=True)
                ],
                index=[row.name for row in problem.constraints],
                columns=[*standard.column_names, "Lado derecho"],
            )
        )
        st.write("Base inicial: " + ", ".join(standard.column_names[j] for j in standard.basis))
    except NotImplementedError:
        st.info("Pendiente de implementar: forma estándar")
        return
    except Exception:
        st.error("No se pudo mostrar la forma estándar. Revise el módulo y vuelva a intentar.")
        return
    if solution is None:
        st.info("Las iteraciones estarán disponibles al resolver con un método implementado.")
        return
    try:
        for iteration in solution.iterations:
            render_iteration(problem, standard, iteration)
    except Exception:
        st.error("No se pudieron mostrar las iteraciones. Revise el módulo y vuelva a intentar.")


def space_graph_labels(figure: go.Figure, result: GraphicalResult) -> None:
    """Separar rótulos en píxeles aproximados sin mover puntos ni cambiar la escala."""
    bounds = tuple(map(float, result.drawing_bounds))
    width, height = 870, 395
    ratio = bounds[0] / bounds[1]
    if 0.25 <= ratio <= 4:
        unit = min(width / bounds[0], height / bounds[1])
        width, height = bounds[0] * unit, bounds[1] * unit
    occupied = []
    # Las coordenadas tienen prioridad; después se acomodan las rectas e isoutilidad.
    annotations = sorted(figure.layout.annotations, key=lambda a: not a.text.startswith("("))
    for label in annotations:
        if label.showarrow:
            continue
        x = float(label.x) / bounds[0] * width + (label.xshift or 0)
        y = float(label.y) / bounds[1] * height
        text_width = len(label.text) * 6.5
        left = (
            x
            if label.xanchor == "left"
            else x - text_width
            if label.xanchor == "right"
            else x - text_width / 2
        )
        for shift in (label.yshift or 0, 28, 48, 68, 88, -28, -48, -68):
            bottom = y + shift - (0 if label.yanchor == "bottom" else 9)
            box = (left, bottom, left + text_width, bottom + 18)
            collision = any(
                box[0] < other[2] + 4
                and box[2] > other[0] - 4
                and box[1] < other[3] + 4
                and box[3] > other[1] - 4
                for other in occupied
            )
            if not collision and 0 <= bottom <= height - 18:
                if shift != (label.yshift or 0):
                    # Un rótulo desplazado conserva una guía hacia su punto o recta.
                    label.update(
                        showarrow=True,
                        arrowhead=0,
                        arrowwidth=1,
                        arrowcolor="gray",
                        ax=label.xshift or 0,
                        ay=-shift,
                        xshift=0,
                        yshift=0,
                    )
                else:
                    label.yshift = shift
                occupied.append(box)
                break


def render_graph(result: GraphicalResult, problem: LPProblem) -> None:
    """Dibujar el recorte calculado, conservando rectas incluso con región vacía."""
    if not result.applicable:
        st.info(result.reason)
        return
    names = problem.variable_names
    st.info(result.reason)
    if result.objective_value is not None:
        st.write(f"Óptimo gráfico: Z = {number(result.objective_value)}")
    figure = go.Figure()
    polygon = result.feasible_polygon
    if polygon:
        closed = (*polygon, polygon[0]) if len(polygon) > 2 else polygon
        figure.add_trace(
            go.Scatter(
                x=[float(p[0]) for p in closed],
                y=[float(p[1]) for p in closed],
                fill="toself" if len(polygon) > 2 else None,
                mode="lines+markers" if len(polygon) < 3 else "lines",
                name="Región factible",
                line={"width": 0 if result.bounded is False else 5 if len(polygon) < 3 else 2},
                fillcolor="rgba(99,110,250,0.2)",
            )
        )
        if result.bounded is False:
            for first, last in zip(closed, closed[1:], strict=False):
                on_box = any(
                    first[i] == last[i] and first[i] in (0, result.drawing_bounds[i])
                    for i in (0, 1)
                )
                figure.add_trace(
                    go.Scatter(
                        x=[float(first[0]), float(last[0])],
                        y=[float(first[1]), float(last[1])],
                        mode="lines",
                        name="Borde del recorte" if on_box else "Frontera factible",
                        line={
                            "color": "gray" if on_box else "#636efa",
                            "dash": "dot" if on_box else "solid",
                            "width": 2,
                        },
                        showlegend=False,
                    )
                )
    lines = result.lines + ((result.objective_line,) if result.objective_line else ())
    label_positions = []
    for index, line in enumerate(lines):
        objective = line is result.objective_line
        label = line.label
        if objective:
            label = f"Isoutilidad: Z = {number(line.rhs)}"
        else:
            mode = "fraction" if st.session_state["format"] == "Fracciones" else "decimal"
            expression = format_expression(
                line.coefficients, names, mode, st.session_state["decimals"]
            )
            row = problem.constraints[index]
            relation = {"<=": "≤", ">=": "≥", "=": "="}[row.relation]
            label = f"{row.name}: {expression} {relation} {number(line.rhs)}"
        figure.add_trace(
            go.Scatter(
                x=[float(p[0]) for p in line.points],
                y=[float(p[1]) for p in line.points],
                mode="lines+markers" if len(line.points) == 1 else "lines",
                name=label,
                line={"dash": "dot" if objective else "solid"},
            )
        )
        if line.points:
            first, last = line.points[0], line.points[-1]
            # Escoger un tramo alejado de vértices y rótulos ya colocados.
            candidates = [
                tuple(float(a + (b - a) * t / 5) for a, b in zip(first, last, strict=True))
                for t in (1, 2, 3, 4)
            ]
            occupied = [tuple(map(float, v.point)) for v in result.vertices] + label_positions
            bounds = tuple(map(float, result.drawing_bounds))
            position = max(
                candidates,
                key=lambda p: min(
                    (sum(((p[i] - q[i]) / bounds[i]) ** 2 for i in (0, 1)) for q in occupied),
                    default=1,
                ),
            )
            label_positions.append(position)
            figure.add_annotation(
                x=position[0],
                y=position[1],
                text=label,
                showarrow=False,
                yanchor="middle",
                yshift=-18 if objective or position[1] > bounds[1] * 5 / 6 else 14,
                xanchor="left"
                if position[0] < bounds[0] / 6
                else "right"
                if position[0] > bounds[0] * 5 / 6
                else "center",
                font={"color": "#172554", "size": 12},
                bgcolor="rgba(255,255,255,0.8)",
            )
    if result.vertices:
        figure.add_trace(
            go.Scatter(
                x=[float(v.point[0]) for v in result.vertices],
                y=[float(v.point[1]) for v in result.vertices],
                mode="markers",
                name="Vértices",
            )
        )
        for vertex in result.vertices:
            figure.add_annotation(
                x=float(vertex.point[0]),
                y=float(vertex.point[1]),
                text=f"({number(vertex.point[0])}, {number(vertex.point[1])}), "
                f"Z={number(vertex.objective_value)}",
                showarrow=False,
                xanchor="left" if vertex.point[0] == 0 else "center",
                yanchor="bottom",
                xshift=5 if vertex.point[0] == 0 else 0,
                yshift=8,
                font={"color": "#111827", "size": 12},
                bgcolor="rgba(255,255,255,0.85)",
            )
    if result.optimal_points:
        figure.add_trace(
            go.Scatter(
                x=[float(p[0]) for p in result.optimal_points],
                y=[float(p[1]) for p in result.optimal_points],
                mode="lines+markers",
                marker={"size": 12},
                line={"width": 6},
                name="Óptimo",
            )
        )
    for points in result.optimal_ray_segments:
        figure.add_trace(
            go.Scatter(
                x=[float(p[0]) for p in points],
                y=[float(p[1]) for p in points],
                mode="lines",
                line={"width": 6},
                name="Rayo óptimo (recorte)",
            )
        )
    if result.improvement_segment:
        first, last = result.improvement_segment
        direction = result.improving_direction
        figure.add_annotation(
            x=float(first[0] + (last[0] - first[0]) * 9 / 10),
            y=float(first[1] + (last[1] - first[1]) * 9 / 10),
            ax=float(first[0] + (last[0] - first[0]) / 3),
            ay=float(first[1] + (last[1] - first[1]) / 3),
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            showarrow=True,
            arrowhead=2,
            arrowwidth=3,
            arrowcolor="#9f1239",
            font={"color": "#9f1239", "size": 13},
            bgcolor="rgba(255,255,255,0.9)",
            text=f"Mejora ilimitada: ({number(direction[0])}, {number(direction[1])})",
        )
    space_graph_labels(figure, result)
    figure.update_layout(
        xaxis_title=names[0],
        yaxis_title=names[1],
        height=560,
        margin={"l": 60, "r": 40, "t": 35, "b": 130},
        legend={"orientation": "h", "y": -0.25, "x": 0},
    )
    figure.update_xaxes(range=[0, float(result.drawing_bounds[0])], constrain="domain")
    figure.update_yaxes(range=[0, float(result.drawing_bounds[1])], constrain="domain")
    ratio = result.drawing_bounds[0] / result.drawing_bounds[1]
    if Fraction(1, 4) <= ratio <= 4:
        figure.update_yaxes(scaleanchor="x", scaleratio=1)
    else:
        st.info("Los ejes tienen escalas distintas: direcciones y pendientes se ven deformadas")
    st.plotly_chart(figure, width="stretch")
    if result.bounded is False:
        for direction in result.recession_directions:
            st.info(
                "La región factible continúa sin límite en la dirección "
                f"({number(direction[0])}, {number(direction[1])}); "
                "el recuadro solo limita el dibujo"
            )


def render_comparison(solutions: dict[str, Solution]) -> None:
    """Comparar estados por posición, conservando diferencias y secuencias desiguales."""
    big_m, revised = solutions["Gran M"], solutions["Simplex revisado"]
    rows = []
    for index, (left, right) in enumerate(zip_longest(big_m.iterations, revised.iterations)):
        row = {"Iteración": index}
        for label, solution, state in (("Gran M", big_m, left), ("Revisado", revised, right)):
            row.update(
                {
                    f"Base {label}": ", ".join(
                        solution.standard_form.column_names[j] for j in state.basis
                    )
                    if state
                    else "—",
                    f"Entrante {label}": state.entering_variable or "—" if state else "—",
                    f"Saliente {label}": state.leaving_variable or "—" if state else "—",
                    f"Z {label}": number(state.objective_value)
                    if state and state.objective_value is not None
                    else "—",
                }
            )
        row["Base coincide"] = "Sí" if left and right and left.basis == right.basis else "No"
        rows.append(row)
    st.table(rows)
    st.write(
        f"Estados registrados: Gran M {len(big_m.iterations)}; revisado {len(revised.iterations)}. "
        f"Pivotes: Gran M {sum(i.pivot is not None for i in big_m.iterations)}; "
        f"revisado {sum(i.pivot is not None for i in revised.iterations)}."
    )
    if big_m.status == revised.status == Status.OPTIMAL:
        st.write(
            "Misma solución: "
            + ("Sí" if big_m.values == revised.values else "No")
            + ". Mismo Z: "
            + ("Sí" if big_m.objective_value == revised.objective_value else "No")
            + "."
        )
    else:
        st.write(
            "Mismo estado: "
            + ("Sí" if big_m.status == revised.status else "No")
            + ". Sin solución óptima ni Z finito para comparar."
        )
    st.caption(
        "Por iteración, el tablero actualiza m × (n + m + 1) números como referencia "
        "para filas ≤; con excesos y artificiales puede tener más columnas. "
        "El revisado mantiene B⁻¹ de m × m y calcula x_B, y, r y la columna d necesaria."
    )


def render_pdf_download(problem: LPProblem, solution: Solution, label: str, key: str) -> None:
    """Ofrecer bytes de la evidencia disponible y comunicar fallos sin traceback."""
    try:
        mode = "fraction" if st.session_state["format"] == "Fracciones" else "decimal"
        data = export_steps_pdf(problem, solution, mode, st.session_state["decimals"])
        st.download_button(
            label,
            data=data,
            file_name=f"pasos_{solution.method}.pdf",
            mime="application/pdf",
            key=key,
            on_click="ignore",
        )
    except NotImplementedError:
        st.info("Pendiente de implementar: exportación PDF")
    except Exception:
        st.error("No se pudo generar el PDF. Revise el módulo y vuelva a intentar.")


def render_results(problem: LPProblem, step_mode: bool) -> None:
    """Mantener cada sección utilizable aunque otros módulos estén pendientes."""
    solutions = st.session_state["solutions"]
    solution = next(iter(solutions.values()), None)
    tabs = st.tabs(
        ["Resultado", "Paso a paso", "Método gráfico", "Sensibilidad", "Comparar métodos"]
    )
    with tabs[0]:
        for label, message in st.session_state["notices"].items():
            st.info(f"{label}: {message}")
        for label, item in solutions.items():
            st.subheader(label)
            render_solution(problem, item)
        if not solutions and not st.session_state["notices"]:
            st.info("Pulse Resolver para ejecutar el método seleccionado.")
    with tabs[1]:
        render_steps(problem, solution, step_mode)
        if solution is not None:
            render_pdf_download(problem, solution, "Exportar paso a paso a PDF", "steps_pdf")
        else:
            st.info("Resuelva el problema para exportar el paso a paso a PDF.")
    with tabs[2]:
        if len(problem.variable_names) != 2:
            st.info("El método gráfico no aplica: requiere exactamente dos variables.")
        else:
            try:
                render_graph(graphical_method(problem), problem)
            except NotImplementedError:
                st.info("Pendiente de implementar: método gráfico")
            except Exception:
                st.error("No se pudo mostrar el gráfico. Revise el módulo y vuelva a intentar.")
    with tabs[3]:
        if solution is None:
            st.info(
                "Resuelva el problema para analizar sensibilidad; requiere una solución óptima."
            )
        elif solution.status != Status.OPTIMAL:
            st.info("El análisis de sensibilidad requiere una solución óptima.")
        else:
            try:
                report = sensitivity_analysis(problem, solution)
                mode = "fraction" if st.session_state["format"] == "Fracciones" else "decimal"
                interpretations = sensitivity_interpretations(
                    problem, report, solution, mode, st.session_state["decimals"]
                )
                for warning in report.warnings:
                    st.warning(warning)
                for label, key_label, value_label, values, prefix in (
                    (
                        "Precios sombra",
                        "Restricción",
                        "Precio sombra ∂Z*/∂b",
                        report.shadow_prices,
                        "b",
                    ),
                    ("Costos reducidos", "Variable", "cⱼ − zⱼ", report.reduced_costs, "r"),
                ):
                    st.write(label)
                    st.table(
                        [
                            {key_label: name, value_label: number(value)}
                            for name, value in values.items()
                        ]
                    )
                    if prefix == "r":
                        for name in values:
                            st.write(interpretations[f"{prefix}:{name}"])
                for label, key_label, ranges, prefix in (
                    ("Rangos de coeficientes", "Variable", report.objective_ranges, "c"),
                    ("Rangos de lados derechos", "Restricción", report.rhs_ranges, "b"),
                ):
                    st.write(label)
                    names = (
                        [row.name for row in problem.constraints] if prefix == "b" else list(ranges)
                    )
                    unavailable = "No disponible (fila redundante)"
                    st.table(
                        [
                            {
                                key_label: name,
                                "Inferior": unavailable
                                if name not in ranges
                                else number(ranges[name][0])
                                if ranges[name][0] is not None
                                else "−∞",
                                "Superior": unavailable
                                if name not in ranges
                                else number(ranges[name][1])
                                if ranges[name][1] is not None
                                else "+∞",
                            }
                            for name in names
                        ]
                    )
                    for name in names:
                        st.write(interpretations[f"{prefix}:{name}"])
            except NotImplementedError:
                st.info("Pendiente de implementar: sensibilidad")
            except Exception:
                st.error(
                    "No se pudo mostrar la sensibilidad. Revise el módulo y vuelva a intentar."
                )
    with tabs[4]:
        if len(solutions) < 2:
            st.info("Seleccione Comparar ambos y pulse Resolver para comparar las iteraciones.")
        else:
            render_comparison(solutions)
            st.table(
                [
                    {
                        "Método": label,
                        "Estado": item.status.value,
                        "Z": number(item.objective_value)
                        if item.objective_value is not None
                        else "—",
                        "Iteraciones": len(item.iterations),
                    }
                    for label, item in solutions.items()
                ]
            )
            for label, item in solutions.items():
                st.subheader(label)
                render_steps(problem, item, step_mode)
                render_pdf_download(
                    problem, item, f"Exportar PDF: {label}", f"compare_pdf_{item.method}"
                )


def main() -> None:
    """Construir editores, navegación y avisos de módulos pendientes."""
    st.set_page_config(page_title="Programación lineal", layout="wide")
    if "raw" not in st.session_state:
        replace_problem(load_problem(FIXTURES / "ejemplo_1.json"))
    st.title("Aplicación de Programación Lineal")
    st.caption(
        "Todas las variables son no negativas. Ingrese enteros, decimales o fracciones como 2/5."
    )
    with st.sidebar:
        st.selectbox(
            "Sentido", ["max", "min"], format_func=str.upper, key="sense", on_change=change_sense
        )
        method = st.selectbox("Método", [*METHODS, "Comparar ambos"])
        mode = st.radio("Modo", ["Directo", "Paso a paso"])
        st.selectbox("Formato numérico", ["Fracciones", "Decimales"], key="format")
        st.number_input("Número de decimales", min_value=0, max_value=12, value=4, key="decimals")
        st.selectbox(
            "Ejemplo", [path.name for path in sorted(FIXTURES.glob("*.json"))], key="example"
        )
        st.button("Cargar ejemplo", on_click=load_example)
        st.file_uploader("Cargar JSON", type=["json"], key="upload", on_change=upload_problem)
    if message := st.session_state.pop("load_error", None):
        st.error(message)
    raw = st.session_state["raw"]
    for column, label, kind, change in zip(
        st.columns(4),
        ("Agregar variable", "Quitar variable", "Agregar restricción", "Quitar restricción"),
        ("variable", "variable", "constraint", "constraint"),
        (1, -1, 1, -1),
        strict=True,
    ):
        size = len(raw["variables"] if kind == "variable" else raw["restricciones"])
        column.button(
            label, on_click=resize, args=(kind, change), disabled=change < 0 and size <= 1
        )
    identifiers = [f"x{i + 1}" for i in range(len(raw["variables"]))]
    config = {
        key: st.column_config.TextColumn(name)
        for key, name in zip(identifiers, raw["variables"], strict=True)
    }
    revision = st.session_state["revision"]
    objective_key, constraints_key = f"objective_{revision}", f"constraints_{revision}"
    st.subheader("Función objetivo")
    st.data_editor(
        [dict(zip(identifiers, raw["objetivo"], strict=True))],
        key=objective_key,
        column_config=config,
        hide_index=True,
        on_change=apply_edits,
        args=(objective_key, True),
    )
    st.subheader("Restricciones")
    rows = [
        {
            "nombre": row["nombre"],
            **dict(zip(identifiers, row["coeficientes"], strict=True)),
            "signo": row["signo"],
            "rhs": row["rhs"],
        }
        for row in raw["restricciones"]
    ]
    st.data_editor(
        rows,
        key=constraints_key,
        hide_index=True,
        disabled=["nombre"],
        column_config={
            **config,
            "nombre": "Restricción",
            "signo": st.column_config.SelectboxColumn("Signo", options=["<=", ">=", "="]),
            "rhs": st.column_config.TextColumn("Lado derecho"),
        },
        on_change=apply_edits,
        args=(constraints_key, False),
    )
    problem, issues = validate(raw)
    st.sidebar.download_button(
        "Guardar JSON",
        data=save_problem(problem) if problem else "",
        file_name="problema.json",
        mime="application/json",
        disabled=problem is None,
    )
    if st.button("Resolver", type="primary"):
        invalidate()
        if issues:
            for issue in issues:
                st.error(f"{issue.location}: {issue.message}")
        elif problem is not None:
            st.session_state["validated"] = problem
            selected = METHODS if method == "Comparar ambos" else {method: METHODS[method]}
            for label, solver in selected.items():
                try:
                    st.session_state["solutions"][label] = solver(problem)
                except NotImplementedError:
                    st.session_state["notices"][label] = f"Pendiente de implementar: {label}"
                except ValueError as error:
                    st.session_state["notices"][label] = str(error)
                except Exception:
                    st.session_state["notices"][label] = (
                        "No se pudo resolver. Revise el método y vuelva a intentar."
                    )
    if problem is not None:
        with st.expander("Resumen del problema validado", expanded=True):
            render_summary(problem)
        render_results(problem, mode == "Paso a paso")
    elif not issues:
        st.info("Ingrese un problema para comenzar.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        st.error("No se pudo completar la operación. Revise los datos o recargue la aplicación.")
