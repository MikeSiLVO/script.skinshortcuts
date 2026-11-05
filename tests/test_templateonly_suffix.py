"""A templateonly base property suppresses its numeric slot variants, not its named ones."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig

MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies">
      <label>Movies</label>
      <action>Noop</action>
      <property name="widgetSortby">title</property>
      <property name="widgetSortby.2">year</property>
      <property name="widgetSortby.backgroundWidget">rating</property>
    </item>
  </menu>
</menus>
"""

PROPERTIES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <property name="widgetSortby" templateonly="true" />
  <property name="widgetSortby.backgroundWidget" />
</properties>
"""


def _movie_props(tmp_path: Path) -> dict[str, str]:
    """Properties the built mainmenu include gives movies under the test skin."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS_XML)
    (skin / "properties.xml").write_text(PROPERTIES_XML)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(
        config.menus, templates=config.templates, property_schema=config.property_schema
    ).build()
    for inc in root.findall("include"):
        if inc.get("name") != "skinshortcuts-mainmenu":
            continue
        for item in inc.findall("item"):
            props = {p.get("name"): (p.text or "") for p in item.findall("property")}
            if props.get("name") == "movies":
                return props
    return {}


def test_base_and_numeric_variant_suppressed(tmp_path: Path):
    props = _movie_props(tmp_path)
    assert "widgetSortby" not in props
    assert "widgetSortby.2" not in props


def test_named_variant_not_suppressed(tmp_path: Path):
    props = _movie_props(tmp_path)
    assert props.get("widgetSortby.backgroundWidget") == "rating"
