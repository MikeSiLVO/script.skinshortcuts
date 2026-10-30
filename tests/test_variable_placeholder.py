"""A declared variable no item built still gets a placeholder."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from skinshortcuts.config import SkinConfig


MENUS = """<?xml version="1.0"?>
<menus>
  <menu name="mainmenu" container="9000">
    <item name="movies"><label>Movies</label><action>Noop</action>
      <property name="widgetPath">videodb://movies/</property>
    </item>
  </menu>
</menus>
"""


def _build(tmp_path: Path, templates: str) -> ET.Element:
    """Build includes for the test menus and given templates XML."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS)
    (skin / "templates.xml").write_text(
        f'<?xml version="1.0"?>\n<templates>{templates}\n</templates>\n'
    )
    out = tmp_path / "out.xml"
    SkinConfig.load(skin, load_user=False).build_includes(str(out))
    return ET.fromstring(out.read_text())


def _variables(root: ET.Element) -> dict[str, ET.Element]:
    """Every variable in the build, by name."""
    return {v.get("name") or "": v for v in root.iter("variable")}


def test_unmatched_template_still_defines_its_variable(tmp_path: Path):
    root = _build(tmp_path, """
  <template menu="mainmenu" include="A">
    <condition>backgroundType=playlist</condition>
    <variables><variable name="PlaylistVar"><value>$PROPERTY[widgetPath]</value></variable>"""
    """</variables>
    <controls><label>x</label></controls>
  </template>""")

    placeholder = _variables(root)["PlaylistVar"]
    values = list(placeholder)
    assert [v.tag for v in values] == ["value"]
    assert not (values[0].text or "").strip()


def test_kodi_keeps_a_variable_that_has_a_value_child(tmp_path: Path):
    root = _build(tmp_path, """
  <template menu="mainmenu" include="A">
    <condition>backgroundType=playlist</condition>
    <variables><variable name="PlaylistVar"><value>x</value></variable></variables>
    <controls><label>x</label></controls>
  </template>""")

    assert len(list(_variables(root)["PlaylistVar"])) >= 1


def test_a_built_variable_is_not_replaced_by_a_placeholder(tmp_path: Path):
    root = _build(tmp_path, """
  <template menu="mainmenu" include="A">
    <variables><variable name="BuiltVar"><value>$PROPERTY[widgetPath]</value></variable></variables>
    <controls><label>x</label></controls>
  </template>""")

    built = _variables(root)["BuiltVar"]
    assert "".join(built.itertext()).strip() == "videodb://movies/"


def test_item_derived_name_is_never_given_a_placeholder(tmp_path: Path):
    root = _build(tmp_path, """
  <template menu="mainmenu" include="A">
    <condition>backgroundType=playlist</condition>
    <variables>
      <variable name="PerItem" output="Widget$PROPERTY[id]Var"><value>x</value></variable>
    </variables>
    <controls><label>x</label></controls>
  </template>""")

    assert _variables(root) == {} or all("Widget" not in n for n in _variables(root))


def test_variable_group_reference_gets_a_placeholder(tmp_path: Path):
    root = _build(tmp_path, """
  <variables>
    <variable name="GroupedVar"><value>$PROPERTY[widgetPath]</value></variable>
    <variableGroup name="theGroup"><variable content="GroupedVar" /></variableGroup>
  </variables>
  <template menu="mainmenu" include="A">
    <condition>backgroundType=playlist</condition>
    <variableGroup content="theGroup" />
    <controls><label>x</label></controls>
  </template>""")

    assert "GroupedVar" in _variables(root)


def test_menu_with_no_items_still_defines_the_variable(tmp_path: Path):
    root = _build(tmp_path, """
  <template menu="nosuchmenu" include="A">
    <variables><variable name="OrphanVar"><value>literal</value></variable></variables>
    <controls><label>x</label></controls>
  </template>""")

    assert "OrphanVar" in _variables(root)


def test_items_template_variable_group_gets_a_placeholder(tmp_path: Path):
    root = _build(tmp_path, """
  <variables>
    <variable name="ItemsVar"><value>$PROPERTY[widgetPath]</value></variable>
    <variableGroup name="itemsGroup"><variable content="ItemsVar" /></variableGroup>
  </variables>
  <template menu="mainmenu" include="A">
    <controls><control type="group"><skinshortcuts insert="widgets">items</skinshortcuts>"""
    """</control></controls>
  </template>
  <template items="widgets" source="widgets">
    <variableGroup content="itemsGroup" />
    <controls><label>x</label></controls>
  </template>""")

    assert "ItemsVar" in _variables(root)
