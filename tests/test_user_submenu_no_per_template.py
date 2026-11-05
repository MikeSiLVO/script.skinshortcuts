"""User-added submenus on items with no menus.xml template must not emit per-template includes."""

from __future__ import annotations

import json
from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig

MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="home">
      <label>Home</label>
      <action>ActivateWindow(Home)</action>
    </item>
  </menu>
</menus>
"""


def _setup(tmp_path: Path, parent_id: str) -> tuple[Path, Path]:
    """Write the test menus.xml and userdata with a user item's submenu; return both paths."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS_XML)

    userdata = tmp_path / "userdata.json"
    payload = {
        "menus": {
            "mainmenu": {
                "items": [
                    {
                        "name": parent_id,
                        "label": "Brand New",
                        "actions": [{"action": "Noop"}],
                        "icon": "DefaultShortcut.png",
                        "is_new": True,
                        "position": 1,
                    }
                ]
            },
            f"mainmenu/{parent_id}": {
                "items": [
                    {
                        "name": "sub-aa",
                        "label": "Sub A",
                        "actions": [{"action": "ActivateWindow(Videos)"}],
                        "icon": "DefaultShortcut.png",
                        "is_new": True,
                        "position": 0,
                    },
                ]
            },
        }
    }
    userdata.write_text(json.dumps(payload))
    return skin, userdata


def _names(root) -> list[str]:
    """Names of every include in the build."""
    return [inc.get("name", "") for inc in root.findall("include")]


def test_user_created_submenu_does_not_emit_per_template_include(tmp_path: Path):
    parent_id = "user-abc12345"
    skin, userdata = _setup(tmp_path, parent_id)

    config = SkinConfig.load(skin, load_user=True, userdata_path=str(userdata))
    root = IncludesBuilder(
        config.menus,
        templates=config.templates,
        userdata=config.userdata,
    ).build()

    names = _names(root)
    assert f"skinshortcuts-{parent_id}" not in names
    assert "skinshortcuts-mainmenu-submenu" in names
