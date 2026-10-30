"""Tests for the `<value iterate=... as=...>` expansion in TemplateBuilder."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from types import SimpleNamespace

import pytest

from skinshortcuts.builders.template import TemplateBuilder


@pytest.fixture
def builder() -> TemplateBuilder:
    tb = TemplateBuilder.__new__(TemplateBuilder)
    tb.schema = None
    tb.menus = []
    tb._menu_map = {}
    tb._assigned_templates = set()
    return tb


def _item(props: dict[str, str]) -> SimpleNamespace:
    """Stand-in item holding given properties."""
    return SimpleNamespace(properties=props)


def test_resolve_suffixes_numeric():
    assert TemplateBuilder._resolve_iterate_suffixes("3", _item({})) == ["", ".2", ".3"]


def test_resolve_suffixes_family_scan_with_gaps():
    item = _item({"widgetPath": "a", "widgetPath.3": "c", "widgetPath.4": "d"})
    assert TemplateBuilder._resolve_iterate_suffixes("widgetPath", item) == ["", ".3", ".4"]


def test_resolve_suffixes_family_empty_when_missing():
    assert TemplateBuilder._resolve_iterate_suffixes("widgetPath", _item({})) == []


def test_apply_iterate_text_resolves_loop_locals():
    out = TemplateBuilder._apply_iterate_to_text(
        "$PROPERTY[slotIndex]-$PROPERTY[slotSuffix]", ".3", 2, "slot"
    )
    assert out == "2-.3"


def test_apply_iterate_text_suffixes_other_props():
    out = TemplateBuilder._apply_iterate_to_text("$PROPERTY[widgetPath]", ".3", 2, "slot")
    assert out == "$PROPERTY[widgetPath.3]"


def test_apply_iterate_text_skips_no_suffix_props():
    out = TemplateBuilder._apply_iterate_to_text("$PROPERTY[id]-$PROPERTY[name]", ".3", 2, "slot")
    assert out == "$PROPERTY[id]-$PROPERTY[name]"


def test_apply_iterate_text_empty_suffix_unchanged():
    out = TemplateBuilder._apply_iterate_to_text("$PROPERTY[widgetPath]", "", 1, "slot")
    assert out == "$PROPERTY[widgetPath]"


def test_expand_family_scan(builder: TemplateBuilder):
    item = _item({"widgetPath": "a", "widgetPath.3": "c"})
    src = (
        '<variable name="V">'
        '<value iterate="widgetPath" as="s" '
        'condition="!String.IsEmpty($PROPERTY[widgetName])">'
        "$PROPERTY[widgetPath]</value>"
        "<value>fallback</value>"
        "</variable>"
    )
    elem = ET.fromstring(src)
    builder._expand_iterate_values(elem, item, {})

    values = list(elem)
    assert len(values) == 3
    assert values[0].text == "$PROPERTY[widgetPath]"
    assert values[0].attrib["condition"] == "!String.IsEmpty($PROPERTY[widgetName])"
    assert values[1].text == "$PROPERTY[widgetPath.3]"
    assert values[1].attrib["condition"] == "!String.IsEmpty($PROPERTY[widgetName.3])"
    assert values[2].text == "fallback"
    assert "iterate" not in values[0].attrib


def test_expand_numeric(builder: TemplateBuilder):
    item = _item({})
    src = (
        '<variable name="V">'
        '<value iterate="3" as="n">$PROPERTY[nIndex]:$PROPERTY[nSuffix]</value>'
        "</variable>"
    )
    elem = ET.fromstring(src)
    builder._expand_iterate_values(elem, item, {})

    values = list(elem)
    assert [v.text for v in values] == ["1:", "2:.2", "3:.3"]


def test_expand_warns_and_strips_when_as_missing(builder: TemplateBuilder):
    item = _item({"widgetPath": "a"})
    src = '<variable name="V"><value iterate="widgetPath">x</value></variable>'
    elem = ET.fromstring(src)
    builder._expand_iterate_values(elem, item, {})

    values = list(elem)
    assert len(values) == 1
    assert values[0].text == "x"
    assert "iterate" not in values[0].attrib
    assert "as" not in values[0].attrib


def test_resolve_suffixes_family_scan_any_case():
    item = _item({"widgetpath": "a", "WIDGETPATH.3": "c"})
    assert TemplateBuilder._resolve_iterate_suffixes("widgetPath", item) == ["", ".3"]
