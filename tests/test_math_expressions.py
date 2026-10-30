"""$MATH floor division, float results, missing properties and failed expressions."""

from __future__ import annotations

import pytest

from skinshortcuts.expressions import evaluate_math, process_math_expressions


def test_integer_floor_division() -> None:
    assert evaluate_math("7//2", {}) == "3"
    assert evaluate_math("-7//2", {}) == "-4"


@pytest.mark.parametrize(
    ("expr", "want"),
    [("-3.5//1", "-4"), ("7//2.5", "2"), ("100//2.5", "40"), ("5//0.5", "10")],
)
def test_floor_division_floors_non_integers(expr: str, want: str) -> None:
    assert evaluate_math(expr, {}) == want


@pytest.mark.xfail(strict=True, reason="won't fix: float results are not rounded")
def test_float_results_are_rounded() -> None:
    assert evaluate_math("0.1+0.2", {}) == "0.3"


def test_missing_property_counts_as_zero() -> None:
    assert evaluate_math("offset*2 + 10", {}) == "10"
    assert evaluate_math("offset*2 + 10", {"offset": "wide"}) == "10"


def test_failed_expression_loses_its_wrapper() -> None:
    assert process_math_expressions("id=$MATH[x/0]", {}) == "id=x/0"
