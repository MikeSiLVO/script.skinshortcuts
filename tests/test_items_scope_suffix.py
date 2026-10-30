"""Slot suffixes inside items templates: sub-items have no slots, whatever output hosts them."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import Menu, MenuItem

TEMPLATES = """<templates>
  <variables>
    <variable name="memberVar" output="Member$PARENT[suffix]-$PROPERTY[index]">
      <value>$PROPERTY[widgetPath]</value>
    </variable>
    <variable name="refVar" output="Ref$PARENT[suffix]-$PROPERTY[index]">
      <value>$PROPERTY[widgetPath]</value>
    </variable>
    <variableGroup name="memberConditioned">
      <variable content="memberVar" condition="widgetPath" />
    </variableGroup>
    <variableGroup name="refConditioned">
      <variable content="refVar" />
    </variableGroup>
  </variables>
  <presets>
    <preset name="art">
      <values condition="widgetArt=Poster" art="poster" />
      <values art="other" />
    </preset>
  </presets>
  <propertyGroups>
    <propertyGroup name="artGroup">
      <property name="groupArt" condition="widgetArt=Poster">poster</property>
      <property name="groupArt">other</property>
    </propertyGroup>
  </propertyGroups>
  <template include="host" menu="mainmenu">
    <output include="host1" suffix="" />
    <output include="host2" suffix=".2" />
    <controls>
      <control type="group"><skinshortcuts insert="widgets" /></control>
    </controls>
  </template>
  <template items="widgets" source="widgets">
    <preset content="art" suffix=".2" />
    <propertyGroup content="artGroup" suffix=".2" />
    <controls>
      <control type="label"><label>$PROPERTY[art]|$PROPERTY[groupArt]</label></control>
    </controls>
    <variableGroup content="memberConditioned" />
    <variableGroup content="refConditioned" condition="widgetPath" />
  </template>
</templates>"""


@pytest.fixture
def notified(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Headings and messages the loader notifies."""
    seen: list[str] = []
    monkeypatch.setattr(
        "skinshortcuts.loaders.template.notify", lambda h, m, *_: seen.append(f"{h}: {m}")
    )
    return seen


@pytest.fixture
def root(tmp_path: Path, notified: list[str]) -> ET.Element:
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES, encoding="utf-8")
    widget = MenuItem(
        name="recent",
        label="Recent",
        properties={"widgetPath": "videodb://recent/", "widgetArt": "Poster"},
    )
    menus = [
        Menu(name="mainmenu", items=[MenuItem(name="movies", label="Movies")], container="9000"),
        Menu(name="movies.widgets", items=[widget], is_submenu=True),
    ]
    return TemplateBuilder(load_templates(path), menus).build()


def variable_names(root: ET.Element) -> set[str]:
    """Names of every variable in the build."""
    return {var.get("name", "") for var in root.findall("variable")}


def test_group_reference_condition_builds_in_every_output(root: ET.Element) -> None:
    assert {"Ref-1", "Ref.2-1"} <= variable_names(root)


def test_member_condition_builds_in_every_output(root: ET.Element) -> None:
    assert {"Member-1", "Member.2-1"} <= variable_names(root)


def test_reference_suffix_is_ignored(root: ET.Element) -> None:
    label = root.findtext("include[@name='skinshortcuts-template-host1']/control/control/label")
    assert label == "poster|poster"


def test_reference_suffix_is_reported(root: ET.Element, notified: list[str]) -> None:
    assert set(notified) == {"Items Template Error: 'widgets' uses suffix="}
