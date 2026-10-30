"""A from= name or iterate ref that already carries a slot keeps it on a suffixed output."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.conditions import suffix_condition, suffix_property
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import MenuItem
from skinshortcuts.models.template import TemplateProperty


@pytest.fixture
def builder(tmp_path: Path) -> TemplateBuilder:
    path = tmp_path / "templates.xml"
    path.write_text("<templates/>", encoding="utf-8")
    return TemplateBuilder(load_templates(path), [])


def test_condition_keeps_an_existing_slot() -> None:
    assert suffix_condition("widgetPath.3", ".2") == "widgetPath.3"


def test_from_keeps_an_existing_slot() -> None:
    assert suffix_property("widgetPath.3", ".2") == "widgetPath.3"


@pytest.mark.parametrize(
    "suffix", ["", ".2"]
)
def test_from_slot_resolves_on_every_output(builder: TemplateBuilder, suffix: str) -> None:
    item = MenuItem(name="movies", label="Movies", properties={"widgetPath.3": "plugin://x/"})
    prop = TemplateProperty(name="third", from_source="widgetPath.3")
    assert builder._resolve_property(prop, item, {}, suffix) == "plugin://x/"


def test_iterate_ref_keeps_an_existing_slot() -> None:
    text = TemplateBuilder._apply_iterate_to_text("$PROPERTY[widgetPath.3]", ".2", 2, "slot")
    assert text == "$PROPERTY[widgetPath.3]"
