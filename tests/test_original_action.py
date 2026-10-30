"""originalAction keeps the skin's action through user edits; an added item shows its own."""

from __future__ import annotations

from pathlib import Path

import pytest
from harness import HarnessDialog, harness_fixture, open_root, write_skin  # noqa: F401

from skinshortcuts.models.menu import Action, MenuItem

MENUS = """<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>ActivateWindow(Videos)</action></item>
    <item name="tv"><label>TV</label><action>ActivateWindow(TVChannels)</action></item>
  </menu>
</menus>"""


def original(dialog: HarnessDialog, name: str) -> str:
    """The originalAction property the dialog shows for a main menu item."""
    item = next(i for i in dialog.manager.get_menu_items("mainmenu") if i.name == name)
    return dialog._listitem_values(item).properties["originalaction"]


def test_saved_change_keeps_the_skin_action(harness, tmp_path: Path) -> None:
    """An action changed in an earlier session still shows the skin's."""
    skin = write_skin(tmp_path, MENUS)
    first = open_root(skin, tmp_path)
    first.manager.set_action("mainmenu", "movies", "Noop")
    first.manager.save()
    assert original(open_root(skin, tmp_path), "movies") == "ActivateWindow(Videos)"


@pytest.mark.xfail(strict=True, reason="originalAction follows an unsaved action change")
def test_unsaved_change_keeps_the_skin_action(harness, tmp_path: Path) -> None:
    """An action changed in this session still shows the skin's."""
    dialog = open_root(write_skin(tmp_path, MENUS), tmp_path)
    dialog.manager.set_action("mainmenu", "tv", "Noop")
    assert original(dialog, "tv") == "ActivateWindow(TVChannels)"


def test_added_item_shows_its_own_action(harness, tmp_path: Path) -> None:
    """An item the user added shows its current action."""
    dialog = open_root(write_skin(tmp_path, MENUS), tmp_path)
    added = MenuItem(name="music", label="Music", actions=[Action(action="ActivateWindow(Music)")])
    dialog.manager.add_item("mainmenu", item=added)
    assert original(dialog, "music") == "ActivateWindow(Music)"
