"""Property conditions bind + tighter than |, in symbol and keyword styles alike."""

from __future__ import annotations

import itertools

import pytest

from skinshortcuts.conditions import evaluate_condition

AND_OR = ["a + b | c", "a AND b | c", "a + b OR c", "a AND b OR c"]
OR_AND = ["a | b + c", "a OR b + c", "a | b AND c", "a OR b AND c"]
NEGATED = ["!a + b", "NOT a + b", "!a AND b", "NOT a AND b"]

TRUTH = list(itertools.product([False, True], repeat=3))


def props(a: bool, b: bool, c: bool) -> dict[str, str]:
    """Only truthy properties are present."""
    return {k: "1" for k, v in zip("abc", (a, b, c), strict=True) if v}


@pytest.mark.parametrize("cond", AND_OR)
@pytest.mark.parametrize(("a", "b", "c"), TRUTH)
def test_and_binds_tighter_than_or(cond: str, a: bool, b: bool, c: bool) -> None:
    assert evaluate_condition(cond, props(a, b, c)) is ((a and b) or c)


@pytest.mark.parametrize("cond", OR_AND)
@pytest.mark.parametrize(("a", "b", "c"), TRUTH)
def test_trailing_and_binds_tighter(cond: str, a: bool, b: bool, c: bool) -> None:
    assert evaluate_condition(cond, props(a, b, c)) is (a or (b and c))


@pytest.mark.parametrize("cond", NEGATED)
@pytest.mark.parametrize(("a", "b", "c"), TRUTH)
def test_negation_binds_to_its_own_term(cond: str, a: bool, b: bool, c: bool) -> None:
    assert evaluate_condition(cond, props(a, b, c)) is ((not a) and b)


@pytest.mark.parametrize(("a", "b", "c"), TRUTH)
def test_brackets_override_precedence(a: bool, b: bool, c: bool) -> None:
    assert evaluate_condition("a + [b | c]", props(a, b, c)) is (a and (b or c))
    assert evaluate_condition("[a + b] | c", props(a, b, c)) is ((a and b) or c)


GROUPED = [
    # a bracketed group beside a compact list is a condition, not a value for the property
    ("![widgetType=movies | [widgetType=tvshows + widgetStyle=Panel]]",
     {"widgetType": "tvshows", "widgetStyle": "Panel"}, False),
    ("![widgetType=movies | [widgetType=tvshows + widgetStyle=Panel]]",
     {"widgetType": "albums"}, True),
    ("widgetType=movies | [widgetType=tvshows + widgetStyle=Panel]",
     {"widgetType": "tvshows", "widgetStyle": "Panel"}, True),
    ("[widgetType=movies | widgetType=tvshows] | widgetStyle=Panel",
     {"widgetStyle": "Panel"}, True),
    # plain compact OR still expands against the running property
    ("widgetType=movies | episodes | tvshows", {"widgetType": "episodes"}, True),
    ("widgetType=movies | episodes | tvshows", {"widgetType": "albums"}, False),
]


@pytest.mark.parametrize(("cond", "props_", "want"), GROUPED)
def test_groups_survive_compact_or_expansion(cond: str, props_: dict, want: bool) -> None:
    assert evaluate_condition(cond, props_) is want


NESTED_COMPACT = [
    # a compact value list inside a group expands against the group's own property
    ("widgetType=movies | [widgetStyle=Panel | List]", {"widgetStyle": "List"}, True),
    ("widgetType=movies | [widgetStyle=Panel | List]", {"widgetStyle": "Wide"}, False),
    ("widgetType=movies | [widgetStyle=Panel | List]", {"widgetType": "movies"}, True),
    ("a=1 + [b=2 | 3]", {"a": "1", "b": "3"}, True),
    ("a=1 + [b=2 | 3]", {"a": "1", "b": "4"}, False),
]


@pytest.mark.parametrize(("cond", "props_", "want"), NESTED_COMPACT)
def test_compact_or_expands_inside_groups(cond: str, props_: dict, want: bool) -> None:
    assert evaluate_condition(cond, props_) is want
