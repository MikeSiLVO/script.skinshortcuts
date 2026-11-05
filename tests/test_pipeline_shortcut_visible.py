"""A picked shortcut's visible condition survives save, reload and build into the output XML."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig
from skinshortcuts.loaders.menu import load_groupings
from skinshortcuts.manager import MenuManager
from skinshortcuts.models.menu import Action

MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="powermenu">
    <item name="existing">
      <label>Existing</label>
      <action>Noop</action>
    </item>
  </menu>

  <groupings>
    <shortcut name="cancel-alarm" label="Cancel Alarm">
      <action>CancelAlarm(shutdowntimer)</action>
      <visible>System.HasAlarm(shutdowntimer)</visible>
    </shortcut>
    <shortcut name="reboot" label="Reboot">
      <action>Reboot</action>
    </shortcut>
  </groupings>
</menus>
"""


def _setup_skin(tmp_path: Path) -> tuple[Path, Path]:
    """Write the test menus.xml into a shortcuts folder; return it and a userdata path."""
    skin_dir = tmp_path / "shortcuts"
    skin_dir.mkdir()
    (skin_dir / "menus.xml").write_text(MENUS_XML)
    userdata_path = tmp_path / "userdata.json"
    return skin_dir, userdata_path


def _apply_shortcut_to_item(manager: MenuManager, menu_id: str, item_name: str, shortcut) -> None:
    """Apply a shortcut to an item with the manager calls the dialog's shortcut picker makes."""
    manager.set_label(menu_id, item_name, shortcut.label)
    manager.set_action(
        menu_id, item_name, shortcut.actions or [Action(action=shortcut.resolved_action())]
    )
    if shortcut.icon:
        manager.set_icon(menu_id, item_name, shortcut.icon)
    if shortcut.item_visible:
        manager.set_visible(menu_id, item_name, shortcut.item_visible)


def _build_includes_xml(skin_dir: Path, userdata_path: Path) -> str:
    """Build includes with user changes loaded and return them as XML text."""
    config = SkinConfig.load(skin_dir, load_user=True, userdata_path=str(userdata_path))
    builder = IncludesBuilder(config.menus, templates=config.templates)
    return ET.tostring(builder.build(), encoding="unicode")


def test_picked_shortcut_visible_persists_through_pipeline(tmp_path: Path):
    skin_dir, userdata_path = _setup_skin(tmp_path)

    groupings = load_groupings(skin_dir / "menus.xml")
    cancel_alarm = next(s for s in groupings if getattr(s, "name", "") == "cancel-alarm")
    assert cancel_alarm.item_visible == "System.HasAlarm(shutdowntimer)"

    manager = MenuManager(skin_dir, userdata_path=str(userdata_path))

    new_item = manager.add_item("powermenu", after_index=0)
    _apply_shortcut_to_item(manager, "powermenu", new_item.name, cancel_alarm)

    assert manager.save()
    assert userdata_path.exists()

    output = _build_includes_xml(skin_dir, userdata_path)

    assert '<item id="2">' in output
    assert "<visible>System.HasAlarm(shutdowntimer)</visible>" in output
    assert "CancelAlarm(shutdowntimer)" in output


def test_picked_shortcut_without_item_visible_emits_no_visible(tmp_path: Path):
    skin_dir, userdata_path = _setup_skin(tmp_path)

    groupings = load_groupings(skin_dir / "menus.xml")
    reboot = next(s for s in groupings if getattr(s, "name", "") == "reboot")

    manager = MenuManager(skin_dir, userdata_path=str(userdata_path))

    new_item = manager.add_item("powermenu", after_index=0)
    _apply_shortcut_to_item(manager, "powermenu", new_item.name, reboot)

    assert manager.save()

    output = _build_includes_xml(skin_dir, userdata_path)

    assert "Reboot" in output
    assert "<visible>" not in output


def test_existing_item_picks_shortcut_with_visible(tmp_path: Path):
    skin_dir, userdata_path = _setup_skin(tmp_path)

    groupings = load_groupings(skin_dir / "menus.xml")
    cancel_alarm = next(s for s in groupings if getattr(s, "name", "") == "cancel-alarm")

    manager = MenuManager(skin_dir, userdata_path=str(userdata_path))

    _apply_shortcut_to_item(manager, "powermenu", "existing", cancel_alarm)

    assert manager.save()

    output = _build_includes_xml(skin_dir, userdata_path)

    assert "<visible>System.HasAlarm(shutdowntimer)</visible>" in output
