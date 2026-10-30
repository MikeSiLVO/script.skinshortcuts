"""Boolean attributes share one rule, keywords ignore case, and digit checks accept only ASCII."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.base import get_bool
from skinshortcuts.loaders.menu import load_menus
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.localize import resolve_label
from skinshortcuts.models.menu import Menu, MenuItem


def menus(tmp_path: Path, attributes: str = "", body: str = "") -> list[Menu]:
    """Menus parsed from a generated one-menu menus.xml."""
    path = tmp_path / "menus.xml"
    path.write_text(
        f'<menus><menu name="mainmenu" {attributes}>'
        '<item name="a"><label>A</label><action>Noop</action></item>'
        f"</menu>{body}</menus>",
        encoding="utf-8",
    )
    return load_menus(path).menus


@pytest.mark.parametrize(("value", "want"), [("true", True), ("TRUE", True), ("false", False)])
def test_get_bool_reads_true_and_false(value: str, want: bool) -> None:
    assert get_bool(ET.fromstring(f'<m flag="{value}"/>'), "flag", not want) is want


@pytest.mark.parametrize("value", ["yes", "1", "on"])
def test_get_bool_falls_back_to_the_default(value: str) -> None:
    assert get_bool(ET.fromstring(f'<m flag="{value}"/>'), "flag", True) is True


@pytest.mark.parametrize("value", ["no", "0", "yes"])
def test_icons_and_standalone_agree(tmp_path: Path, value: str) -> None:
    menu = menus(tmp_path, f'icons="{value}" standalone="{value}"')[0]
    assert menu.icons is menu.standalone


def test_build_keyword_ignores_case(tmp_path: Path) -> None:
    assert menus(tmp_path, 'build="Auto"')[0].build == "auto"


def test_submenu_path_attribute_ignores_case(tmp_path: Path) -> None:
    assert menus(tmp_path, 'submenuPath="All"')[0].submenu_path == "all"


def test_submenu_path_element_ignores_case(tmp_path: Path) -> None:
    path = tmp_path / "menus.xml"
    path.write_text("<menus><submenuPath>All</submenuPath></menus>", encoding="utf-8")
    assert load_menus(path).submenu_path_all is True


def test_non_ascii_menu_id_does_not_abort(tmp_path: Path) -> None:
    assert menus(tmp_path, 'id="²"')[0].startid == 1


def test_non_ascii_setfocus_does_not_abort(tmp_path: Path) -> None:
    dialogs = '<dialogs><subdialog buttonID="800" mode="x" setfocus="²"/></dialogs>'
    menus(tmp_path, body=dialogs)


def test_non_ascii_digit_label_does_not_abort() -> None:
    assert resolve_label("²") == "²"


def test_non_ascii_iterate_count_does_not_abort(tmp_path: Path) -> None:
    path = tmp_path / "templates.xml"
    path.write_text("<templates/>", encoding="utf-8")
    builder = TemplateBuilder(load_templates(path), [])
    item = MenuItem(name="movies", label="Movies")
    assert builder._resolve_iterate_suffixes("²", item) == []
