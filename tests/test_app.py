"""Pruebas de navegación, estado y mensajes usando AppTest de Streamlit."""

from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app import streamlit_app
from plapp.big_m import solve_big_m
from plapp.formatting import format_number
from plapp.io_json import problem_to_dict
from plapp.model import Constraint, LPProblem

APP = Path(__file__).resolve().parents[1] / "app/streamlit_app.py"


def button(app, label):
    """Localizar un botón por su texto visible."""
    return next(item for item in app.button if item.label == label)


def selectbox(app, label):
    """Localizar una selección por su texto visible."""
    return next(item for item in app.selectbox if item.label == label)


@pytest.fixture
def app():
    """Iniciar una sesión aislada con tiempo para las primeras importaciones."""
    result = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not result.exception and not result.error
    return result


def test_navigation_and_pending_modules(app):
    assert [tab.label for tab in app.tabs] == [
        "Resultado",
        "Paso a paso",
        "Método gráfico",
        "Sensibilidad",
        "Comparar métodos",
    ]
    assert any(item.label == "Resumen del problema validado" for item in app.expander)
    button(app, "Resolver").click().run()
    assert not app.exception and not app.error
    assert any("Z = 3380" in item.value for item in app.markdown)
    assert button(app, "Exportar paso a paso a PDF").disabled
    assert any("Pendiente de implementar: método gráfico" in item.value for item in app.info)


def test_resize_preserves_cells(app):
    original = deepcopy(app.session_state["raw"])
    button(app, "Agregar variable").click().run()
    raw = app.session_state["raw"]
    assert raw["objetivo"][:-1] == original["objetivo"]
    assert raw["restricciones"][0]["coeficientes"] == ["2", "1", "0"]
    original_rows = deepcopy(raw["restricciones"])
    button(app, "Agregar restricción").click().run()
    assert app.session_state["raw"]["restricciones"][:-1] == original_rows
    button(app, "Quitar restricción").click().run()
    button(app, "Quitar variable").click().run()
    assert app.session_state["raw"] == original
    assert not app.exception and not app.error


def test_minimum_dimensions(app):
    button(app, "Quitar variable").click().run()
    button(app, "Quitar restricción").click().run()
    button(app, "Quitar restricción").click().run()
    assert button(app, "Quitar variable").disabled
    assert button(app, "Quitar restricción").disabled


def test_load_min_and_three_variables(app):
    selectbox(app, "Ejemplo").select("ejemplo_2.json").run()
    button(app, "Cargar ejemplo").click().run()
    assert selectbox(app, "Sentido").value == "min"
    assert app.session_state["raw"]["restricciones"][2]["rhs"] == "-4"
    selectbox(app, "Ejemplo").select("ejemplo_3.json").run()
    button(app, "Cargar ejemplo").click().run()
    assert len(app.session_state["raw"]["variables"]) == 3
    assert any("no aplica" in item.value for item in app.info)
    assert not app.exception and not app.error


def test_both_methods_and_formats(app):
    selectbox(app, "Método").select("Comparar ambos").run()
    app.radio[0].set_value("Paso a paso").run()
    selectbox(app, "Formato numérico").select("Decimales").run()
    button(app, "Resolver").click().run()
    assert len(app.session_state["notices"]) == 1
    assert any("Simplex revisado" in item.value for item in app.info)
    assert not app.exception and not app.error


def test_validation_locations(app):
    raw = deepcopy(app.session_state["raw"])
    raw["objetivo"][0] = ""
    raw["restricciones"][1]["rhs"] = "abc"
    app.session_state["raw"] = raw
    app.session_state["revision"] += 1
    app.run()
    button(app, "Resolver").click().run()
    assert any("objetivo, x1" in item.value for item in app.error)
    assert any("lado derecho de R2" in item.value for item in app.error)
    assert not app.exception


