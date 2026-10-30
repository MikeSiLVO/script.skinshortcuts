"""$INCLUDE[...] text becomes Kodi <include> elements, in every template kind and for every ref."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import Menu, MenuItem
from skinshortcuts.models.template import TemplateSchema

WIDGET = "$INCLUDE[skinshortcuts-template-MovieWidgets]"
CONTENT = "<control type=\"list\"><content>$PROPERTY[widgetPath]</content></control>"

TEMPLATES = f"""<templates>
  <template include="Menu" menu="mainmenu">
    <controls>{CONTENT}</controls>
  </template>
  <template include="Raw" build="true" menu="mainmenu">
    <property name="widgetPath" from="widgetPath" />
    <controls>
      <control type="list">
        <content>$PROPERTY[widgetPath]</content>
        <skinshortcuts>visibility</skinshortcuts>
      </control>
    </controls>
  </template>
  <template items="widgets" source="widgets">
    <controls>{CONTENT}</controls>
  </template>
  <submenu include="Level" level="1">
    <controls>{CONTENT}</controls>
  </submenu>
  <submenu include="Named" name="movies.widgets">
    <controls><control type="group"><skinshortcuts insert="widgets" /></control></controls>
  </submenu>
</templates>"""


@pytest.fixture
def root(tmp_path: Path) -> ET.Element:
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES, encoding="utf-8")
    movies = MenuItem(name="movies", label="Movies", properties={"widgetPath": WIDGET})
    widget = MenuItem(name="recent", label="Recent", properties={"widgetPath": WIDGET})
    menus = [
        Menu(name="mainmenu", items=[movies], container="9000"),
        Menu(name="mainmenu/movies", items=[MenuItem(name="a", label="A")], is_submenu=True),
        Menu(name="movies.widgets", items=[widget], is_submenu=True),
    ]
    return TemplateBuilder(load_templates(path), menus).build()


def content_of(root: ET.Element, include: str) -> ET.Element:
    """First <content> element under the include of a given name, asserted present."""
    found = root.find(f"include[@name='{include}']//content")
    assert found is not None
    return found


def converted(content: ET.Element) -> bool:
    """Whether the widget path became an <include> child with no literal left behind."""
    names = [child.text for child in content.findall("include")]
    return names == ["skinshortcuts-template-MovieWidgets"] and not (content.text or "").strip()


def test_menu_template_converts(root: ET.Element) -> None:
    assert converted(content_of(root, "skinshortcuts-template-Menu"))


def test_items_inside_a_submenu_template_convert(root: ET.Element) -> None:
    assert converted(content_of(root, "skinshortcuts-Named"))


def test_raw_template_converts(root: ET.Element) -> None:
    assert converted(content_of(root, "skinshortcuts-template-Raw"))


def test_level_submenu_template_converts(root: ET.Element) -> None:
    assert converted(content_of(root, "skinshortcuts-Level"))


def test_every_reference_in_one_text_converts() -> None:
    elem = ET.Element("content")
    elem.text = "$INCLUDE[First]$INCLUDE[Second]"
    TemplateBuilder(TemplateSchema(), [])._handle_include_substitution(elem)
    assert [child.text for child in elem] == ["First", "Second"]
    assert "$INCLUDE" not in ET.tostring(elem, encoding="unicode")
