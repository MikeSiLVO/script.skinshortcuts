"""A {item}.X subdialog routes to the per-item key only when it names the item's submenu."""

from __future__ import annotations

import types
from pathlib import Path

from skinshortcuts.config import SkinConfig
from skinshortcuts.dialog.subdialogs import SubdialogsMixin
from skinshortcuts.manager import MenuManager
from skinshortcuts.models.menu import SubDialog


def _setup(tmp_path: Path, menus_xml: str) -> Path:
    """Write a menus.xml into a shortcuts folder and return it."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(menus_xml)
    return skin


def _resolver(manager: MenuManager, parent_menu_id: str):
    """Menu reference resolver bound to a stub dialog on a parent menu."""
    stub = types.SimpleNamespace(manager=manager, menu_id=parent_menu_id, _log=lambda _msg: None)
    return SubdialogsMixin._resolve_menu_reference.__get__(stub)


def test_routes_to_per_item_when_subdialog_matches_item_submenu(tmp_path: Path):
    """Predefined item with ``submenu="movies.1"`` and skin subdialog ``{item}.1``: route."""
    menus_xml = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies" submenu="movies.1">
      <label>Movies</label>
      <action>Noop</action>
    </item>
  </menu>
  <submenu name="movies.1" type="widgets"/>
</menus>
"""
    skin = _setup(tmp_path, menus_xml)
    manager = MenuManager(skin)
    movies = next(i for i in manager.working["mainmenu"].items if i.name == "movies")

    resolve = _resolver(manager, "mainmenu")
    target = resolve("{item}.1", movies, SubDialog(button_id=406))

    assert target == "mainmenu/movies"
    assert "mainmenu/movies" in manager.working


def test_falls_through_when_subdialog_is_a_different_template(tmp_path: Path):
    """Subdialog ``{item}.2`` with item.submenu=``movies.1``: don't route."""
    menus_xml = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies" submenu="movies.1">
      <label>Movies</label>
      <action>Noop</action>
    </item>
  </menu>
  <submenu name="movies.1"/>
  <submenu name="movies.2"/>
</menus>
"""
    skin = _setup(tmp_path, menus_xml)
    manager = MenuManager(skin)
    movies = next(i for i in manager.working["mainmenu"].items if i.name == "movies")

    resolve = _resolver(manager, "mainmenu")
    target = resolve("{item}.2", movies, SubDialog(button_id=406))

    assert target == "movies.2"


def test_falls_through_for_user_added_item_without_submenu_attr(tmp_path: Path):
    """User-added item: resolved ``user-X.1`` doesn't match item.name ``user-X``; no route."""
    menus_xml = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="home">
      <label>Home</label>
      <action>Noop</action>
    </item>
  </menu>
</menus>
"""
    skin = _setup(tmp_path, menus_xml)
    config = SkinConfig.load(skin, load_user=False)

    from skinshortcuts.models.menu import Action, MenuItem
    user_item = MenuItem(name="user-abc12345", label="Custom", actions=[Action(action="Noop")])
    config.menus[0].items.append(user_item)
    manager = MenuManager(skin)
    manager.working["mainmenu"].items.append(user_item)

    resolve = _resolver(manager, "mainmenu")
    target = resolve("{item}.1", user_item, SubDialog(button_id=406))

    assert target == "user-abc12345.1"
    assert "mainmenu/user-abc12345" not in manager.working


def test_falls_through_when_no_submenu_attr(tmp_path: Path):
    """No submenu attribute even when a same-named template exists: don't route."""
    menus_xml = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="settings">
      <label>Settings</label>
      <action>ActivateWindow(Settings)</action>
    </item>
  </menu>
  <submenu name="settings"/>
</menus>
"""
    skin = _setup(tmp_path, menus_xml)
    manager = MenuManager(skin)
    settings = next(i for i in manager.working["mainmenu"].items if i.name == "settings")

    resolve = _resolver(manager, "mainmenu")
    target = resolve("{item}", settings, SubDialog(button_id=500))

    assert target == "settings"
