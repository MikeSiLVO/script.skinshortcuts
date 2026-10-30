"""Fallback rules resolve against the item's widget properties, first match winning."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from skinshortcuts.config import SkinConfig


WIDGETS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<widgets>
  <widget name="w-movies" label="Movies" type="movies" target="videos" source="library">
    <path>videodb://movies/titles/</path>
  </widget>
  <widget name="w-albums" label="Albums" type="albums" target="music" source="library">
    <path>musicdb://albums/</path>
  </widget>
  <widget name="w-addon" label="Addon" type="movies" target="videos" source="addon">
    <path>plugin://plugin.video.example/</path>
  </widget>
</widgets>
"""

PROPERTIES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <property name="widget" type="widget" />
  <property name="widgetSortby" templateonly="true" />
  <fallbacks>
    <fallback property="widgetSortby">
      <when condition="widgetType=albums">artist</when>
      <when condition="widgetSource=addon">none</when>
      <when condition="widgetTarget=videos">dateadded</when>
      <default>title</default>
    </fallback>
  </fallbacks>
  <buttons>
    <button id="309" property="widget" />
  </buttons>
</properties>
"""

MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies">
      <label>Movies</label>
      <action>Noop</action>
      <property name="widget">w-movies</property>
    </item>
    <item name="albums">
      <label>Albums</label>
      <action>Noop</action>
      <property name="widget">w-albums</property>
    </item>
    <item name="addon">
      <label>Addon</label>
      <action>Noop</action>
      <property name="widget">w-addon</property>
    </item>
    <item name="bare">
      <label>Bare</label>
      <action>Noop</action>
    </item>
  </menu>
</menus>
"""

TEMPLATES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <template include="test" menu="mainmenu">
    <property name="sortby" from="widgetSortby" />
    <controls>
      <control type="label">
        <label>$PROPERTY[name]=$PROPERTY[sortby]</label>
      </control>
    </controls>
  </template>
</templates>
"""


def test_fallbacks_key_off_widget_properties(tmp_path: Path):
    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()
    (shortcuts / "widgets.xml").write_text(WIDGETS_XML)
    (shortcuts / "properties.xml").write_text(PROPERTIES_XML)
    (shortcuts / "menus.xml").write_text(MENUS_XML)
    (shortcuts / "templates.xml").write_text(TEMPLATES_XML)

    out = tmp_path / "includes.xml"
    SkinConfig.load(shortcuts, load_user=False).build_includes(out)

    resolved = dict(
        label.text.split("=", 1)
        for label in ET.parse(out).getroot().iter("label")
        if label.text and "=" in label.text
    )

    assert resolved == {
        "movies": "dateadded",
        "albums": "artist",
        "addon": "none",
        "bare": "title",
    }


def test_item_value_in_other_case_skips_the_fallback(tmp_path: Path):
    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()
    (shortcuts / "widgets.xml").write_text(WIDGETS_XML)
    (shortcuts / "properties.xml").write_text(PROPERTIES_XML)
    (shortcuts / "menus.xml").write_text(MENUS_XML.replace(
        '<property name="widget">w-movies</property>',
        '<property name="widget">w-movies</property><property name="widgetsortby">year</property>',
    ))
    (shortcuts / "templates.xml").write_text(TEMPLATES_XML)

    out = tmp_path / "includes.xml"
    SkinConfig.load(shortcuts, load_user=False).build_includes(out)

    labels = [label.text for label in ET.parse(out).getroot().iter("label")]
    assert "movies=year" in labels
