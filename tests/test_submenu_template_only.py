"""A templates.xml holding only submenu templates still builds them."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import Menu, MenuItem

ROWS = """<template items="rows">
    <controls><control type="button"><label>$PROPERTY[label]</label></control></controls>
  </template>"""


def build(tmp_path: Path, templates: str, menus: list[Menu]) -> ET.Element:
    """Build the includes tree for the given templates.xml body and menus."""
    path = tmp_path / "templates.xml"
    path.write_text(f"<templates>{templates}</templates>", encoding="utf-8")
    return IncludesBuilder(menus, templates=load_templates(path)).build()


def labels(root: ET.Element, include: str) -> list[str]:
    """Button labels under the include of a given name."""
    return [label.text or "" for label in root.findall(f"include[@name='{include}']//label")]


def test_named_submenu_template_builds_its_menu(tmp_path: Path) -> None:
    """Named submenu template builds its include from the named menu's rows."""
    named = """<submenu include="Power" name="powermenu">
    <controls><control type="grouplist"><skinshortcuts insert="rows" /></control></controls>
  </submenu>"""
    power = Menu(name="powermenu", items=[MenuItem(name="quit", label="Quit")], container="9001")
    root = build(tmp_path, ROWS + named, [power])
    assert labels(root, "skinshortcuts-Power") == ["Quit"]


def test_level_submenu_template_builds(tmp_path: Path) -> None:
    """Level submenu template builds one copy per root item that has a submenu."""
    level = """<submenu include="Sub" level="1">
    <controls><control type="button"><label>$PROPERTY[label]</label></control></controls>
  </submenu>"""
    main = Menu(name="mainmenu", items=[MenuItem(name="movies", label="Movies")], container="9000")
    sub = Menu(name="mainmenu/movies", items=[MenuItem(name="a", label="A")], is_submenu=True)
    root = build(tmp_path, level, [main, sub])
    assert labels(root, "skinshortcuts-Sub") == ["Movies"]
