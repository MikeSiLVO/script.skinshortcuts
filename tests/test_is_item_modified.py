"""An untouched item reads as unmodified, whatever shorthand its default uses."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from skinshortcuts.conditions import lookup, with_defaults
from skinshortcuts.config import SkinConfig
from skinshortcuts.manager import MenuManager

FIXTURES = Path(__file__).parent / "fixtures" / "skins"
SILVO = FIXTURES / "skin.aeon.nox.silvo"


def _skin(tmp_path: Path, old: str, new: str) -> Path:
    """A silvo copy with one edit to menus.xml."""
    shortcuts = tmp_path / "shortcuts"
    shutil.copytree(SILVO / "shortcuts", shortcuts)
    menus = shortcuts / "menus.xml"
    text = menus.read_text(encoding="utf-8")
    assert text.count(old) == 1
    menus.write_text(text.replace(old, new), encoding="utf-8")
    return shortcuts


@pytest.fixture
def shorthand(tmp_path: Path) -> MenuManager:
    old = '<item name="movies" submenu="movies"'
    new = f'{old} widget="random-movies-pl" background="custom-folder">'
    skin = _skin(tmp_path, f"{old}>", new)
    return MenuManager(skin, str(tmp_path / "userdata.json"))


@pytest.mark.parametrize("skin", sorted(p.name for p in FIXTURES.iterdir() if p.is_dir()))
def test_fixture_skins_have_no_false_flags(skin: str, tmp_path: Path):
    manager = MenuManager(FIXTURES / skin / "shortcuts", str(tmp_path / "userdata.json"))
    flagged = [
        (menu_id, item.name)
        for menu_id, menu in manager.working.items()
        for item in menu.items
        if manager.is_item_modified(menu_id, item.name)
    ]
    assert flagged == []


def test_untouched_item_with_widget_shorthand_is_not_modified(shorthand: MenuManager):
    assert manager_diff(shorthand) is None
    assert not shorthand.is_item_modified("mainmenu", "movies")


def test_item_with_widget_shorthand_is_modified_after_a_change(shorthand: MenuManager):
    shorthand.set_label("mainmenu", "movies", "Films")
    assert shorthand.is_item_modified("mainmenu", "movies")


DEFAULTS = ('<menu name="mainmenu" container="9000">',
            '<menu name="mainmenu" container="9000"><defaults widget="random-movies-pl"/>')


def test_defaults_widget_shorthand_marks_no_item(tmp_path: Path):
    manager = MenuManager(_skin(tmp_path, *DEFAULTS), str(tmp_path / "userdata.json"))
    assert not any(
        manager.is_item_modified("mainmenu", item.name)
        for item in manager.get_menu_items("mainmenu")
    )


def test_defaults_widget_shorthand_derives_its_path(tmp_path: Path):
    config = SkinConfig.load(_skin(tmp_path, *DEFAULTS), load_user=False)
    menu = config.get_menu("mainmenu")
    config.resolve_item_properties(menu)
    item = menu.get_item("pictures")
    context = with_defaults(menu.defaults.properties, item.properties)
    assert context["widget"] == "random-movies-pl"
    assert "randommovies.xsp" in (lookup("widgetPath", context) or "")


def test_own_widget_pick_takes_nothing_from_the_defaults_widget(tmp_path: Path):
    skin = _skin(tmp_path, *DEFAULTS)
    config = SkinConfig.load(skin, load_user=False)
    menu = config.get_menu("mainmenu")
    item = menu.get_item("pictures")
    item.properties["widget"] = "recentlyadded-movies"
    config.resolve_item_properties(menu)
    assert "randommovies.xsp" not in item.properties.get("widgetPath", "")
    assert item.properties["widgetPath"] == "videodb://recentlyaddedmovies/"


def test_explicit_defaults_value_beats_the_derived_one(tmp_path: Path):
    old, new = DEFAULTS
    explicit = new.replace(
        '<defaults widget="random-movies-pl"/>',
        '<defaults widget="random-movies-pl">'
        '<property name="widgetLabel">Mine</property></defaults>',
    )
    config = SkinConfig.load(_skin(tmp_path, old, explicit), load_user=False)
    menu = config.get_menu("mainmenu")
    config.resolve_item_properties(menu)
    item = menu.get_item("pictures")
    assert lookup("widgetLabel", with_defaults(menu.defaults.properties, item.properties)) == "Mine"


def test_defaults_widget_saves_no_widget_data(tmp_path: Path):
    userdata = tmp_path / "userdata.json"
    manager = MenuManager(_skin(tmp_path, *DEFAULTS), str(userdata))
    manager.set_label("mainmenu", "music", "Tunes")
    assert manager.save()
    assert "widget" not in userdata.read_text(encoding="utf-8")


def manager_diff(manager: MenuManager):
    """What a save would store for the movies item."""
    working = manager._get_working_item("mainmenu", "movies")
    default_menu = manager._default_menu("mainmenu")
    default = default_menu.get_item("movies")
    return manager._diff_item(working, default, default_menu.defaults.properties)
