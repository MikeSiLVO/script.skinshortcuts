"""End-to-end pipeline test: <action condition> on a grouping shortcut survives the picker."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig
from skinshortcuts.loaders.menu import load_groupings, load_menus
from skinshortcuts.manager import MenuManager


MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="test">
      <label>test</label>
      <action condition="true">First action</action>
      <action condition="String.IsEqual(ListItem.Label,hello)">Second action</action>
      <action condition="Container.Content(tvshows)">Third action</action>
    </item>
  </menu>

  <groupings>
    <group name="common" label="Common">
      <shortcut name="test" label="Test" icon="DefaultFavourites.png">
        <action condition="true">First action</action>
        <action condition="String.IsEqual(ListItem.Label,hello)">Second action</action>
        <action condition="Container.Content(tvshows)">Third action</action>
      </shortcut>
      <shortcut name="plain" label="Plain">
        <action>Reboot</action>
      </shortcut>
    </group>
  </groupings>
</menus>
"""


def _setup_skin(tmp_path: Path) -> tuple[Path, Path]:
    """Write the test menus.xml into a shortcuts folder; return it and a userdata path."""
    skin_dir = tmp_path / "shortcuts"
    skin_dir.mkdir()
    (skin_dir / "menus.xml").write_text(MENUS_XML)
    return skin_dir, tmp_path / "userdata.json"


def _find_shortcut(skin_dir: Path, name: str):
    """Find the shortcut of a given name in the first group."""
    groups = load_groupings(skin_dir / "menus.xml")
    return next(s for s in groups[0].items if getattr(s, "name", "") == name)


def _build_includes_xml(skin_dir: Path, userdata_path: Path) -> str:
    """Build includes with user changes loaded and return them as XML text."""
    config = SkinConfig.load(skin_dir, load_user=True, userdata_path=str(userdata_path))
    builder = IncludesBuilder(config.menus, templates=config.templates)
    return ET.tostring(builder.build(), encoding="unicode")


def test_grouping_shortcut_keeps_action_conditions(tmp_path: Path):
    skin_dir, _ = _setup_skin(tmp_path)

    shortcut = _find_shortcut(skin_dir, "test")

    assert [(a.action, a.condition) for a in shortcut.actions] == [
        ("First action", "true"),
        ("Second action", "String.IsEqual(ListItem.Label,hello)"),
        ("Third action", "Container.Content(tvshows)"),
    ]
    assert shortcut.action == "First action"


def test_picked_shortcut_emits_conditional_onclicks(tmp_path: Path):
    skin_dir, userdata_path = _setup_skin(tmp_path)

    shortcut = _find_shortcut(skin_dir, "test")
    manager = MenuManager(skin_dir, userdata_path=str(userdata_path))
    manager.set_action("mainmenu", "test", shortcut.actions)

    assert manager.save()

    output = _build_includes_xml(skin_dir, userdata_path)

    assert '<onclick condition="true">First action</onclick>' in output
    assert (
        '<onclick condition="String.IsEqual(ListItem.Label,hello)">Second action</onclick>'
        in output
    )
    assert (
        '<onclick condition="Container.Content(tvshows)">Third action</onclick>' in output
    )
    assert '<property name="action">First action</property>' in output


def test_unconditional_shortcut_emits_bare_onclick(tmp_path: Path):
    skin_dir, userdata_path = _setup_skin(tmp_path)

    shortcut = _find_shortcut(skin_dir, "plain")
    manager = MenuManager(skin_dir, userdata_path=str(userdata_path))
    manager.set_action("mainmenu", "test", shortcut.actions)

    assert manager.save()

    output = _build_includes_xml(skin_dir, userdata_path)

    assert "<onclick>Reboot</onclick>" in output


def test_picked_actions_do_not_alias_the_grouping(tmp_path: Path):
    skin_dir, userdata_path = _setup_skin(tmp_path)

    shortcut = _find_shortcut(skin_dir, "test")
    manager = MenuManager(skin_dir, userdata_path=str(userdata_path))
    manager.set_action("mainmenu", "test", shortcut.actions)

    item = manager.get_menu_items("mainmenu")[0]
    item.actions[0].action = "Changed"

    assert shortcut.actions[0].action == "First action"


def test_menu_item_action_conditions_round_trip(tmp_path: Path):
    """The skin default already carried conditions; a save must not flatten them."""
    skin_dir, userdata_path = _setup_skin(tmp_path)

    menus = load_menus(skin_dir / "menus.xml")
    mainmenu = next(m for m in menus.menus if m.name == "mainmenu")
    item = mainmenu.get_item("test")
    assert item is not None
    assert [a.condition for a in item.actions] == [
        "true",
        "String.IsEqual(ListItem.Label,hello)",
        "Container.Content(tvshows)",
    ]

    manager = MenuManager(skin_dir, userdata_path=str(userdata_path))
    manager.set_label("mainmenu", "test", "Renamed")
    assert manager.save()

    output = _build_includes_xml(skin_dir, userdata_path)
    assert '<onclick condition="true">First action</onclick>' in output
