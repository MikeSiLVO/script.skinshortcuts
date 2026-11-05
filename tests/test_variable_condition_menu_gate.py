"""A variable's condition attribute gates emission by menu and never reaches the output."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig

MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu" container="9000">
    <item name="movies" submenu="moviesub">
      <label>Movies</label>
      <action>Noop</action>
      <property name="backgroundType">playlist</property>
      <property name="backgroundPath">special://x/movies.xsp</property>
    </item>
  </menu>
  <submenu name="moviesub">
    <item name="recent">
      <label>Recent</label>
      <action>Noop</action>
      <property name="backgroundType">playlist</property>
      <property name="backgroundPath">special://x/recent.xsp</property>
    </item>
  </submenu>
</menus>
"""

TEMPLATES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <template include="pl">
    <condition>backgroundType=playlist</condition>
    <variables>
      <variable name="MainVar" condition="menu=mainmenu">
        <value>$PROPERTY[name]</value>
      </variable>
      <variable name="SubVar" condition="menu~mainmenu/">
        <value>$PROPERTY[name]</value>
      </variable>
    </variables>
    <controls>
      <control type="image" />
    </controls>
  </template>
</templates>
"""


def _build(tmp_path: Path):
    """Build includes for the test menus and templates."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS_XML)
    (skin / "templates.xml").write_text(TEMPLATES_XML)
    config = SkinConfig.load(skin, load_user=False)
    builder = IncludesBuilder(
        config.menus, templates=config.templates, property_schema=config.property_schema
    )
    return builder.build()


def test_menu_condition_gates_emission(tmp_path: Path):
    root = _build(tmp_path)
    by_name = {v.get("name"): v for v in root.findall("variable")}

    assert "MainVar" in by_name, "MainVar should emit for the mainmenu item"
    assert "SubVar" in by_name, "SubVar should emit for the submenu item"

    main_values = [v.text for v in by_name["MainVar"].findall("value")]
    sub_values = [v.text for v in by_name["SubVar"].findall("value")]
    assert main_values == ["movies"], f"MainVar leaked a submenu item: {main_values}"
    assert sub_values == ["recent"], f"SubVar leaked a main item: {sub_values}"


def test_condition_attribute_not_emitted(tmp_path: Path):
    root = _build(tmp_path)
    for var in root.findall("variable"):
        assert "condition" not in var.attrib, (
            f"build-only condition= leaked into emitted <variable name="
            f"'{var.get('name')}'>"
        )
