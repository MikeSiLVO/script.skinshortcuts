"""$MATH operators, floor division, float results, missing properties and failed expressions."""

from __future__ import annotations

import pytest

from skinshortcuts.expressions import evaluate_math, process_math_expressions


@pytest.fixture
def warned(monkeypatch) -> list[str]:
    """Toasts shown while the expression runs, as heading and message."""
    captured: list[str] = []
    monkeypatch.setattr(
        "xbmcgui.Dialog.notification", lambda _self, h, m, *_: captured.append(f"{h}: {m}")
    )
    return captured


def test_integer_floor_division() -> None:
    """Floor division of integers rounds toward negative infinity."""
    assert evaluate_math("7//2", {}) == "3"
    assert evaluate_math("-7//2", {}) == "-4"


@pytest.mark.parametrize(
    ("expr", "want"),
    [("-3.5//1", "-4"), ("7//2.5", "2"), ("100//2.5", "40"), ("5//0.5", "10")],
)
def test_floor_division_floors_non_integers(expr: str, want: str) -> None:
    """Floor division with a decimal on either side floors to a whole number."""
    assert evaluate_math(expr, {}) == want


@pytest.mark.parametrize(
    ("expr", "want"),
    [
        ("7 % 3", "1"),
        ("7 / 2", "3.5"),
        ("+5", "5"),
        ("-(2 + 3)", "-5"),
        ("2 + 3 * 4", "14"),
        ("(2 + 3) * 4", "20"),
        (" 1 + 2 ", "3"),
        ("2 * 3 ", "6"),
        ("slot * 100 + offset", "250"),
    ],
)
def test_operators(expr: str, want: str) -> None:
    """Modulo, true division, unary signs, precedence, grouping, spaces and property names."""
    assert evaluate_math(expr, {"slot": "2", "offset": "50"}) == want


@pytest.mark.xfail(strict=True, reason="won't fix: float results are not rounded")
def test_float_results_are_rounded() -> None:
    """Float results are rounded, 0.1+0.2 giving 0.3."""
    assert evaluate_math("0.1+0.2", {}) == "0.3"


def test_missing_property_counts_as_zero() -> None:
    """A missing or non-numeric property counts as zero."""
    assert evaluate_math("offset*2 + 10", {}) == "10"
    assert evaluate_math("offset*2 + 10", {"offset": "wide"}) == "10"


@pytest.mark.parametrize(
    "expr", ["1 / 0", "1 // 0", "1 % 0", "1 2", "(1 + 2", "1 + @", "1 +", "", "2 * (3"]
)
def test_failed_expression_is_reported(warned: list[str], expr: str) -> None:
    """Division by zero and bad syntax give back the text unchanged, with one toast."""
    assert evaluate_math(expr, {}) == expr
    assert warned == ["Expression Error: $MATH failed (see log)"]


def test_failed_expression_loses_its_wrapper() -> None:
    """A failed $MATH in a value loses its wrapper, leaving the bare text."""
    assert process_math_expressions("id=$MATH[x/0]", {}) == "id=x/0"
