"""A custom widget menu is a widget menu, in the session that creates it and after a reload."""

from __future__ import annotations

import types
from pathlib import Path

from skinshortcuts.dialog.base import DialogBaseMixin
from skinshortcuts.manager import MenuManager

SILVO = Path(__file__).parent / "fixtures" / "skins" / "skin.aeon.nox.silvo" / "shortcuts"


def _create(userdata: Path) -> tuple[MenuManager, str]:
    """Create a custom widget menu on mainmenu/movies holding one item, and save."""
    manager = MenuManager(SILVO, str(userdata))
    custom = manager.create_custom_widget_menu("mainmenu", "movies")
    manager.set_custom_property("mainmenu", "movies", "widget", "customwidget")
    manager.add_item(custom, label="Row")
    assert manager.save()
    return manager, custom


def _menutype(manager: MenuManager, menu_id: str) -> str | None:
    """The skinshortcuts-menutype the dialog sets for this menu; None when it is not set."""
    props: dict[str, str] = {}
    stub = types.SimpleNamespace(
        manager=manager,
        menu_id=menu_id,
        setProperty=props.__setitem__,
        _update_deleted_property=lambda: None,
    )
    DialogBaseMixin._update_window_properties.__get__(stub)()
    return props.get("skinshortcuts-menutype")


def test_new_menu_is_a_widget_menu_in_the_working_copy(tmp_path: Path):
    manager, custom = _create(tmp_path / "userdata.json")
    assert manager.working[custom].menu_type == "widgets"


def test_reloaded_menu_is_a_widget_menu(tmp_path: Path):
    _, custom = _create(tmp_path / "userdata.json")
    reloaded = MenuManager(SILVO, str(tmp_path / "userdata.json"))
    assert reloaded.working[custom].menu_type == "widgets"
    assert _menutype(reloaded, custom) == "widgets"


def test_new_menu_reports_widgets_to_the_skin(tmp_path: Path):
    manager, custom = _create(tmp_path / "userdata.json")
    assert _menutype(manager, custom) == "widgets"
