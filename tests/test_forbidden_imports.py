"""Impedir que librerías de optimización produzcan resultados en la aplicación."""

import ast
from pathlib import Path

import pytest

FORBIDDEN = {"scipy", "pulp", "ortools", "cvxpy", "pyomo", "highspy", "gurobipy", "cplex", "mip"}
ROOT = Path(__file__).resolve().parents[1]


def forbidden_imports(source: str) -> list[str]:
    """Detectar imports normales, relativos y cargas dinámicas con nombre literal."""
    found = []
    for node in ast.walk(ast.parse(source)):
        names = []
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""] + [alias.name for alias in node.names]
        elif isinstance(node, ast.Call):
            function = node.func
            dynamic = (isinstance(function, ast.Name) and function.id == "__import__") or (
                isinstance(function, ast.Attribute) and function.attr == "import_module"
            )
            if dynamic and node.args and isinstance(node.args[0], ast.Constant):
                names = [str(node.args[0].value)]
        found.extend(name for name in names if name.split(".")[0] in FORBIDDEN)
    return found


def test_no_optimization_imports():
    findings = []
    for folder in ("src", "app"):
        for path in (ROOT / folder).rglob("*.py"):
            for name in forbidden_imports(path.read_text(encoding="utf-8")):
                findings.append(f"{path.relative_to(ROOT)}: {name}")
    assert not findings, "Imports prohibidos: " + "; ".join(findings)


@pytest.mark.parametrize(
    "source",
    [
        "import scipy.optimize as opt",
        "from scipy import optimize",
        "import pulp",
        "from ortools.linear_solver import pywraplp",
        "from cvxpy import Problem",
        "import pyomo.environ",
        "__import__('scipy')",
        "importlib.import_module('pulp')",
    ],
)
def test_detector(source):
    assert forbidden_imports(source)
