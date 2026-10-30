"""Resetting a menu with its submenus clears the user's edits all the way down."""

from __future__ import annotations

import json
from pathlib import Path

from skinshortcuts.manager import MenuManager

SILVO = Path(__file__).parent / "fixtures" / "skins" / "skin.aeon.nox.silvo" / "shortcuts"


def edited(userdata: Path) -> MenuManager:
    """A manager reloaded from saved edits to the main menu and the movies submenu."""
    manager = MenuManager(SILVO, str(userdata))
    manager.set_label("mainmenu", "movies", "Films")
    manager.set_label("mainmenu/movies", "movies-recent", "Changed")
    assert manager.save()
    return MenuManager(SILVO, str(userdata))


def saved(manager: MenuManager, userdata: Path) -> dict:
    """Save the manager and return the menus the userdata file then holds."""
    manager.save()
    return json.loads(userdata.read_text(encoding="utf-8")).get("menus", {})


def labels(menu: dict) -> dict[str, str]:
    """Item labels a menu's saved diff sets, by item name."""
    return {item["name"]: item["label"] for item in menu.get("items", []) if "label" in item}


def test_tree_reset_clears_the_submenus(tmp_path: Path) -> None:
    """The main menu and each item's submenu go back to the skin defaults."""
    userdata = tmp_path / "userdata.json"
    manager = edited(userdata)
    assert manager.reset_menu_tree("mainmenu")

    menus = saved(manager, userdata)
    assert "movies" not in labels(menus.get("mainmenu", {}))
    assert "mainmenu/movies" not in menus


def test_plain_reset_keeps_the_submenus(tmp_path: Path) -> None:
    """Resetting only the main menu leaves the submenu edits."""
    userdata = tmp_path / "userdata.json"
    manager = edited(userdata)
    assert manager.reset_menu("mainmenu")

    menus = saved(manager, userdata)
    assert "movies" not in labels(menus.get("mainmenu", {}))
    assert labels(menus["mainmenu/movies"])["movies-recent"] == "Changed"


def test_tree_reset_drops_an_added_item_and_its_submenu(tmp_path: Path) -> None:
    """An item the user added goes, and so does the submenu they filled for it."""
    userdata = tmp_path / "userdata.json"
    manager = MenuManager(SILVO, str(userdata))
    added = manager.add_item("mainmenu", label="Mine")
    manager.set_submenu("mainmenu", added.name, "movies")
    manager.ensure_item_submenu("mainmenu", added)
    key = manager.submenu_key("mainmenu", added.name)
    manager.set_label(key, "movies-recent", "Mine too")
    assert key in saved(manager, userdata)

    manager = MenuManager(SILVO, str(userdata))
    assert manager.reset_menu_tree("mainmenu")
    menus = saved(manager, userdata)
    assert key not in menus
    assert all(item["name"] != added.name for item in menus.get("mainmenu", {}).get("items", []))
