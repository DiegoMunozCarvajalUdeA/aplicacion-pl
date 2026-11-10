"""Trazas congeladas antes de extraer las reglas de Gran M."""

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from plapp.big_m import solve_big_m
from plapp.io_json import load_problem

TRACES = json.loads((Path(__file__).parent / "fixtures/big_m_traces.json").read_text())


@pytest.mark.parametrize("case", TRACES, ids=lambda case: case["case"])
def test_big_m_trace_unchanged(case):
    """Comparar incluso mensajes, notas, razones y números exactos del tablero."""
    solution = solve_big_m(load_problem(json.dumps(case["problem"])))
    actual = json.loads(json.dumps([asdict(i) for i in solution.iterations], default=str))
    assert len(actual) == len(case["iterations"])
    for state, expected in zip(actual, case["iterations"], strict=True):
        assert {key: state[key] for key in expected} == expected
    assert solution.status.value == case["status"]
    assert solution.message == case["message"]
    assert list(solution.notes) == case["notes"]
