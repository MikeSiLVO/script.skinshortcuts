"""Raw templates: output suffixes in conditions, and what happens to <variables>."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import Menu, MenuItem

MARKER = "<skinshortcuts>visibility</skinshortcuts>"
VISIBILITY = f'<control type="image">{MARKER}</control>'

SUFFIXED = f"""<templates>
  <template include="RawA" build="true" menu="mainmenu">
    <output include="RawA2" suffix=".2"/>
    <condition>widgetPath</condition>
    <controls>{VISIBILITY}</controls>
  </template>
  <template include="MenuA" menu="mainmenu">
    <output include="MenuA2" suffix=".2"/>
    <condition>widgetPath</condition>
    <controls><control type="label"><label>$PROPERTY[name]</label></control></controls>
  </template>
</templates>"""

UNTRANSFORMED = f"""<templates>
  <template include="RawB" build="true" menu="mainmenu">
    <controls>{VISIBILITY}</controls>
    <variables>
      <variable name="RawBVar"><value>shown</value></variable>
    </variables>
  </template>
</templates>"""

GROUPED = f"""<templates>
  <template include="Bg" build="true" menu="mainmenu">
    <property name="art" from="backgroundPath" />
    <controls>
      <control type="image"><texture>$PROPERTY[art]</texture>{MARKER}</control>
    </controls>
    <variables>
      <variable name="BgVar" output="Bg-$PROPERTY[name]"><value>$PROPERTY[art]</value></variable>
    </variables>
  </template>
</templates>"""

GROUP_REF = f"""<templates>
  <variables>
    <variable name="bgVar" output="Bg-$PROPERTY[name]"><value>$PROPERTY[art]</value></variable>
    <variableGroup name="bgVars"><variable content="bgVar" /></variableGroup>
  </variables>
  <template include="BgRef" build="true" menu="mainmenu">
    <property name="art" from="backgroundPath" />
    <controls>
      <control type="image"><texture>$PROPERTY[art]</texture>{MARKER}</control>
    </controls>
    <variableGroup content="bgVars" />
  </template>
</templates>"""


def mainmenu(*items: MenuItem) -> Menu:
    """The main menu raw templates read, with the container their visibility needs."""
    return Menu(name="mainmenu", items=list(items), container="9000")


def build(tmp_path: Path, templates: str, menu: Menu) -> ET.Element:
    """Write templates.xml and build it against a single menu."""
    path = tmp_path / "templates.xml"
    path.write_text(templates, encoding="utf-8")
    return TemplateBuilder(load_templates(path), [menu]).build()


def include(root: ET.Element, name: str) -> ET.Element:
    """Generated include of a given template, asserted present."""
    found = root.find(f"include[@name='skinshortcuts-template-{name}']")
    assert found is not None
    return found


def variable_names(root: ET.Element) -> set[str]:
    """Names of every generated variable."""
    return {var.get("name", "") for var in root.findall("variable")}


def slot_only_item() -> MenuItem:
    """An item whose only widget is in slot 2."""
    return MenuItem(name="movies", label="Movies", properties={"widgetPath.2": "videodb://x/"})


def test_menu_template_condition_takes_the_output_suffix(tmp_path: Path) -> None:
    root = build(tmp_path, SUFFIXED, mainmenu(slot_only_item()))
    assert include(root, "MenuA2").findtext("control/label") == "movies"


def test_raw_template_condition_takes_the_output_suffix(tmp_path: Path) -> None:
    root = build(tmp_path, SUFFIXED, mainmenu(slot_only_item()))
    visible = include(root, "RawA2").findtext("control/visible")
    assert visible == "String.IsEqual(Container(9000).ListItem.Property(name),movies)"


def test_untransformed_raw_variables_leave_only_the_placeholder(tmp_path: Path) -> None:
    root = build(tmp_path, UNTRANSFORMED, mainmenu(MenuItem(name="movies", label="Movies")))
    var = root.find("variable[@name='RawBVar']")
    assert var is not None
    assert [value.text for value in var.findall("value")] == [None]


def test_grouped_raw_variables_are_not_built(tmp_path: Path) -> None:
    items = [
        MenuItem(name=name, label=name, properties={"backgroundPath": "same.jpg"})
        for name in ("movies", "tvshows", "music")
    ]
    root = build(tmp_path, GROUPED, mainmenu(*items))
    assert variable_names(root) == set()


def test_raw_variable_group_references_are_not_built(tmp_path: Path) -> None:
    items = [
        MenuItem(name=name, label=name, properties={"backgroundPath": f"{name}.jpg"})
        for name in ("movies", "tvshows")
    ]
    root = build(tmp_path, GROUP_REF, mainmenu(*items))
    assert variable_names(root) == set()


@pytest.mark.parametrize(
    "templates", [UNTRANSFORMED, GROUPED, GROUP_REF], ids=["plain", "grouped", "group-ref"]
)
def test_raw_template_variables_are_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, templates: str
) -> None:
    warnings: list[str] = []
    xbmc = sys.modules["xbmc"]
    monkeypatch.setattr(
        xbmc, "log", lambda msg, level=0: warnings.append(msg) if level >= xbmc.LOGWARNING else None
    )
    item = MenuItem(name="movies", label="Movies", properties={"backgroundPath": "a.jpg"})
    build(tmp_path, templates, mainmenu(item))
    assert any("raw templates do not build" in line for line in warnings)


def test_raw_template_on_a_menu_without_container_is_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    notified: list[str] = []
    monkeypatch.setattr(
        "skinshortcuts.builders.template.notify", lambda h, m, *_: notified.append(f"{h}: {m}")
    )
    menu = Menu(name="mainmenu", items=[MenuItem(name="movies", label="Movies")])
    root = build(tmp_path, SUFFIXED, menu)
    assert include(root, "RawA2").findtext("control/visible") == "false"
    assert "Template Error: menu 'mainmenu' has no container" in notified


def test_raw_include_marker_is_left_out_and_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    notified: list[str] = []
    monkeypatch.setattr(
        "skinshortcuts.loaders.template.notify", lambda h, m, *_: notified.append(f"{h}: {m}")
    )
    templates = """<templates>
  <includes><include name="Shared"><control type="image" /></include></includes>
  <template include="RawInc" build="true" menu="mainmenu">
    <controls><control type="group"><skinshortcuts include="Shared" /></control></controls>
  </template>
</templates>"""
    root = build(tmp_path, templates, mainmenu(MenuItem(name="movies", label="Movies")))
    assert include(root, "RawInc").find(".//skinshortcuts") is None
    assert "Template Error: raw template 'RawInc' has <skinshortcuts include>" in notified
