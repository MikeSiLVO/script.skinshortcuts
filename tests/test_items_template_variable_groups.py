"""An items template honors a nested <variableGroup>."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig
from skinshortcuts.loaders.template import load_templates


MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu" container="9000">
    <item name="movies">
      <label>Movies</label>
      <action>Noop</action>
    </item>
  </menu>
  <submenu name="movies.widgets" type="widgets">
    <item name="recent">
      <label>Recent</label>
      <action>Noop</action>
      <property name="widgetPath">videodb://recent</property>
    </item>
    <item name="popular">
      <label>Popular</label>
      <action>Noop</action>
      <property name="widgetPath">videodb://popular</property>
    </item>
  </submenu>
</menus>
"""

TEMPLATES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <variables>
    <variable name="widgetSlot" output="WidgetSlot$PROPERTY[id]">
      <value>$PROPERTY[widgetPath]</value>
    </variable>

    <variableGroup name="widgetItemVars">
      <variable content="widgetSlot" />
    </variableGroup>
  </variables>

  <template include="widgets" menu="mainmenu">
    <controls>
      <control type="group">
        <skinshortcuts insert="widgets">items</skinshortcuts>
      </control>
    </controls>
  </template>

  <template items="widgets" source="widgets">
    <property name="id" from="index" />
    <controls>
      <control type="image" />
    </controls>
    <variableGroup content="widgetItemVars" />
  </template>
</templates>
"""


def _setup(tmp_path: Path) -> Path:
    """Write the test menus and templates into a shortcuts folder and return it."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS_XML)
    (skin / "templates.xml").write_text(TEMPLATES_XML)
    return skin


def test_items_template_variable_group_parsed(tmp_path: Path):
    skin = _setup(tmp_path)
    schema = load_templates(skin / "templates.xml")
    items_def = schema.get_items_template("widgets")

    assert items_def is not None
    assert len(items_def.variable_groups) == 1
    assert items_def.variable_groups[0].name == "widgetItemVars"


def test_items_template_variable_group_emits_per_iteration_variables(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    builder = IncludesBuilder(
        config.menus, templates=config.templates, property_schema=config.property_schema
    )
    root = builder.build()

    variables = root.findall("variable")
    names = {v.get("name", "") for v in variables}

    assert "WidgetSlot1" in names, f"missing per-item variable WidgetSlot1; got {names}"
    assert "WidgetSlot2" in names, f"missing per-item variable WidgetSlot2; got {names}"

    by_name = {v.get("name"): v for v in variables}
    assert "videodb://recent" in (by_name["WidgetSlot1"].findtext("value") or "")
    assert "videodb://popular" in (by_name["WidgetSlot2"].findtext("value") or "")


def test_items_template_variable_output_resolves_parent_index(tmp_path: Path):
    """Variable output uses $PARENT[index] of the parent menu item."""
    menus_xml = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu" container="9000">
    <item name="movies"><label>Movies</label><action>Noop</action></item>
    <item name="tvshows"><label>TVShows</label><action>Noop</action></item>
  </menu>
  <submenu name="movies.widgets" type="widgets">
    <item name="recent"><label>Recent</label><action>Noop</action></item>
  </submenu>
  <submenu name="tvshows.widgets" type="widgets">
    <item name="recent"><label>Recent</label><action>Noop</action></item>
  </submenu>
</menus>
"""
    templates_xml = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <variables>
    <variable name="widgetContainer" output="WidgetContainer_C$MATH[$PARENT[index] * 1000 + 301]">
      <value>$PROPERTY[id]</value>
    </variable>
    <variableGroup name="widgetItemVars">
      <variable content="widgetContainer" />
    </variableGroup>
  </variables>

  <template include="widgets" menu="mainmenu">
    <controls>
      <control type="group">
        <skinshortcuts insert="widgets">items</skinshortcuts>
      </control>
    </controls>
  </template>

  <template items="widgets" source="widgets">
    <property name="id" from="index" />
    <controls><control type="image" /></controls>
    <variableGroup content="widgetItemVars" />
  </template>
</templates>
"""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(menus_xml)
    (skin / "templates.xml").write_text(templates_xml)

    config = SkinConfig.load(skin, load_user=False)
    builder = IncludesBuilder(
        config.menus, templates=config.templates, property_schema=config.property_schema
    )
    root = builder.build()

    names = sorted(v.get("name", "") for v in root.findall("variable"))
    assert "WidgetContainer_C1301" in names, f"missing parent-resolved var; got {names}"
    assert "WidgetContainer_C2301" in names, f"missing parent-resolved var; got {names}"


def test_items_template_without_variable_group_still_works(tmp_path: Path):
    schema_xml = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <template items="widgets">
    <property name="id" from="index" />
    <controls><control type="image" /></controls>
  </template>
</templates>
"""
    path = tmp_path / "templates.xml"
    path.write_text(schema_xml)
    schema = load_templates(path)
    items_def = schema.get_items_template("widgets")
    assert items_def is not None
    assert items_def.variable_groups == []
