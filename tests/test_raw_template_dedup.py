"""Raw template dedup: one control per distinct resolved output, visibility OR'd per group."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.menu import load_menus
from skinshortcuts.loaders.template import load_templates

MATCHING = ("favorites", "movies", "livetv", "music")

MENUS = """<menus>
  <menu name="mainmenu" container="9000">
    <item name="favorites"><label>Favourites</label>
      <property name="widgetLayout">4x3</property>
      <property name="widgetLabel">Favourites</property>
      <property name="widgetPath">favourites://</property></item>
    <item name="movies"><label>Movies</label>
      <property name="widgetLayout">4x3</property>
      <property name="widgetLabel">Recently added movies</property>
      <property name="widgetPath">videodb://recentlyaddedmovies/</property></item>
    <item name="livetv"><label>Live TV</label>
      <property name="widgetLayout">4x3</property>
      <property name="widgetLabel">Recordings</property>
      <property name="widgetPath">pvr://recordings/tv/active/</property></item>
    <item name="music"><label>Music</label>
      <property name="widgetLayout">4x3</property>
      <property name="widgetLabel">Sources</property>
      <property name="widgetPath">musicdb://sources/</property></item>
    <item name="settings"><label>Settings</label>
      <property name="widgetLayout">1x1</property></item>
  </menu>
</menus>"""

TEMPLATES = """<templates>
  <propertyGroups>
    <propertyGroup name="artworkContent">
      <property name="widgetPath" from="widgetPath" />
      <var name="widgetAspect">
        <value condition="widgetLayout=4x3">landscape</value>
        <value>square</value>
      </var>
    </propertyGroup>
  </propertyGroups>
  <template include="testwidget" build="true" menu="mainmenu">
    <condition>widgetLayout=4x3</condition>
    <propertyGroup content="artworkContent"/>
    <controls>
      <control type="grouplist">
        <skinshortcuts>visibility</skinshortcuts>
        <left>500</left>
        {inner}
      </control>
    </controls>
  </template>
</templates>"""

PER_ITEM = '<control type="label"><label>$PROPERTY[widgetLabel]</label></control>'
RUNTIME = (
    '<control type="label">'
    "<label>$INFO[Container(9000).ListItem.Property(widgetLabel)]</label></control>"
)
PLAIN_INCLUDE = "<include>MyPanel</include>"


def build(tmp_path: Path, inner: str) -> list[ET.Element]:
    """Build the raw template, returning its top-level controls."""
    (tmp_path / "menus.xml").write_text(MENUS, encoding="utf-8")
    (tmp_path / "templates.xml").write_text(TEMPLATES.format(inner=inner), encoding="utf-8")

    menus = load_menus(str(tmp_path / "menus.xml"))
    schema = load_templates(str(tmp_path / "templates.xml"))
    out = TemplateBuilder(schema, menus.menus, None).build()

    include = next(
        i for i in out.iter("include") if i.get("name") == "skinshortcuts-template-testwidget"
    )
    return [c for c in include if c.tag == "control"]


def visibility(control: ET.Element) -> str:
    """The control's resolved <visible> text."""
    visible = control.find("visible")
    assert visible is not None and visible.text
    return visible.text


def condition_for(name: str) -> str:
    """Visibility condition the marker resolves to for an item."""
    return f"String.IsEqual(Container(9000).ListItem.Property(name),{name})"


def test_per_item_property_splits_the_output(tmp_path: Path) -> None:
    controls = build(tmp_path, PER_ITEM)
    assert len(controls) == len(MATCHING)
    assert [visibility(c) for c in controls] == [condition_for(n) for n in MATCHING]


def test_property_group_alone_stays_one_control(tmp_path: Path) -> None:
    controls = build(tmp_path, RUNTIME)
    assert len(controls) == 1
    assert visibility(controls[0]) == " | ".join(condition_for(n) for n in MATCHING)


def test_plain_kodi_include_passes_through(tmp_path: Path) -> None:
    controls = build(tmp_path, PLAIN_INCLUDE)
    assert len(controls) == 1
    assert [e.text for e in controls[0].iter("include")] == ["MyPanel"]
    assert visibility(controls[0]) == " | ".join(condition_for(n) for n in MATCHING)


def test_unmatched_item_is_left_out(tmp_path: Path) -> None:
    assert "settings" not in visibility(build(tmp_path, RUNTIME)[0])
