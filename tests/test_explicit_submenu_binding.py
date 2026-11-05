"""Submenu binding is explicit; an item name matching a submenu template does not bind it."""

from __future__ import annotations

import json
from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig

MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies" submenu="movies">
      <label>Movies</label>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
    </item>
    <item name="settings">
      <label>Settings</label>
      <action>ActivateWindow(Settings)</action>
    </item>
  </menu>

  <menu name="powermenu">
    <item name="reboot">
      <label>Reboot</label>
      <action>Reboot</action>
    </item>
    <item name="settings">
      <label>Settings</label>
      <action>ActivateWindow(Settings)</action>
    </item>
  </menu>

  <submenu name="movies">
    <item name="recent">
      <label>Recent</label>
      <action>Noop</action>
    </item>
  </submenu>

  <submenu name="settings">
    <item name="system">
      <label>System</label>
      <action>ActivateWindow(SystemSettings)</action>
    </item>
  </submenu>
</menus>
"""


def _setup(tmp_path: Path) -> Path:
    """Write the test menus.xml into a shortcuts folder and return it."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS_XML)
    return skin


def _names(root) -> list[str]:
    """Names of every include in the build."""
    return [inc.get("name", "") for inc in root.findall("include")]


def _parents(root, include_name: str) -> set[str]:
    """Parent values on the items of an include of a given name."""
    for inc in root.findall("include"):
        if inc.get("name") != include_name:
            continue
        result: set[str] = set()
        for item in inc.findall("item"):
            for prop in item.findall("property"):
                if prop.get("name") == "parent" and prop.text:
                    result.add(prop.text)
        return result
    return set()


def test_no_combined_submenu_for_menu_without_explicit_bindings(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    assert "skinshortcuts-powermenu-submenu" not in _names(root)


def test_combined_submenu_only_contains_explicit_bindings(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    assert "skinshortcuts-mainmenu-submenu" in _names(root)
    assert _parents(root, "skinshortcuts-mainmenu-submenu") == {"movies"}


def test_per_template_include_only_emits_when_explicitly_referenced(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    assert "skinshortcuts-movies" in _names(root)
    assert "skinshortcuts-settings" not in _names(root)


def test_user_added_submenu_persists_without_submenu_attr(tmp_path: Path):
    """Userdata items at an implicit submenu key reach the combined submenu."""
    skin = _setup(tmp_path)
    userdata = tmp_path / "userdata.json"
    payload = {
        "menus": {
            "mainmenu/settings": {
                "items": [
                    {
                        "name": "custom",
                        "label": "Custom",
                        "actions": [{"action": "Noop"}],
                        "icon": "DefaultShortcut.png",
                        "is_new": True,
                        "position": 0,
                    }
                ]
            }
        }
    }
    userdata.write_text(json.dumps(payload))

    config = SkinConfig.load(skin, load_user=True, userdata_path=str(userdata))
    root = IncludesBuilder(
        config.menus, templates=config.templates, userdata=config.userdata
    ).build()

    parents = _parents(root, "skinshortcuts-mainmenu-submenu")
    assert "settings" in parents
    assert "movies" in parents
