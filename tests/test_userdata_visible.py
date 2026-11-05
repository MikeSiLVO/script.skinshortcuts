"""User-set visible round-trips through userdata."""

from __future__ import annotations

from skinshortcuts.models.menu import Action, MenuItem
from skinshortcuts.userdata import (
    MenuDiff,
    MenuItemDiff,
    UserData,
    _apply_diff,
    _create_item_from_diff,
)


def test_override_visible_serializes_and_loads():
    override = MenuItemDiff(name="cancel", visible="System.HasAlarm(x)", is_new=True)
    userdata = UserData(menus={"powermenu": MenuDiff(items=[override])})

    data = userdata.to_dict()
    item_data = data["menus"]["powermenu"]["items"][0]
    assert item_data["visible"] == "System.HasAlarm(x)"

    restored = UserData.from_dict(data)
    restored_override = restored.menus["powermenu"].items[0]
    assert restored_override.visible == "System.HasAlarm(x)"


def test_override_visible_applies_to_existing_item():
    default = MenuItem(
        name="cancel",
        label="Cancel",
        actions=[Action(action="CancelAlarm(x)")],
        visible="",
    )
    override = MenuItemDiff(name="cancel", visible="System.HasAlarm(x)")

    merged = _apply_diff(default, override)
    assert merged.visible == "System.HasAlarm(x)"


def test_override_visible_falls_back_to_default():
    default = MenuItem(name="x", label="X", visible="Library.HasContent(movies)")
    override = MenuItemDiff(name="x", label="Renamed")

    merged = _apply_diff(default, override)
    assert merged.visible == "Library.HasContent(movies)"


def test_new_item_from_override_preserves_visible():
    override = MenuItemDiff(
        name="cancel",
        label="Cancel Alarm",
        actions=[Action(action="CancelAlarm(x)")],
        visible="System.HasAlarm(x)",
        is_new=True,
    )

    item = _create_item_from_diff(override)
    assert item.visible == "System.HasAlarm(x)"


def test_legacy_userdata_without_visible_still_loads():
    legacy_data = {
        "menus": {
            "main": {
                "items": [
                    {"name": "movies", "label": "Movies"},
                ]
            }
        }
    }

    restored = UserData.from_dict(legacy_data)
    item = restored.menus["main"].items[0]
    assert item.visible is None
