"""A save made while visible= hides an item keeps that item's stored edits, position and removal."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import xbmc

from skinshortcuts.config import SkinConfig
from skinshortcuts.manager import MenuManager

SILVO = Path(__file__).parent / "fixtures" / "skins" / "skin.aeon.nox.silvo"
HIDDEN = "playdisc"


@pytest.fixture
def skin(tmp_path: Path) -> Path:
    shortcuts = tmp_path / "shortcuts"
    shutil.copytree(SILVO / "shortcuts", shortcuts)
    return shortcuts


@pytest.fixture
def disc(monkeypatch: pytest.MonkeyPatch) -> dict[str, bool]:
    """Whether every visible= condition passes, standing in for a disc in the drive."""
    state = {"in": False}
    monkeypatch.setattr(xbmc, "getCondVisibility", lambda _condition: state["in"])
    return state


def _unrelated_save(skin: Path, userdata: Path) -> None:
    """Rename an item in the music submenu and save, touching nothing in mainmenu."""
    manager = MenuManager(skin, str(userdata))
    assert HIDDEN not in [i.name for i in manager.get_menu_items("mainmenu")]
    first = manager.get_menu_items("mainmenu/music")[0]
    manager.set_label("mainmenu/music", first.name, "Renamed")
    assert manager.save()


def _mainmenu(skin: Path, userdata: Path) -> list[str]:
    """Mainmenu item names as the next build loads them."""
    menu = SkinConfig.load(skin, userdata_path=str(userdata)).get_menu("mainmenu")
    assert menu is not None
    return [item.name for item in menu.items]


def test_rename_survives_while_the_item_stays_visible(skin, tmp_path, disc):
    userdata = tmp_path / "userdata.json"
    disc["in"] = True
    manager = MenuManager(skin, str(userdata))
    manager.set_label("mainmenu", HIDDEN, "Disc")
    assert manager.save()
    menu = SkinConfig.load(skin, userdata_path=str(userdata)).get_menu("mainmenu")
    assert menu.get_item(HIDDEN).label == "Disc"


def test_unrelated_save_writes_no_mainmenu_diff(skin, tmp_path, disc):
    userdata = tmp_path / "userdata.json"
    _unrelated_save(skin, userdata)
    assert "mainmenu" not in json.loads(userdata.read_text(encoding="utf-8"))["menus"]


def test_unrelated_save_keeps_the_hidden_item_position(skin, tmp_path, disc):
    userdata = tmp_path / "userdata.json"
    default = SkinConfig.load(skin, load_user=False).get_default_menu("mainmenu")
    default_index = [item.name for item in default.items].index(HIDDEN)
    _unrelated_save(skin, userdata)
    disc["in"] = True
    assert _mainmenu(skin, userdata).index(HIDDEN) == default_index


def test_unrelated_save_keeps_the_hidden_item_rename(skin, tmp_path, disc):
    userdata = tmp_path / "userdata.json"
    disc["in"] = True
    manager = MenuManager(skin, str(userdata))
    manager.set_label("mainmenu", HIDDEN, "Disc")
    assert manager.save()
    disc["in"] = False
    _unrelated_save(skin, userdata)
    disc["in"] = True
    menu = SkinConfig.load(skin, userdata_path=str(userdata)).get_menu("mainmenu")
    assert menu.get_item(HIDDEN).label == "Disc"


def test_unrelated_save_keeps_the_hidden_item_removed(skin, tmp_path, disc):
    userdata = tmp_path / "userdata.json"
    disc["in"] = True
    manager = MenuManager(skin, str(userdata))
    assert manager.remove_item("mainmenu", HIDDEN)
    assert manager.save()
    disc["in"] = False
    _unrelated_save(skin, userdata)
    disc["in"] = True
    assert HIDDEN not in _mainmenu(skin, userdata)


def test_a_move_beside_the_hidden_item_keeps_its_order(skin, tmp_path, disc):
    userdata = tmp_path / "userdata.json"
    default = SkinConfig.load(skin, load_user=False).get_default_menu("mainmenu")
    manager = MenuManager(skin, str(userdata))
    shown = [i.name for i in manager.get_menu_items("mainmenu")]
    names = [item.name for item in default.items]
    before = [n for n in names[: names.index(HIDDEN)] if n in shown][-1]
    assert manager.move_item("mainmenu", shown[shown.index(before) - 1], 1)
    assert manager.save()
    moved = [i.name for i in manager.get_menu_items("mainmenu")]
    assert _mainmenu(skin, userdata) == moved
    disc["in"] = True
    built = _mainmenu(skin, userdata)
    assert [n for n in built if n in moved] == moved
    assert built[built.index(before) + 1] == HIDDEN