def test_unexpected_solver_error(app, monkeypatch):
    def broken_solver(problem):
        raise RuntimeError("Detalle interno que no debe mostrarse")

    monkeypatch.setattr("plapp.big_m.solve_big_m", broken_solver)
    app.run()
    button(app, "Resolver").click().run()
    assert not app.exception
    assert any("No se pudo resolver" in item.value for item in app.info)
    assert all("Detalle interno" not in item.value for item in app.info)


def test_solver_limit_message(app, monkeypatch):
    message = "Se alcanzó el límite de 1000 iteraciones de Gran M; revise el problema."

    def limited_solver(problem):
        raise ValueError(message)

    monkeypatch.setattr("plapp.big_m.solve_big_m", limited_solver)
    app.run()
    button(app, "Resolver").click().run()
    assert not app.exception and not app.error
    assert any(message in item.value for item in app.info)


def test_editor_callback_and_resize(monkeypatch):
    state = {
        "raw": {
            "variables": ["x1", "x2"],
            "objetivo": ["1", "2"],
            "restricciones": [
                {"nombre": "R1", "coeficientes": ["3", "4"], "signo": "<=", "rhs": "5"}
            ],
        },
        "revision": 0,
        "objective_0": {"edited_rows": {0: {"x1": "2/5"}}},
        "constraints_0": {"edited_rows": {0: {"x2": "2,5", "signo": ">=", "rhs": "-4"}}},
    }
    monkeypatch.setattr(streamlit_app.st, "session_state", state)
    streamlit_app.apply_edits("objective_0", True)
    streamlit_app.apply_edits("constraints_0", False)
    streamlit_app.resize("variable", 1)
    assert state["raw"]["objetivo"] == ["2/5", "2", "0"]
    assert state["raw"]["restricciones"][0] == {
        "nombre": "R1",
        "coeficientes": ["3", "2,5", "0"],
        "signo": ">=",
        "rhs": "-4",
    }
    assert state["solutions"] == {} and "validated" not in state


def test_invalid_upload_preserves_problem(monkeypatch, example_one):
    class Upload:
        def getvalue(self):
            return b"{no es JSON}"

    state = {"revision": 0}
    monkeypatch.setattr(streamlit_app.st, "session_state", state)
    streamlit_app.replace_problem(example_one)
    original = deepcopy(state["raw"])
    state["upload"] = Upload()
    streamlit_app.upload_problem()
    assert state["raw"] == original
    assert "JSON válido" in state["load_error"]


@pytest.mark.parametrize("example", [1, 2, 3, 4, 5, 6, 7])
@pytest.mark.parametrize("mode", ["Directo", "Paso a paso"])
@pytest.mark.parametrize("number_format", ["Fracciones", "Decimales"])
def test_solved_examples_in_both_modes_and_formats(app, example, mode, number_format):
    selectbox(app, "Ejemplo").select(f"ejemplo_{example}.json").run()
    button(app, "Cargar ejemplo").click().run()
    app.radio[0].set_value(mode).run()
    selectbox(app, "Formato numérico").select(number_format).run()
    button(app, "Resolver").click().run()
    assert not app.exception and not app.error
    text = "\n".join(item.value for item in [*app.markdown, *app.info])
    numeric_mode = "fraction" if number_format == "Fracciones" else "decimal"
    expected = {1: 3380, 2: Fraction(17, 5), 3: 1350, 6: 10, 7: 18}
    if example in expected:
        assert "Z = " + format_number(Fraction(expected[example]), numeric_mode) in text
    elif example == 4:
        assert "no tiene solución factible" in text
    else:
        assert "solución no acotada" in text
    if example == 6:
        endpoints = (
            "(0, 5/2) y (3, 1)"
            if numeric_mode == "fraction"
            else "(0.0000, 2.5000) y (3.0000, 1.0000)"
        )
        assert "segmento entre " + endpoints in text
        assert "Solución alterna 1" in text
    if example == 7:
        assert "degeneración" in text and "variables básicas en 0: x1" in text
    iterations = [e for e in app.expander if e.label.startswith("Iteración ")]
    tableaus = [table for table in app.table if "cⱼ − zⱼ" in table.value.index]
    standard_tables = [table.value for table in app.table if "Columna" in table.value.columns]
    if mode == "Directo":
        assert not iterations and not tableaus and not standard_tables
        return
    solution = app.session_state["solutions"]["Gran M"]
    assert len(iterations) == len(tableaus) == len(solution.iterations)
    assert len(standard_tables) == 1
    for element, iteration in zip(tableaus, solution.iterations, strict=True):
        table = element.value
        assert list(table.columns) == [*solution.standard_form.column_names, "Lado derecho"]
        assert list(table.index) == [
            *(solution.standard_form.column_names[j] for j in iteration.basis),
            "cⱼ − zⱼ",
        ]
        assert table.iloc[-1, -1] == format_number(iteration.objective_value, numeric_mode)
        if iteration.pivot is not None:
            styles = element.proto.arrow_data.styler.styles
            assert f"_row{iteration.pivot.row}_col{iteration.pivot.column}" in styles
            assert "background-color: #fef08a" in styles
    if example == 2:
        result_tables = [t.value for t in app.table if "Restricción" in t.value.columns]
        assert any(list(t["Tipo"]) == ["Igualdad", "Exceso", "Exceso"] for t in result_tables)
        assert "Canonización" in text and "restó M" in text


