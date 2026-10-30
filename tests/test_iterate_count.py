"""A numeric iterate count emits exactly that many <value> entries, zero included."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.models.menu import MenuItem
from skinshortcuts.models.template import TemplateSchema


def values(count: str) -> list[str]:
    """Value texts a slot iterate of a given count expands to."""
    var = ET.fromstring(
        f'<variable name="v"><value iterate="{count}" as="slot">'
        "$PROPERTY[slotIndex]</value></variable>"
    )
    item = MenuItem(name="movies", label="Movies")
    TemplateBuilder(TemplateSchema(), [])._expand_iterate_values(var, item, {})
    return [value.text or "" for value in var.findall("value")]


@pytest.mark.parametrize(("count", "want"), [("3", ["1", "2", "3"]), ("1", ["1"])])
def test_count_emits_that_many_values(count: str, want: list[str]) -> None:
    assert values(count) == want


def test_unset_count_emits_nothing() -> None:
    assert values("$PROPERTY[missing]") == []


def test_zero_count_emits_nothing() -> None:
    assert values("0") == []
