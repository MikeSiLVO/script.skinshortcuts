"""Submenus are one level deep: the dialog offers no submenu for an item that is in one."""

from __future__ import annotations

import json
import types
from pathlib import Path

import pytest
import xbmc

from skinshortcuts.config import SkinConfig
from skinshortcuts.dialog.base import CONTROL_EDIT_SUBMENU, DialogBaseMixin
from skinshortcuts.dialog.items import ItemsMixin
from skinshortcuts.dialog.subdialogs import SubdialogsMixin
from skinshortcuts.manager import MenuManager

FIXTURES = Path(__file__).parent / "fixtures" / "skins"
MARTIAN = FIXTURES / "skin.arctic.zephyr.martian" / "shortcuts"
ROUNDED = FIXTURES / "skin.arctic.zephyr.rounded" / "shortcuts"


def _dialog(manager: MenuManager, menu_id: str, item_name: str) -> types.SimpleNamespace:
    """A dialog stub on one menu with one item selected, recording child dialogs it opens."""
    item = manager._get_working_item(menu_id, item_name)
    assert item is not None
    stub = types.SimpleNamespace(
        manager=manager, menu_id=menu_id, opened=[], _get_selected_item=lambda: item,
        _refresh_selected_item=lambda: None,
        _log=lambda _msg: None,
    )
    stub._run_child_dialog = lambda child_id, _mode="": stub.opened.append(child_id)
    return stub


def _edit_submenu(manager: MenuManager, menu_id: str, item_name: str) -> list[str]:
    """Menus the Edit Submenu button opens for an item."""
    stub = _dialog(manager, menu_id, item_name)
    SubdialogsMixin._edit_submenu.__get__(stub)()
    return stub.opened


def _context_ids(manager: MenuManager, menu_id: str, item_name: str) -> list[int]:
    """Button IDs the default context menu lists for an item."""
    from skinshortcuts.loaders.menu import load_menus

    item = manager._get_working_item(menu_id, item_name)
    stub = types.SimpleNamespace(
        manager=manager,
        menu_id=menu_id,
        context_menu=load_menus(MARTIAN / "menus.xml").context_menu,
        property_schema=None,
        property_suffix="",
        _subdialogs={},
        _log=lambda _msg: None,
    )
    stub._get_item_properties = DialogBaseMixin._get_item_properties.__get__(stub)
    stub._context_button_routes = ItemsMixin._context_button_routes.__get__(stub)
    return [row[0] for row in ItemsMixin._context_menu_rows.__get__(stub)(item)]


@pytest.fixture
def martian(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> MenuManager:
    monkeypatch.setattr("skinshortcuts.dialog.items.LANGUAGE", lambda sid: f"#{sid}")
    monkeypatch.setattr(xbmc, "getLocalizedString", lambda sid: f"core#{sid}", raising=False)
    return MenuManager(MARTIAN, str(tmp_path / "userdata.json"))


def test_top_level_item_opens_its_submenu(martian: MenuManager):
    assert _edit_submenu(martian, "mainmenu", "movies") == ["mainmenu/movies"]
    assert CONTROL_EDIT_SUBMENU in _context_ids(martian, "mainmenu", "movies")


def test_submenu_item_opens_no_submenu(martian: MenuManager):
    assert _edit_submenu(martian, "mainmenu/movies", "recently-added") == []


def test_submenu_item_context_menu_has_no_edit_submenu(martian: MenuManager):
    assert CONTROL_EDIT_SUBMENU not in _context_ids(martian, "mainmenu/movies", "recently-added")


@pytest.mark.parametrize(
    ("skin", "menu_id"), [(MARTIAN, "mainmenu/movies"), (ROUNDED, "movies.1")]
)
def test_third_level_edits_are_not_loaded_back(tmp_path: Path, skin: Path, menu_id: str):
    userdata = tmp_path / "userdata.json"
    manager = MenuManager(skin, str(userdata))
    item = manager.get_menu_items(menu_id)[0]
    nested = manager.ensure_item_submenu(menu_id, item)
    manager.add_item(nested.name, label="Deep")
    assert manager.save()
    assert nested.name in json.loads(userdata.read_text(encoding="utf-8"))["menus"]

    reloaded = MenuManager(skin, str(userdata))
    assert nested.name not in reloaded.working
    assert SkinConfig.load(skin, userdata_path=str(userdata)).get_menu(nested.name) is None

    reloaded.set_label("mainmenu", reloaded.get_menu_items("mainmenu")[0].name, "Touched")
    assert reloaded.save()
    assert nested.name not in json.loads(userdata.read_text(encoding="utf-8"))["menus"]
