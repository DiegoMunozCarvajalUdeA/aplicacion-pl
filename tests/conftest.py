"""Fixtures comunes; conservar los valores esperados fuera del código productivo."""

import json
from pathlib import Path

import pytest

from plapp.io_json import load_problem

PROBLEMS = Path(__file__).parent / "fixtures/problems"
PROBLEM_FILES = sorted(PROBLEMS.glob("*.json"))


@pytest.fixture
def example_one():
    """Problema bidimensional con restricción redundante."""
    return load_problem(PROBLEMS / "ejemplo_1.json")


@pytest.fixture(params=PROBLEM_FILES, ids=lambda path: path.stem)
def fixture_problem(request):
    """Cargar modelo y resultado esperado para cada problema."""
    path = request.param
    return load_problem(path), json.loads(path.read_text(encoding="utf-8"))["esperado"]
