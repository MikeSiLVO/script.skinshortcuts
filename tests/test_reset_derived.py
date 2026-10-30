"""A reset or restored item shows its widget and background sub-properties straight away."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from skinshortcuts.manager import MenuManager

SILVO = Path(__file__).parent / "fixtures" / "skins" / "skin.aeon.nox.silvo"


@pytest.fixture
def manager(tmp_path: Path) -> MenuManager:
    shortcuts = tmp_path / "shortcuts"
    shutil.copytree(SILVO / "shortcuts", shortcuts)
    menus = shortcuts / "menus.xml"
    text = menus.read_text(encoding="utf-8")
    anchor = "<icon>special://skin/extras/icons/DefaultMovies.png</icon>"
    assert text.count(anchor) >= 1
    text = text.replace(
        anchor,
        anchor + '<property name="widget">recentlyadded-movies</property>'
        '<property name="background">movie-fanart</property>',
        1,
    )
    menus.write_text(text, encoding="utf-8")
    userdata = tmp_path / "userdata.json"
    userdata.write_text(json.dumps({"menus": {}}), encoding="utf-8")
    return MenuManager(shortcuts, str(userdata))


def _assert_derived(manager: MenuManager) -> None:
    """Assert movies carries its derived widget and background properties."""
    item = manager._get_working_item("mainmenu", "movies")
    assert item is not None
    assert item.properties["widgetPath"] == "videodb://recentlyaddedmovies/"
    assert "backgroundPath" in item.properties
    assert "backgroundLabel" in item.properties


def test_reset_item_fills_derived(manager):
    _assert_derived(manager)
    manager.set_custom_property("mainmenu", "movies", "background", None)
    manager.set_custom_property("mainmenu", "movies", "backgroundPath", None)
    assert manager.reset_item("mainmenu", "movies")
    _assert_derived(manager)


def test_derived_properties_do_not_count_as_modified(manager):
    assert not manager.is_item_modified("mainmenu", "movies")
    manager.set_custom_property("mainmenu", "movies", "background", None)
    assert manager.is_item_modified("mainmenu", "movies")
    assert manager.reset_item("mainmenu", "movies")
    assert not manager.is_item_modified("mainmenu", "movies")


def test_restore_item_fills_derived(manager):
    assert manager.remove_item("mainmenu", "movies")
    removed = [i for i in manager.get_removed_items("mainmenu") if i.name == "movies"]
    assert manager.restore_item("mainmenu", removed[0])
    _assert_derived(manager)
