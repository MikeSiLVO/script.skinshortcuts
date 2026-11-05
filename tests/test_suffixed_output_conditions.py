"""A suffixed template output reads its own slot in every condition form, fallbacks included."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from skinshortcuts.config import SkinConfig

MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="split">
      <label>Split</label>
      <action>Noop</action>
      <property name="widgetPath">a://</property>
      <property name="widgetType">albums</property>
      <property name="panel">true</property>
      <property name="widgetPath.2">b://</property>
      <property name="widgetType.2">episodes</property>
    </item>
    <item name="first">
      <label>First</label>
      <action>Noop</action>
      <property name="widgetPath">a://</property>
      <property name="widgetType">movies</property>
    </item>
  </menu>
</menus>
"""

PROPERTIES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <property name="widgetArt" templateonly="true" />
  <fallbacks>
    <fallback property="widgetArt">
      <when condition="widgetType IN albums,songs">Square</when>
      <when condition="$EXP[IsVideo]">Landscape</when>
      <default>Fanart</default>
    </fallback>
  </fallbacks>
</properties>
"""

TEMPLATES_XML = ("""<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <expressions>
    <expression name="IsVideo">widgetType=movies | widgetType=episodes</expression>
  </expressions>
  <template menu="mainmenu">
    <output include="w1" idprefix="81" />
    <output include="w2" idprefix="82" suffix=".2" />
    <condition>widgetPath</condition>
    <condition>widgetType=movies | widgetType=episodes | widgetType=albums</condition>
    <property name="art" from="widgetArt" />
    <property name="kind" condition="widgetType EQUALS movies OR widgetType EQUALS episodes">"""
    """video</property>
    <property name="kind" condition="NOT widgetType IN movies,episodes">music</property>
    <controls>
      <control type="label">
        <label>$PROPERTY[name]:$PROPERTY[art]:$PROPERTY[kind]</label>
      </control>
    </controls>
  </template>
</templates>
""")

MARKERS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <propertyGroups>
    <propertyGroup name="tags">
      <property name="tag" condition="kind=video">v</property>
      <property name="tag">m</property>
    </propertyGroup>
  </propertyGroups>
  <presets>
    <preset name="sizes">
      <values condition="kind=video" size="wide" />
      <values size="tall" />
    </preset>
  </presets>
  <includes>
    <include name="Panel"><control type="label"><label>$PROPERTY[name]:panel</label></control>
    </include>
    <include name="Video"><control type="label"><label>$PROPERTY[name]:video</label></control>
    </include>
  </includes>
  <template menu="mainmenu">
    <output include="w1" idprefix="81" />
    <output include="w2" idprefix="82" suffix=".2" />
    <property name="kind" condition="widgetType IN movies,episodes">video</property>
    <property name="kind">music</property>
    <propertyGroup content="tags" />
    <preset content="sizes" />
    <controls>
      <control type="group">
        <label>$PROPERTY[name]:$PROPERTY[tag]:$PROPERTY[size]</label>
        <skinshortcuts include="Panel" condition="panel" />
        <skinshortcuts include="Video" condition="kind=video" />
      </control>
    </controls>
  </template>
</templates>
"""


def _labels(tmp_path: Path, templates: str = TEMPLATES_XML) -> dict[str, list[str]]:
    """Sorted labels the w1 and w2 outputs build from the test skin files."""
    for name, text in (
        ("menus.xml", MENUS_XML),
        ("properties.xml", PROPERTIES_XML),
        ("templates.xml", templates),
    ):
        (tmp_path / name).write_text(text)
    config = SkinConfig.load(tmp_path, load_user=False)
    out = tmp_path / "includes.xml"
    config.build_includes(out)
    root = ET.parse(out).getroot()
    result = {}
    for include in root.findall("include"):
        name = include.get("name", "")
        if name.endswith(("-w1", "-w2")):
            result[name[-2:]] = sorted(e.text or "" for e in include.iter("label"))
    return result


def test_each_output_reads_its_own_slot(tmp_path):
    labels = _labels(tmp_path)
    assert labels["w1"] == ["first:Landscape:video", "split:Square:music"]
    assert labels["w2"] == ["split:Landscape:video"]


def test_conditions_read_template_values_as_set(tmp_path):
    """Markers, propertyGroups and presets in a suffixed output read that slot's template values."""
    labels = _labels(tmp_path, MARKERS_XML)
    assert labels["w1"] == ["first:v:wide", "first:video", "split:m:tall", "split:panel"]
    assert labels["w2"] == ["first:m:tall", "split:v:wide", "split:video"]
