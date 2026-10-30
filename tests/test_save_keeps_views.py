"""A menu save keeps view selections, which are made outside the management dialog."""

from __future__ import annotations

import json
from pathlib import Path

from skinshortcuts.manager import MenuManager

SKIN = Path(__file__).parent / "fixtures" / "skins" / "skin.aeon.nox.silvo" / "shortcuts"


def test_editing_a_label_keeps_stored_views(tmp_path):
    userdata = tmp_path / "userdata.json"
    userdata.write_text(
        json.dumps({"views": {"library": {"movies": "view-500"}}}), encoding="utf-8"
    )

    manager = MenuManager(SKIN, userdata)
    menu_id = manager.get_menu_ids()[0]
    item = manager.get_menu_items(menu_id)[0]
    manager.set_label(menu_id, item.name, "Renamed")
    manager.save()

    saved = json.loads(userdata.read_text(encoding="utf-8"))
    assert saved["views"] == {"library": {"movies": "view-500"}}
    assert saved["menus"]
