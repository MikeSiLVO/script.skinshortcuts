"""Suffix transform: slot every property name the evaluator would read, nothing else."""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

import pytest

from skinshortcuts.conditions import (
    NO_SUFFIX_PROPERTIES,
    evaluate_condition,
    suffix_condition,
)

SKIN_CONDITIONS = json.loads(
    (Path(__file__).parent / "fixtures" / "skin_conditions.json").read_text()
)

CASES = [
    ("widgetType=movies", "widgetType.2=movies"),
    ("widgetType = movies", "widgetType.2=movies"),
    ("widgetType EQUALS movies", "widgetType.2=movies"),
    ("widgetPath~videodb://", "widgetPath.2~videodb://"),
    ("widgetPath CONTAINS videodb://", "widgetPath.2~videodb://"),
    ("widgetPath~plugin://x/?action=list", "widgetPath.2~plugin://x/?action=list"),
    ("widgetPath=a~b", "widgetPath.2=a~b"),
    ("widgetPath", "widgetPath.2"),
    ("!widgetPath", "!widgetPath.2"),
    ("NOT widgetPath", "!widgetPath.2"),
    ("widgetPath EMPTY", "widgetPath.2 EMPTY"),
    ("!widgetPath EMPTY", "!widgetPath.2 EMPTY"),
    ("widgetType IN movies,episodes", "widgetType.2 IN movies,episodes"),
    ("!widgetType=movies", "!widgetType.2=movies"),
    # every comparison in a full OR, not just the first
    ("widgetType=movies | widgetType=episodes", "widgetType.2=movies | widgetType.2=episodes"),
    ("widgetType=movies OR widgetType=episodes", "widgetType.2=movies | widgetType.2=episodes"),
    # compact OR values stay values
    ("widgetType=movies | episodes", "widgetType.2=movies | widgetType.2=episodes"),
    ("a=1 | 2 + b=3", "a.2=1 | a.2=2 + b.2=3"),
    ("a=1 | b=2 | 3", "a.2=1 | b.2=2 | b.2=3"),
    ("widgetType=movies + widgetStyle=Panel", "widgetType.2=movies + widgetStyle.2=Panel"),
    ("[a=1 | b=2] + c", "[a.2=1 | b.2=2] + c.2"),
    ("![a=1 | [b=2 + !c]]", "![a.2=1 | [b.2=2 + !c.2]]"),
    ("!a + b", "!a.2 + b.2"),
    # built-ins stay unslotted
    ("suffix=.2", "suffix=.2"),
    ("!suffix", "!suffix"),
    ("index=1 + name=movies", "index=1 + name=movies"),
    ("label=Films | disabled=true", "label=Films | disabled=true"),
    ("id + idprefix + menu + default", "id + idprefix + menu + default"),
    # names that already carry a slot are left alone
    ("widgetType.2=movies", "widgetType.2=movies"),
    ("widgetType.3 EMPTY", "widgetType.3 EMPTY"),
    ("widgetType=system | widgetType.2=system", "widgetType.2=system | widgetType.2=system"),
    # literals and unexpanded references stay unslotted
    ("true", "true"),
    ("False", "False"),
    ("$EXP[isMovie] + widgetStyle=Panel", "$EXP[isMovie] + widgetStyle.2=Panel"),
    ("!$EXP[isMovie]", "!$EXP[isMovie]"),
    # nosuffix expansions pass through untouched
    (
        "{NOSUFFIX:widgetType=movies | widgetType=tvshows} + widgetStyle=Panel",
        "[{NOSUFFIX:widgetType=movies | widgetType=tvshows}] + widgetStyle.2=Panel",
    ),
    ("!{NOSUFFIX:a=1}", "![{NOSUFFIX:a=1}]"),
]


@pytest.mark.parametrize(("condition", "expected"), CASES)
def test_transform(condition, expected):
    assert suffix_condition(condition, ".2") == expected


def test_no_suffix_or_no_text_is_untouched():
    assert suffix_condition("widgetType = movies", "") == "widgetType = movies"
    assert suffix_condition("", ".2") == ""


@pytest.mark.parametrize("condition", SKIN_CONDITIONS)
def test_idempotent_on_skin_conditions(condition):
    once = suffix_condition(condition, ".2")
    assert suffix_condition(once, ".2") == once


_NAME = re.compile(r"(?<![\w.$])([A-Za-z_][\w.]*)")
_SLOTTED = re.compile(r"\.\d+$")


def _names_and_values(condition: str) -> tuple[set[str], list[str]]:
    """Unslotted names in a condition, and candidate values to give them."""
    names = {n for n in _NAME.findall(condition) if not _SLOTTED.search(n)}
    values = [v.strip() for v in re.split(r"[=~|+\[\]!,]| IN ", condition) if v.strip()]
    return names, values + ["", "true", "false", "x"]


@pytest.mark.parametrize("condition", [c for c in SKIN_CONDITIONS if not re.search(r"\.\d", c)])
def test_slot_two_reads_like_slot_one(condition):
    names, values = _names_and_values(condition)
    rng = random.Random(condition)
    transformed = suffix_condition(condition, ".2")
    for _ in range(40):
        slot_one = {n: rng.choice(values) for n in names}
        builtins = {k: v for k, v in slot_one.items() if k in NO_SUFFIX_PROPERTIES}
        slot_two = {**builtins, **{f"{k}.2": v for k, v in slot_one.items()}}
        assert evaluate_condition(transformed, slot_two) == evaluate_condition(
            condition, slot_one
        ), (condition, transformed, slot_one)
