"""Interfaz base; solo los métodos del equipo podrán producir soluciones."""

from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from plapp.big_m import solve_big_m
from plapp.formatting import format_expression, format_number
from plapp.graphical import graphical_method
from plapp.io_json import load_problem, problem_to_dict, save_problem
from plapp.model import LPProblem, validate
from plapp.result import GraphicalResult, Solution, Status
from plapp.revised_simplex import solve_revised
from plapp.sensitivity import sensitivity_analysis
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
        st.write(f"{row.name}: {expression} {row.relation} {number(row.rhs)}")
    st.write(", ".join(problem.variable_names) + " ≥ 0")


def render_solution(solution: Solution) -> None:
    """Presentar únicamente resultados calculados por el método propio."""
    st.write(solution.message)
    if solution.status == Status.OPTIMAL:
        st.table(
            [{"Variable": name, "Valor": number(value)} for name, value in solution.values.items()]
        )
        if solution.objective_value is not None:
            st.write(f"Z = {number(solution.objective_value)}")
        st.table(
            [
                {"Restricción": name, "Holgura/exceso": number(value)}
                for name, value in solution.slacks.items()
            ]
        )
        if solution.multiple_optima:
            st.info("Hay soluciones óptimas múltiples.")
        if solution.degenerate:
            st.info("Se detectó degeneración.")


def render_steps(problem: LPProblem, solution: Solution | None, step_mode: bool) -> None:
    """Preparar la vista de forma estándar y, en modo paso a paso, las iteraciones."""
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
            st.write(message)
        st.table(
            [
                {
                    **{
                        name: number(value)
                        for name, value in zip(standard.column_names, row, strict=True)
                    },
                    "Lado derecho": number(rhs),
                }
                for row, rhs in zip(standard.a, standard.b, strict=True)
            ]
        )
        st.write("Base inicial:", [standard.column_names[index] for index in standard.basis])
    except NotImplementedError:
        st.info("Pendiente de implementar: forma estándar")
    except Exception:
        st.error("No se pudo mostrar la forma estándar. Revise el módulo y vuelva a intentar.")
    if not step_mode:
        st.info(
            "Seleccione Paso a paso para ver las iteraciones cuando el método esté implementado."
        )
        return
    if solution is None:
        st.info("Pendiente de implementar: iteraciones del método")
        return
    for iteration in solution.iterations:
        with st.expander(f"Iteración {iteration.number}", expanded=True):
            st.write("Base (índices desde cero):", iteration.basis)
            st.write("Entrante:", iteration.entering_variable, iteration.entering_reason)
            st.table(
                [
                    {
                        "Fila": row.row + 1,
                        "Básica": row.basic_variable,
                        "Lado derecho": number(row.rhs),
                        "Coeficiente": number(row.coefficient),
                        "Razón": number(row.ratio)
                        if row.ratio is not None
                        else row.exclusion_reason,
                    }
                    for row in iteration.ratios
                ]
            )
            st.write("Saliente:", iteration.leaving_variable, iteration.leaving_reason)
            if iteration.pivot:
                pivot = iteration.pivot
                st.write(
                    f"Pivote: fila {pivot.row + 1}, columna {pivot.column + 1}, "
                    f"{number(pivot.value)}"
                )
            for label, matrix in (("Tablero", iteration.tableau), ("B⁻¹", iteration.b_inverse)):
                if matrix:
                    st.write(label)
                    st.table([[number(value) for value in row] for row in matrix])
            if iteration.reduced_costs:
                st.write("Costos reducidos:", [number(value) for value in iteration.reduced_costs])


