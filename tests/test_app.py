"""Pruebas de navegación, estado y mensajes usando AppTest de Streamlit."""

from copy import deepcopy
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app import streamlit_app

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


def test_navigation_and_stubs(app):
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
    assert any("Pendiente de implementar: Gran M" in item.value for item in app.info)
    assert button(app, "Exportar paso a paso a PDF").disabled


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
    assert len(app.session_state["notices"]) == 2
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
