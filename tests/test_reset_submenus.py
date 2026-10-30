"""Submenu reset covers <submenu> defaults and their per-item copies, never user widget menus."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from skinshortcuts.config import SkinConfig
from skinshortcuts.manager import MenuManager

FIXTURES = Path(__file__).parent / "fixtures" / "skins"
SILVO = FIXTURES / "skin.aeon.nox.silvo"
MARTIAN = FIXTURES / "skin.arctic.zephyr.martian"
ROUNDED = FIXTURES / "skin.arctic.zephyr.rounded"


def _reset_and_save(skin: Path, userdata: Path) -> dict:
    """Reset submenus and save as entry.py does, returning the saved userdata menus."""
    manager = MenuManager(skin, str(userdata))
    manager.reset_all_submenus()
    manager.save()
    return json.loads(userdata.read_text(encoding="utf-8")).get("menus", {})


def test_per_item_submenu_copy_is_reset(tmp_path: Path):
    userdata = tmp_path / "userdata.json"
    manager = MenuManager(SILVO / "shortcuts", str(userdata))
    manager.set_label("mainmenu/movies", "movies-recent", "Changed")
    assert manager.save()
    assert "mainmenu/movies" not in _reset_and_save(SILVO / "shortcuts", userdata)


def test_custom_widget_menu_survives(tmp_path: Path):
    skin = SILVO / "shortcuts"
    userdata = tmp_path / "userdata.json"
    manager = MenuManager(skin, str(userdata))
    custom = manager.create_custom_widget_menu("mainmenu", "movies")
    manager.set_custom_property("mainmenu", "movies", "widget", "customwidget")
    manager.add_item(custom, label="Mine")
    assert manager.save()

    menus = _reset_and_save(skin, userdata)
    assert custom in menus

    out = tmp_path / "includes.xml"
    SkinConfig.load(skin, userdata_path=str(userdata)).build_includes(out)
    assert 'name="skinshortcuts-movies-customwidget"' in out.read_text(encoding="utf-8")


def test_martian_user_widget_menus_survive(tmp_path: Path):
    userdata = tmp_path / "userdata.json"
    shutil.copy(MARTIAN / "userdata.json", userdata)
    menus = _reset_and_save(MARTIAN / "shortcuts", userdata)
    assert {"movies.widgets", "settings.widgets"} <= set(menus)


def test_rounded_user_item_widget_menu_survives(tmp_path: Path):
    skin = ROUNDED / "shortcuts"
    userdata = tmp_path / "userdata.json"
    manager = MenuManager(skin, str(userdata))
    added = manager.add_item("mainmenu", label="Mine")
    widgets = f"{added.name}.1"
    manager.add_item(widgets, label="Row")
    assert manager.save()
    assert widgets in json.loads(userdata.read_text(encoding="utf-8"))["menus"]
    assert widgets in _reset_and_save(skin, userdata)
