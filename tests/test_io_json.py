"""Persistencia de los datos exactos y errores de archivo comprensibles."""

import json

import pytest

from plapp.io_json import load_problem, save_problem


def test_round_trip(fixture_problem, tmp_path):
    problem, _ = fixture_problem
    path = tmp_path / "problema.json"
    text = save_problem(problem, path)
    assert load_problem(path) == problem
    assert load_problem(text) == problem
    assert load_problem(text.encode()) == problem
    raw = json.loads(text)
    assert all(isinstance(value, str) for value in raw["objetivo"])
    assert "esperado" not in raw
    assert "fuente" not in raw


@pytest.mark.parametrize("text", ["{", "[]", "null", b"\xff", '{"objetivo": ["abc"]}'])
def test_invalid_json(text):
    with pytest.raises(ValueError):
        load_problem(text)


def test_missing_file(tmp_path):
    with pytest.raises(ValueError, match="No se pudo leer"):
        load_problem(tmp_path / "ausente.json")


def test_unwritable_destination(example_one, tmp_path):
    with pytest.raises(ValueError, match="No se pudo guardar"):
        save_problem(example_one, tmp_path)
