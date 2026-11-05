"""Slot limits and the names that never take a slot suffix, in code and in the templates doc."""

from __future__ import annotations

import re
from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.conditions import NO_SUFFIX_PROPERTIES
from skinshortcuts.models.menu import Menu, MenuItem

TEMPLATES_DOC = Path(__file__).resolve().parents[1] / "docs" / "skinning" / "templates.md"


def custom_widget_includes(slot: str) -> list[str]:
    """Custom widget include names for a movies item with one custom widget at a given suffix."""
    parent = MenuItem(name="movies", label="Movies", properties={f"customWidget{slot}": "cw"})
    widget = MenuItem(name="recent", label="Recent")
    menus = [
        Menu(name="mainmenu", items=[parent], container="9000"),
        Menu(name="cw", items=[widget], is_submenu=True),
    ]
    elements = IncludesBuilder(menus)._build_custom_widget_includes(menus[0])
    return [element.get("name", "") for element in elements]


def test_custom_widget_slot_ten_builds() -> None:
    assert custom_widget_includes(".10") == ["skinshortcuts-movies-customwidget10"]


def test_custom_widget_slot_eleven_builds() -> None:
    assert custom_widget_includes(".11") == ["skinshortcuts-movies-customwidget11"]


def test_custom_widget_slots_build_in_slot_order() -> None:
    parent = MenuItem(name="movies", label="Movies", properties={
        "customWidget.12": "cw", "customwidget.3": "cw", "customWidget": "cw",
        "customWidgetStyle": "x",
    })
    menus = [
        Menu(name="mainmenu", items=[parent], container="9000"),
        Menu(name="cw", items=[MenuItem(name="recent", label="Recent")], is_submenu=True),
    ]
    names = [e.get("name") for e in IncludesBuilder(menus)._build_custom_widget_includes(menus[0])]
    assert names == [
        "skinshortcuts-movies-customwidget",
        "skinshortcuts-movies-customwidget3",
        "skinshortcuts-movies-customwidget12",
    ]


def test_iterate_scan_ignores_case() -> None:
    item = MenuItem(name="m", label="M", properties={"widgetPath": "a", "widgetPath.3": "b"})
    assert TemplateBuilder._resolve_iterate_suffixes("widgetpath", item) == ["", ".3"]


def test_iterate_scan_reaches_slot_one_hundred() -> None:
    item = MenuItem(name="m", label="M", properties={"widgetPath": "a", "widgetPath.100": "b"})
    assert TemplateBuilder._resolve_iterate_suffixes("widgetPath", item) == ["", ".100"]


def test_suffix_transform_section_lists_every_unsuffixed_name() -> None:
    """The templates doc's Suffix Transform section lists every name the suffix skips, any case."""
    text = TEMPLATES_DOC.read_text(encoding="utf-8")
    section = re.search(r"### Suffix Transform\n(.*?)\n### ", text, re.S)
    assert section is not None
    listed = {name.lower() for name in re.findall(r"`(\w+)`", section.group(1))}
    assert NO_SUFFIX_PROPERTIES <= listed
