"""An items template's own properties, vars, presets and property groups, $PARENT included."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.menu import load_menus
from skinshortcuts.loaders.template import load_templates

MENUS = """<menus>
<menu name="mainmenu" container="9000">
  <item name="movies"><label>Movies</label><action>Noop</action>
    <property name="parentStyle">wide</property></item>
</menu>
<submenu name="movies.widgets">
  <item name="first"><label>First</label><action>Noop</action>
    <property name="widgetArt">Poster</property></item>
  <item name="second"><label>Second</label><action>Noop</action>
    <property name="widgetArt">Landscape</property></item>
</submenu>
</menus>"""

TEMPLATES = """<templates>
<presets><preset name="posterSize"><values width="200" height="300" /></preset></presets>
<propertyGroups>
  <propertyGroup name="landscapeProps"><property name="aspect">wide</property></propertyGroup>
</propertyGroups>
<template include="Widgets" menu="mainmenu">
  <controls><control type="grouplist"><skinshortcuts insert="widgets" /></control></controls>
</template>
<template items="widgets" source="widgets">
  <property name="caption">$PARENT[label]: $PROPERTY[label]</property>
  <var name="style">
    <value condition="widgetArt=Poster">$PARENT[parentStyle]-poster</value>
    <value>$PARENT[parentStyle]-other</value>
  </var>
  <preset content="posterSize" condition="widgetArt=Poster" />
  <propertyGroup content="landscapeProps" condition="widgetArt=Landscape" />
  <controls>
    <control type="group">
      <caption>$PROPERTY[caption]</caption>
      <style>$PROPERTY[style]</style>
      <width>$PROPERTY[width]</width>
      <aspect>$PROPERTY[aspect]</aspect>
    </control>
  </controls>
</template>
</templates>"""


def widgets(tmp_path: Path) -> list[dict[str, str]]:
    """Leaf texts by tag for each control the items template builds, in submenu order."""
    (tmp_path / "menus.xml").write_text(MENUS, encoding="utf-8")
    (tmp_path / "templates.xml").write_text(TEMPLATES, encoding="utf-8")
    menus = load_menus(str(tmp_path / "menus.xml"))
    root = TemplateBuilder(load_templates(str(tmp_path / "templates.xml")), menus.menus).build()
    return [
        {leaf.tag: leaf.text or "" for leaf in control}
        for control in root.iter("control")
        if control.get("type") == "group"
    ]


def test_parent_reads_in_property_and_var(tmp_path: Path) -> None:
    """$PARENT in a property or a var value reads the main item; $PROPERTY the submenu item."""
    built = widgets(tmp_path)
    assert [(w["caption"], w["style"]) for w in built] == [
        ("Movies: First", "wide-poster"),
        ("Movies: Second", "wide-other"),
    ]


def test_preset_and_property_group_follow_their_condition(tmp_path: Path) -> None:
    """Preset and property group each follow their condition, per submenu item."""
    built = widgets(tmp_path)
    assert [(w.get("width"), w.get("aspect")) for w in built] == [("200", None), (None, "wide")]
