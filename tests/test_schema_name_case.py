"""Names the script coined match in any case; the rest of the XML keeps the case it was written."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path

import pytest

from skinshortcuts.exceptions import TemplateConfigError
from skinshortcuts.loaders.base import _ATTRIBUTES, _ELEMENTS, parse_xml
from skinshortcuts.loaders.menu import load_menus
from skinshortcuts.loaders.property import load_properties
from skinshortcuts.loaders.template import load_templates

ITEM = '<item name="a"><label>A</label><action>Noop</action></item>'

SAMPLES = [
    ("controlType", load_menus, f'<menus><menu name="m" {{}}="list">{ITEM}</menu></menus>'),
    ("enableOn", load_menus, '<menus><contextmenu {}="211"/></menus>'),
    ("setFocus", load_menus,
     '<menus><dialogs><subdialog buttonID="800" mode="widget1" {}="309"/></dialogs></menus>'),
    ("noSuffix", load_templates,
     '<templates><expressions><expression name="e" {}="true">a</expression></expressions>'
     "</templates>"),
    ("idPrefix", load_templates, '<templates><template include="T" {}="80"/></templates>'),
    ("templateOnly", load_templates, '<templates><template include="T" {}="true"/></templates>'),
    ("templateOnly", load_properties, '<properties><property name="p" {}="true"/></properties>'),
]


def parse(tmp_path: Path, body: str) -> ET.Element:
    """Parse XML wrapped in a <templates> root, as a templates.xml file."""
    path = tmp_path / "templates.xml"
    path.write_text(f"<templates>{body}</templates>", encoding="utf-8")
    return parse_xml(path, "templates", TemplateConfigError)


@pytest.mark.parametrize("case", [str.lower, str.upper])
@pytest.mark.parametrize("name", sorted(_ELEMENTS.values()))
def test_element_name_reads_in_any_case(tmp_path: Path, name: str, case: Callable) -> None:
    """An element the script names is respelled as the loaders read it."""
    assert parse(tmp_path, f"<{case(name)}/>")[0].tag == name


@pytest.mark.parametrize("case", [str.lower, str.upper])
@pytest.mark.parametrize("name", sorted(set(_ATTRIBUTES.values())))
def test_attribute_name_reads_in_any_case(tmp_path: Path, name: str, case: Callable) -> None:
    """An attribute the script names is respelled as the loaders read it."""
    assert parse(tmp_path, f'<x {case(name)}="1"/>')[0].attrib == {name: "1"}


def test_other_names_keep_their_case(tmp_path: Path) -> None:
    """Kodi's names, and the script's attribute names written as elements, stay as written."""
    body = '<control colorDiffuse="a" Type="b"><Visible/><idprefix/></control>'
    control = parse(tmp_path, body)[0]
    assert control.attrib == {"colorDiffuse": "a", "Type": "b"}
    assert [child.tag for child in control] == ["Visible", "idprefix"]


def test_first_spelling_wins(tmp_path: Path) -> None:
    """An attribute written twice in different case keeps the first value."""
    attrib = parse(tmp_path, '<x controltype="a" controlType="b"/>')[0].attrib
    assert attrib == {"controlType": "a"}


@pytest.mark.parametrize(
    ("name", "loader", "xml"), SAMPLES, ids=[f"{n} {f.__name__}" for n, f, _ in SAMPLES]
)
def test_both_spellings_load_alike(tmp_path: Path, name: str, loader: Callable, xml: str) -> None:
    """The documented spelling and the run-together one load the same, and both are read."""
    loaded = []
    for number, spelling in enumerate((name, name.lower(), "unread")):
        path = tmp_path / f"{number}.xml"
        path.write_text(xml.format(spelling), encoding="utf-8")
        loaded.append(loader(path))
    assert loaded[0] == loaded[1] != loaded[2]


def test_old_name_loads_with_one_info_line(tmp_path: Path, monkeypatch) -> None:
    """An old name loads as its new one, logged once at info with no toast, however often read."""
    lines: list[tuple[int, str]] = []
    toasts: list[tuple] = []
    monkeypatch.setattr("xbmc.log", lambda msg, level: lines.append((level, msg)))
    monkeypatch.setattr("xbmcgui.Dialog.notification", lambda *args: toasts.append(args))
    path = tmp_path / "menus.xml"
    menu = f'<menus><menu name="m" template_only="submenu">{ITEM}</menu></menus>'
    path.write_text(menu, encoding="utf-8")

    assert [load_menus(path).menus[0].template_only for _ in range(2)] == ["submenu"] * 2
    assert [line for line in lines if "deprecated attribute" in line[1]] == [(
        1, 'script.skinshortcuts: menus.xml: <menu template_only="submenu"> uses a deprecated '
        "attribute; please update to use templateOnly, since template_only will be removed in a "
        "future version",
    )]
    assert toasts == []
