"""Salida del verificador y detección de discrepancias del método propio."""

import json
from dataclasses import replace
from fractions import Fraction

from plapp.result import Solution, Status
from scripts import verify
from tests.conftest import PROBLEMS


def test_compare_solution(example_one):
    oracle = verify.verify_with_scipy(example_one)
    solution = Solution(
        "big_m",
        Status.OPTIMAL,
        "Solución óptima",
        values={"x1": Fraction(42), "x2": Fraction(16)},
        objective_value=Fraction(3380),
    )
    assert not verify.compare_solution(example_one, solution, oracle)
    assert verify.compare_solution(example_one, replace(solution, status=Status.INFEASIBLE), oracle)
    assert verify.compare_solution(
        example_one, replace(solution, objective_value=Fraction(0)), oracle
    )
    assert verify.compare_solution(example_one, replace(solution, values={}), oracle)
    assert verify.compare_solution(
        example_one, replace(solution, values={"x1": Fraction(-1), "x2": Fraction(0)}), oracle
    )


def test_cli_report(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["verify.py", str(PROBLEMS / "ejemplo_1.json")])
    assert verify.main() == 0
    output = capsys.readouterr().out
    for text in (
        "x1 = 42",
        "x2 = 16",
        "Z = 3380",
        "Precio sombra R1 = 14",
        "pendiente de implementar",
    ):
        assert text in output


def test_cli_json(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["verify.py", str(PROBLEMS / "ejemplo_2.json"), "--json"])
    assert verify.main() == 0
    output = json.loads(capsys.readouterr().out)
    assert output["status"] == "optimo"
    assert abs(output["objective_value"] - 3.4) < 1e-7


def test_cli_bad_file(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr("sys.argv", ["verify.py", str(tmp_path / "no-existe.json")])
    assert verify.main() == 1
    assert "Error de verificación" in capsys.readouterr().out


def test_cli_own_discrepancy(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["verify.py", str(PROBLEMS / "ejemplo_1.json")])
    monkeypatch.setattr(
        verify, "solve_big_m", lambda problem: Solution("big_m", Status.UNBOUNDED, "No acotada")
    )
    assert verify.main() == 1
    assert "estado propio no_acotado; SciPy optimo" in capsys.readouterr().out
