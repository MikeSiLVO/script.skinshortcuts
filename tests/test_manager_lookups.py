"""MenuManager item lookups, top-level and per-item submenu keys, on a real skin fixture."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from skinshortcuts.manager import MenuManager

SKIN = Path(__file__).parent / "fixtures" / "skins" / "skin.aeon.nox.silvo"


@pytest.fixture
def manager(tmp_path) -> MenuManager:
    userdata = tmp_path / "userdata.json"
    shutil.copy(SKIN / "userdata.json", userdata)
    return MenuManager(SKIN / "shortcuts", str(userdata))


def test_get_working_item(manager):
    assert manager._get_working_item("mainmenu", "movies").name == "movies"
    assert manager._get_working_item("mainmenu/movies", "movies-recent").name == "movies-recent"
    assert manager._get_working_item("mainmenu", "nope") is None
    assert manager._get_working_item("nomenu", "movies") is None


def test_set_label_then_modified_and_reset(manager):
    assert manager.reset_item("mainmenu", "movies")
    assert not manager.is_item_modified("mainmenu", "movies")
    manager.set_label("mainmenu", "movies", "Films")
    assert manager._get_working_item("mainmenu", "movies").label == "Films"
    assert manager.is_item_modified("mainmenu", "movies")
    assert manager.reset_item("mainmenu", "movies")
    assert not manager.is_item_modified("mainmenu", "movies")


def test_per_item_submenu_modified_and_reset(manager):
    key = "mainmenu/tvshows"
    assert not manager.is_item_modified(key, "tvshows-genres")
    manager.set_label(key, "tvshows-genres", "Kinds")
    assert manager.is_item_modified(key, "tvshows-genres")
    assert manager.reset_item(key, "tvshows-genres")
    assert manager._get_working_item(key, "tvshows-genres").label != "Kinds"
    assert not manager.is_item_modified(key, "tvshows-genres")


def test_user_added_item_not_resettable(manager):
    assert not manager.is_item_modified("mainmenu/movies", "sub-0ce8742d")
    assert not manager.reset_item("mainmenu/movies", "sub-0ce8742d")
    assert not manager.reset_item("mainmenu", "nope")
    assert not manager.reset_item("nomenu", "movies")


def test_template_for_submenu_key(manager):
    assert manager._template_for_submenu_key("mainmenu/movies").name == "movies"
    assert manager._template_for_submenu_key("mainmenu/music") is None
    assert manager._template_for_submenu_key("mainmenu/nope") is None
    assert manager._template_for_submenu_key("nomenu/movies") is None


def test_reset_menu_per_item_key_reseeds(manager):
    key = "mainmenu/movies"
    manager.set_label(key, "movies-recent", "Changed")
    assert manager.reset_menu(key)
    seeded = manager.working[key]
    assert seeded.name == key
    assert "sub-0ce8742d" not in [i.name for i in seeded.items]
    assert not manager.is_item_modified(key, "movies-recent")


def test_reset_menu_unknown_per_item_key(manager):
    assert not manager.reset_menu("mainmenu/nope")


def test_save_is_stable(manager, tmp_path):
    manager._changed = True
    assert manager.save()
    first = (tmp_path / "userdata.json").read_text()
    again = MenuManager(SKIN / "shortcuts", str(tmp_path / "userdata.json"))
    again._changed = True
    assert again.save()
    assert (tmp_path / "userdata.json").read_text() == first
