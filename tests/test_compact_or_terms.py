"""Compact OR expansion next to keyword operators, bracket groups and IN or EMPTY terms."""

from __future__ import annotations

import pytest

from skinshortcuts.conditions import evaluate_condition, expand_compact_or, suffix_condition

MARTIAN = "widgetAspect=Square OR widgetPath IN Submenu,Settings,Systeminfo"


@pytest.mark.parametrize(
    "condition",
    ["widgetType=movies | tvshows", "widgetType=movies OR tvshows", "widgetType IN movies,tvshows"],
)
def test_symbol_forms_take_compact_values(condition: str) -> None:
    assert evaluate_condition(condition, {"widgetType": "tvshows"}) is True


@pytest.mark.parametrize(
    ("condition", "properties"),
    [
        ("widgetType EQUALS movies OR tvshows", {"widgetType": "tvshows"}),
        ("widgetType EQUALS movies | tvshows", {"widgetType": "tvshows"}),
        ("widgetPath CONTAINS movies OR tvshows", {"widgetPath": "videodb://tvshows/titles/"}),
    ],
)
def test_keyword_forms_take_compact_values(condition: str, properties: dict[str, str]) -> None:
    assert evaluate_condition(condition, properties) is True


def test_keyword_compact_values_suffix_their_property() -> None:
    suffixed = suffix_condition("widgetType EQUALS movies OR tvshows", ".2")
    assert suffixed == "widgetType.2=movies | widgetType.2=tvshows"


def test_and_joined_groups_expand_inside_each_group() -> None:
    assert expand_compact_or("[a=1 | 2] + [b=3 | 4]") == "[a=1 | a=2] + [b=3 | b=4]"


def test_or_joined_groups_keep_their_own_property() -> None:
    assert expand_compact_or("[a=1] | [b=2 | 3]") == "[a=1] | [b=2 | b=3]"
    assert evaluate_condition("[a=1] | [b=2 | 3]", {"b": "3"}) is True


def test_in_term_after_compact_or_is_its_own_term() -> None:
    assert evaluate_condition(MARTIAN, {"widgetPath": "Settings"}) is True
    assert suffix_condition(MARTIAN, ".2") == (
        "widgetAspect.2=Square | widgetPath.2 IN Submenu,Settings,Systeminfo"
    )


def test_empty_term_after_compact_or_is_its_own_term() -> None:
    properties = {"widgetType": "tvshows", "widgetPath": "plugin://x/"}
    assert evaluate_condition("widgetType=movies | widgetPath EMPTY", properties) is False


@pytest.mark.xfail(strict=True, reason="won't fix, documented: IN and EMPTY are reserved in values")
@pytest.mark.parametrize(
    ("condition", "label", "want"),
    [("label=Films IN HD", "Films IN HD", True), ("label=Nothing EMPTY", "Something", False)],
)
def test_operator_words_inside_a_value(condition: str, label: str, want: bool) -> None:
    assert evaluate_condition(condition, {"label": label}) is want