def test_format_change_preserves_exact_solution(app):
    selectbox(app, "Ejemplo").select("ejemplo_2.json").run()
    button(app, "Cargar ejemplo").click().run()
    button(app, "Resolver").click().run()
    original = app.session_state["solutions"]["Gran M"]
    selectbox(app, "Formato numérico").select("Decimales").run()
    assert any("Z = 3.4000" in item.value for item in app.markdown)
    assert app.session_state["solutions"]["Gran M"] == original
    assert original.values == {"x1": Fraction(2, 5), "x2": Fraction(9, 5)}


def test_revised_contract_presentation(app, monkeypatch, example_one):
    solution = solve_big_m(example_one)
    last = replace(solution.iterations[-1], tableau=None, b_inverse=solution.final_b_inverse)
    monkeypatch.setattr(
        "plapp.revised_simplex.solve_revised",
        lambda p: replace(solution, method="revised", iterations=(last,)),
    )
    selectbox(app, "Método").select("Simplex revisado").run()
    app.radio[0].set_value("Paso a paso").run()
    button(app, "Resolver").click().run()
    assert not app.exception and not app.error
    inverse_tables = [t.value for t in app.table if list(t.value.columns) == ["R1", "R2", "R3"]]
    assert len(inverse_tables) == 1
    assert list(inverse_tables[0].index) == ["x1", "x2", "s3"]
    assert inverse_tables[0].iloc[0, 0] == "3/5"
    assert any("cⱼ − zⱼ" in t.value.index for t in app.table)


def test_optimal_ray_presentation(app):
    original = LPProblem(
        (Fraction(1), Fraction(0)),
        (Constraint((Fraction(1), Fraction(0)), "<=", Fraction(1)),),
    )
    app.session_state["raw"] = problem_to_dict(original)
    app.session_state["revision"] += 1
    app.run()
    button(app, "Resolver").click().run()
    assert not app.exception and not app.error
    assert any("rayo desde (1, 0), con dirección (0, 1)" in item.value for item in app.markdown)


def test_decimal_transformation_and_fractional_result(app):
    original = LPProblem(
        (Fraction(1, 3),),
        (Constraint((Fraction(-1),), ">=", Fraction(-1, 2)),),
    )
    app.session_state["raw"] = problem_to_dict(original)
    app.session_state["revision"] += 1
    app.run()
    app.radio[0].set_value("Paso a paso").run()
    selectbox(app, "Formato numérico").select("Decimales").run()
    button(app, "Resolver").click().run()
    assert not app.exception and not app.error
    text = "\n".join(item.value for item in app.markdown)
    assert "lado derecho negativo (-0.5000)" in text
    assert "Z = 0.1667" in text and "(-1/2)" not in text
