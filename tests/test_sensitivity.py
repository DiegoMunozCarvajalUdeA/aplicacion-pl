"""Sensibilidad contra SciPy sobre una base óptima conocida y no degenerada."""

from fractions import Fraction

import pytest

from plapp.mvalue import MValue
from plapp.result import Solution, StandardForm, Status
from plapp.sensitivity import sensitivity_analysis
from scripts.verify import verify_with_scipy


@pytest.mark.xfail(raises=NotImplementedError, strict=False, reason="Sensibilidad pendiente")
def test_example_one_sensitivity(example_one):
    f = Fraction
    standard = StandardForm(
        ("x1", "x2", "s1", "s2", "s3"),
        ("original", "original", "holgura", "holgura", "holgura"),
        tuple(tuple(map(f, row)) for row in ((2, 1, 1, 0, 0), (1, 3, 0, 1, 0), (0, 1, 0, 0, 1))),
        (f(100), f(90), f(40)),
        tuple(MValue(f(value)) for value in (50, 80, 0, 0, 0)),
        (2, 3, 4),
        (),
    )
    solution = Solution(
        method="big_m",
        status=Status.OPTIMAL,
        message="Solución óptima",
        values={"x1": f(42), "x2": f(16)},
        objective_value=f(3380),
        slacks={"R1": f(0), "R2": f(0), "R3": f(24)},
        standard_form=standard,
        final_basis=(0, 1, 4),
        final_b_inverse=(
            (f(3, 5), f(-1, 5), f(0)),
            (f(-1, 5), f(2, 5), f(0)),
            (f(1, 5), f(-2, 5), f(1)),
        ),
    )
    report = sensitivity_analysis(example_one, solution)
    oracle = verify_with_scipy(example_one)
    assert {key: float(value) for key, value in report.shadow_prices.items()} == pytest.approx(
        oracle.shadow_prices
    )
    assert report.shadow_prices == {"R1": f(14), "R2": f(22), "R3": f(0)}
    assert report.reduced_costs == {"x1": f(0), "x2": f(0)}
    assert report.objective_ranges == {"x1": (f(80, 3), f(160)), "x2": (f(25), f(150))}
    assert report.rhs_ranges == {"R1": (f(30), f(180)), "R2": (f(50), f(150)), "R3": (f(16), None)}
    assert report.interpretations and all(report.interpretations.values())