def render_graph(result: GraphicalResult, names: tuple[str, ...]) -> None:
    """Dibujar geometría ya calculada por graphical_method con Plotly."""
    if not result.applicable or result.empty:
        st.info(result.reason or "La región factible está vacía.")
        return
    figure = go.Figure()
    if result.feasible_polygon:
        figure.add_trace(
            go.Scatter(
                x=[float(p[0]) for p in result.feasible_polygon],
                y=[float(p[1]) for p in result.feasible_polygon],
                fill="toself",
                mode="lines",
                name="Región factible",
            )
        )
    lines = result.lines + ((result.objective_line,) if result.objective_line else ())
    for line in lines:
        figure.add_trace(
            go.Scatter(
                x=[float(p[0]) for p in line.points],
                y=[float(p[1]) for p in line.points],
                mode="lines",
                name=line.label,
            )
        )
    if result.vertices:
        figure.add_trace(
            go.Scatter(
                x=[float(v.point[0]) for v in result.vertices],
                y=[float(v.point[1]) for v in result.vertices],
                mode="markers+text",
                text=[
                    f"({number(v.point[0])}, {number(v.point[1])}), Z={number(v.objective_value)}"
                    for v in result.vertices
                ],
                textposition="top center",
                name="Vértices",
            )
        )
    if result.optimal_points:
        figure.add_trace(
            go.Scatter(
                x=[float(p[0]) for p in result.optimal_points],
                y=[float(p[1]) for p in result.optimal_points],
                mode="markers",
                marker={"size": 12},
                name="Óptimo",
            )
        )
    figure.update_layout(xaxis_title=names[0], yaxis_title=names[1])
    figure.update_yaxes(scaleanchor="x", scaleratio=1)
    st.plotly_chart(figure, width="stretch")
    if result.bounded is False:
        st.info("Región no acotada; se muestra un recorte para visualizarla.")


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
            render_solution(item)
        if not solutions and not st.session_state["notices"]:
            st.info("Pulse Resolver para ejecutar el método seleccionado.")
    with tabs[1]:
        render_steps(problem, solution, step_mode)
        st.button(
            "Exportar paso a paso a PDF",
            disabled=True,
            help="Pendiente de implementar: exportación PDF",
        )
        st.caption("Pendiente de implementar: exportación PDF")
    with tabs[2]:
        if len(problem.variable_names) != 2:
            st.info("El método gráfico no aplica: requiere exactamente dos variables.")
        else:
            try:
                render_graph(graphical_method(problem), problem.variable_names)
            except NotImplementedError:
                st.info("Pendiente de implementar: método gráfico")
            except Exception:
                st.error("No se pudo mostrar el gráfico. Revise el módulo y vuelva a intentar.")
    with tabs[3]:
        if solution is None:
            st.info("Pendiente de implementar: sensibilidad; requiere una solución óptima.")
        elif solution.status != Status.OPTIMAL:
            st.info("El análisis de sensibilidad requiere una solución óptima.")
        else:
            try:
                report = sensitivity_analysis(problem, solution)
                for label, values in (
                    ("Precios sombra", report.shadow_prices),
                    ("Costos reducidos", report.reduced_costs),
                ):
                    st.write(label)
                    st.table(
                        [{"Nombre": name, "Valor": number(value)} for name, value in values.items()]
                    )
                for label, ranges in (
                    ("Rangos de coeficientes", report.objective_ranges),
                    ("Rangos de lados derechos", report.rhs_ranges),
                ):
                    st.write(label)
                    st.table(
                        [
                            {
                                "Nombre": name,
                                "Inferior": number(low) if low is not None else "−∞",
                                "Superior": number(high) if high is not None else "+∞",
                            }
                            for name, (low, high) in ranges.items()
                        ]
                    )
                for name, interpretation in report.interpretations.items():
                    st.write(f"{name}: {interpretation}")
            except NotImplementedError:
                st.info("Pendiente de implementar: sensibilidad")
            except Exception:
                st.error(
                    "No se pudo mostrar la sensibilidad. Revise el módulo y vuelva a intentar."
                )
    with tabs[4]:
        if len(solutions) < 2:
            st.info("Pendiente de implementar: comparación de ambos métodos")
        else:
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
                render_steps(problem, item, True)


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
