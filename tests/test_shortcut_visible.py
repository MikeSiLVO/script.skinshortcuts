"""Shortcut visibility: the attribute applies in the picker, the child element on the item."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.loaders.menu import load_groupings
from skinshortcuts.models.menu import Shortcut


def _write(tmp: Path, body: str) -> Path:
    """Write a menus.xml around given groupings XML and return its path."""
    path = tmp / "menus.xml"
    path.write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<menus>\n  <groupings>\n{body}\n  </groupings>\n</menus>\n'
    )
    return path


def _shortcuts(items) -> list[Shortcut]:
    """Top-level shortcuts among loaded groupings."""
    return [i for i in items if isinstance(i, Shortcut)]


def test_visible_attribute_is_picker_time_only(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <shortcut name="alarm" label="Cancel Alarm" visible="System.HasAlarm(x)">
          <action>CancelAlarm(x)</action>
        </shortcut>
        """,
    )

    shortcut = _shortcuts(load_groupings(path))[0]

    assert shortcut.visible == "System.HasAlarm(x)"
    assert shortcut.item_visible == ""


def test_visible_child_bakes_into_item(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <shortcut name="alarm" label="Cancel Alarm">
          <action>CancelAlarm(x)</action>
          <visible>System.HasAlarm(x)</visible>
        </shortcut>
        """,
    )

    shortcut = _shortcuts(load_groupings(path))[0]

    assert shortcut.visible == ""
    assert shortcut.item_visible == "System.HasAlarm(x)"


def test_attribute_and_child_independent(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <shortcut name="alarm" label="Cancel Alarm" visible="Skin.HasSetting(showAlarms)">
          <action>CancelAlarm(x)</action>
          <visible>System.HasAlarm(x)</visible>
        </shortcut>
        """,
    )

    shortcut = _shortcuts(load_groupings(path))[0]

    assert shortcut.visible == "Skin.HasSetting(showAlarms)"
    assert shortcut.item_visible == "System.HasAlarm(x)"


def test_multiple_visible_children_anded(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <shortcut name="thing" label="Thing">
          <action>Noop</action>
          <visible>Library.HasContent(movies)</visible>
          <visible>Skin.HasSetting(showThing)</visible>
        </shortcut>
        """,
    )

    shortcut = _shortcuts(load_groupings(path))[0]

    assert shortcut.item_visible == "Library.HasContent(movies) + Skin.HasSetting(showThing)"


def test_visible_child_works_inside_groups(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <group name="alarms" label="Alarms">
          <shortcut name="cancel" label="Cancel">
            <action>CancelAlarm(x)</action>
            <visible>System.HasAlarm(x)</visible>
          </shortcut>
        </group>
        """,
    )

    items = load_groupings(path)
    group = items[0]
    nested = group.items[0]

    assert isinstance(nested, Shortcut)
    assert nested.item_visible == "System.HasAlarm(x)"


def test_browse_shortcut_supports_visible_child(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <shortcut name="browse" label="Browse" browse="videos">
          <path>special://profile/playlists/video/</path>
          <visible>Library.HasContent(movies)</visible>
        </shortcut>
        """,
    )

    shortcut = _shortcuts(load_groupings(path))[0]

    assert shortcut.browse == "videos"
    assert shortcut.item_visible == "Library.HasContent(movies)"
