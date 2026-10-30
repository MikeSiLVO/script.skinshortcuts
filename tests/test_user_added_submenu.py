"""Per-item submenus on items that don't resolve to a default template must persist."""

from __future__ import annotations

import json
from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig
from skinshortcuts.manager import MenuManager


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


def _setup(tmp_path: Path) -> tuple[Path, Path]:
    """Write the test menus.xml into a shortcuts folder; return it and a userdata path."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS_XML)
    return skin, tmp_path / "userdata.json"


def _write_userdata_with_user_submenu(userdata_path: Path, parent_item_id: str) -> None:
    """Write userdata with a user mainmenu item holding a two-item submenu."""
    payload = {
        "menus": {
            "mainmenu": {
                "items": [
                    {
                        "name": parent_item_id,
                        "label": "My Custom",
                        "actions": [{"action": "Noop"}],
                        "icon": "DefaultShortcut.png",
                        "is_new": True,
                        "position": 1,
                    }
                ]
            },
            f"mainmenu/{parent_item_id}": {
                "items": [
                    {
                        "name": "sub-aa111111",
                        "label": "Sub A",
                        "actions": [{"action": "ActivateWindow(Videos)"}],
                        "icon": "DefaultShortcut.png",
                        "is_new": True,
                        "position": 0,
                    },
                    {
                        "name": "sub-bb222222",
                        "label": "Sub B",
                        "actions": [{"action": "ActivateWindow(Music)"}],
                        "icon": "DefaultShortcut.png",
                        "is_new": True,
                        "position": 1,
                    },
                ]
            },
        }
    }
    userdata_path.write_text(json.dumps(payload))


def test_user_added_submenu_loads_into_config(tmp_path: Path):
    skin, userdata = _setup(tmp_path)
    parent_id = "user-abc12345"
    _write_userdata_with_user_submenu(userdata, parent_id)

    config = SkinConfig.load(skin, load_user=True, userdata_path=str(userdata))

    instance_key = f"mainmenu/{parent_id}"
    instance = config.get_menu(instance_key)
    assert instance is not None, (
        f"Expected per-item submenu '{instance_key}' in config.menus"
    )
    assert [i.name for i in instance.items] == ["sub-aa111111", "sub-bb222222"]


def test_user_added_submenu_emits_includes(tmp_path: Path):
    """The combined mainmenu-submenu include must list user-added submenu items."""
    skin, userdata = _setup(tmp_path)
    parent_id = "user-abc12345"
    _write_userdata_with_user_submenu(userdata, parent_id)

    config = SkinConfig.load(skin, load_user=True, userdata_path=str(userdata))
    root = IncludesBuilder(
        config.menus,
        templates=config.templates,
        userdata=config.userdata,
    ).build()

    combined = next(
        (inc for inc in root.findall("include")
         if inc.get("name") == "skinshortcuts-mainmenu-submenu"),
        None,
    )
    assert combined is not None, "skinshortcuts-mainmenu-submenu include missing"

    parents = [
        next((p.text for p in item.findall("property") if p.get("name") == "parent"), None)
        for item in combined.findall("item")
    ]
    assert parents.count(parent_id) == 2, (
        f"Expected two submenu items linked to {parent_id}, got parents={parents}"
    )


def test_save_does_not_wipe_user_added_submenu(tmp_path: Path):
    """Opening manager and saving (e.g. after any other edit) must not drop the entry."""
    skin, userdata = _setup(tmp_path)
    parent_id = "user-abc12345"
    _write_userdata_with_user_submenu(userdata, parent_id)

    manager = MenuManager(skin, userdata_path=str(userdata))
    instance_key = f"mainmenu/{parent_id}"
    assert instance_key in manager.working, (
        "Manager should load per-item submenu into working storage"
    )

    manager._changed = True
    assert manager.save()

    saved = json.loads(userdata.read_text())
    assert instance_key in saved.get("menus", {}), (
        f"Save wiped user-added submenu entry. Got: {list(saved.get('menus', {}).keys())}"
    )
    saved_items = saved["menus"][instance_key]["items"]
    assert [i["name"] for i in saved_items] == ["sub-aa111111", "sub-bb222222"]


def test_orphaned_menu_cleanup_keeps_active_user_submenu(tmp_path: Path):
    """The orphan cleanup must not consider an active user-item's submenu orphaned."""
    skin, userdata = _setup(tmp_path)
    parent_id = "user-abc12345"
    _write_userdata_with_user_submenu(userdata, parent_id)

    manager = MenuManager(skin, userdata_path=str(userdata))
    manager._cleanup_orphaned_menus()

    instance_key = f"mainmenu/{parent_id}"
    assert instance_key in manager.working, (
        "Cleanup should keep per-item submenu while parent item still exists"
    )


def test_removing_user_item_drops_its_submenu_on_save(tmp_path: Path):
    skin, userdata = _setup(tmp_path)
    parent_id = "user-abc12345"
    _write_userdata_with_user_submenu(userdata, parent_id)

    manager = MenuManager(skin, userdata_path=str(userdata))
    instance_key = f"mainmenu/{parent_id}"
    assert instance_key in manager.working

    manager.remove_item("mainmenu", parent_id)
    assert manager.save()

    saved = json.loads(userdata.read_text())
    assert instance_key not in saved.get("menus", {}), (
        "Removing the parent should drop its per-item submenu"
    )
