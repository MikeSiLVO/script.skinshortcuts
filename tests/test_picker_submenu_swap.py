"""Changing an item's shortcut reseeds its per-item submenu."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.manager import MenuManager
from skinshortcuts.models.menu import submenu_key


MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="seed">
      <label>Seed</label>
      <action>Noop</action>
    </item>
  </menu>
  <submenu name="musicvideos">
    <item name="mv-recent"><label>MV Recent</label><action>Noop</action></item>
  </submenu>
  <submenu name="pictures">
    <item name="pic-recent"><label>Pic Recent</label><action>Noop</action></item>
  </submenu>
</menus>
"""


def _setup(tmp_path: Path) -> tuple[Path, Path]:
    """Write the test menus.xml into a shortcuts folder; return it and a userdata path."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS_XML)
    return skin, tmp_path / "userdata.json"


def test_drop_per_item_submenu_removes_working_key(tmp_path: Path):
    """Dropping a seeded per-item submenu removes its working key."""
    skin, userdata = _setup(tmp_path)
    manager = MenuManager(skin, userdata_path=str(userdata))

    item = manager.working["mainmenu"].items[0]
    item.submenu = "musicvideos"
    manager.ensure_item_submenu("mainmenu", item)

    key = submenu_key("mainmenu", item.name)
    assert key in manager.working
    assert manager.working[key].items[0].name == "mv-recent"

    manager.drop_item_submenu("mainmenu", item.name)
    assert key not in manager.working


def test_picker_reseeds_submenu_after_shortcut_swap(tmp_path: Path):
    """The picker reseeds an item's submenu from the new template after a shortcut swap."""
    skin, userdata = _setup(tmp_path)
    manager = MenuManager(skin, userdata_path=str(userdata))

    item = manager.working["mainmenu"].items[0]

    item.submenu = "musicvideos"
    manager.set_submenu("mainmenu", item.name, "musicvideos")
    seeded_mv = manager.ensure_item_submenu("mainmenu", item)
    assert [i.name for i in seeded_mv.items] == ["mv-recent"]

    item.submenu = "pictures"
    manager.set_submenu("mainmenu", item.name, "pictures")
    manager.drop_item_submenu("mainmenu", item.name)
    seeded_pic = manager.ensure_item_submenu("mainmenu", item)
    assert [i.name for i in seeded_pic.items] == ["pic-recent"]


def test_drop_per_item_submenu_marks_changed(tmp_path: Path):
    """Dropping a per-item submenu marks the manager changed."""
    skin, userdata = _setup(tmp_path)
    manager = MenuManager(skin, userdata_path=str(userdata))

    item = manager.working["mainmenu"].items[0]
    item.submenu = "musicvideos"
    manager.ensure_item_submenu("mainmenu", item)
    manager._changed = False

    manager.drop_item_submenu("mainmenu", item.name)
    assert manager.has_changes()


def test_drop_per_item_submenu_noop_when_key_absent(tmp_path: Path):
    """Dropping a submenu that was never seeded is a no-op, leaving no change."""
    skin, userdata = _setup(tmp_path)
    manager = MenuManager(skin, userdata_path=str(userdata))
    manager._changed = False

    manager.drop_item_submenu("mainmenu", "nonexistent")
    assert not manager.has_changes()
