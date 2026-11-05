"""A presetGroup applies its first matching child, honoring the reference's condition and suffix."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.menu import load_menus
from skinshortcuts.loaders.template import load_templates

MENUS = """<menus><menu name="mainmenu" container="9000">
<item name="poster"><label>A</label><action>Noop</action><property name="widgetPath">a</property>
  <property name="widgetArt">Poster</property><property name="widgetType">movies</property></item>
<item name="movies"><label>B</label><action>Noop</action><property name="widgetPath">a</property>
  <property name="widgetType">movies</property></item>
<item name="plain"><label>C</label><action>Noop</action><property name="widgetPath">a</property>
</item>
<item name="nopath"><label>D</label><action>Noop</action>
  <property name="widgetArt">Poster</property></item>
<item name="ownColumns"><label>E</label><action>Noop</action>
  <property name="widgetPath">a</property><property name="columns">9</property></item>
<item name="second"><label>F</label><action>Noop</action><property name="widgetPath.2">b</property>
  <property name="widgetArt.2">Poster</property></item>
</menu></menus>"""

TEMPLATES = """<templates>
<presets>
  <preset name="posterLayout"><values layout="poster" columns="6" /></preset>
  <preset name="defaultLayout"><values layout="list" columns="1" /></preset>
</presets>
<presetGroups>
  <presetGroup name="widgetSet">
    <preset content="posterLayout" condition="widgetArt=Poster" />
    <values condition="widgetType=movies" layout="wide" columns="4" />
    <preset content="defaultLayout" />
  </presetGroup>
</presetGroups>
<template include="T" menu="mainmenu">
  {reference}
  <controls>
    <control type="group">
      <name>$PROPERTY[name]</name><layout>$PROPERTY[layout]</layout>
      <columns>$PROPERTY[columns]</columns>
    </control>
  </controls>
</template>
</templates>"""


def layouts(tmp_path: Path, reference: str) -> dict[str, tuple[str | None, str | None]]:
    """Layout and columns built for each item, by item name, for one presetGroup line."""
    (tmp_path / "menus.xml").write_text(MENUS, encoding="utf-8")
    (tmp_path / "templates.xml").write_text(TEMPLATES.format(reference=reference), "utf-8")
    menus = load_menus(str(tmp_path / "menus.xml"))
    root = TemplateBuilder(load_templates(str(tmp_path / "templates.xml")), menus.menus).build()
    return {
        control.findtext("name", ""): (control.findtext("layout"), control.findtext("columns"))
        for control in root.iter("control")
    }


@pytest.mark.parametrize(
    ("reference", "expected"),
    [
        (
            '<presetGroup content="widgetSet" condition="widgetPath" />',
            {
                "poster": ("poster", "6"),
                "movies": ("wide", "4"),
                "plain": ("list", "1"),
                "nopath": (None, None),
                "ownColumns": ("list", "9"),
                "second": (None, None),
            },
        ),
        (
            '<presetGroup content="widgetSet" suffix=".2" condition="widgetPath" />',
            {
                "poster": (None, None),
                "movies": (None, None),
                "plain": (None, None),
                "nopath": (None, None),
                "ownColumns": (None, "9"),
                "second": ("poster", "6"),
            },
        ),
    ],
    ids=["plain", "suffixed"],
)
def test_first_matching_child_applies(
    tmp_path: Path, reference: str, expected: dict[str, tuple[str | None, str | None]]
) -> None:
    """First matching child applies, inline values included; an item's own values are kept."""
    assert layouts(tmp_path, reference) == expected
