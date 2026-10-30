"""The hasSubmenu row property and a child's window properties follow this session's edits."""

from __future__ import annotations

from pathlib import Path

import pytest
from harness import harness_fixture, open_root, write_skin  # noqa: F401

from skinshortcuts.models.menu import Action, Shortcut

MENUS = """<menus>
  <menu name="mainmenu">
    <item name="music" submenu="musicsub"><label>Music</label><action>Noop</action></item>
    <item name="pictures"><label>Pictures</label><action>Noop</action></item>
    <item name="movies" submenu="moviewidgets"><label>Movies</label><action>Noop</action></item>
  </menu>
  <submenu name="musicsub">
    <item name="m1"><label>Artists</label><action>Noop</action></item>
  </submenu>
  <submenu name="moviewidgets" type="widgets">
    <allow widgets="true" backgrounds="false" submenus="false" />
    <item name="w1"><label>Recent</label><action>Noop</action></item>
  </submenu>
  <groupings>
    <shortcut name="pics" label="Pics"><action>ActivateWindow(Pictures)</action></shortcut>
  </groupings>
</menus>"""


def _open(tmp_path: Path):
    """Open the root dialog on the test menus."""
    return open_root(write_skin(tmp_path, MENUS), tmp_path)


def test_template_submenu_shows_on_open(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path)
    rows = dialog.controls[211].rows
    assert [row.getProperty("hasSubmenu") for row in rows] == ["true", "", "true"]


def test_shortcut_without_submenu_clears_the_row(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path)
    pics = Shortcut(name="pics", label="Pics", actions=[Action(action="ActivateWindow(Pictures)")])
    dialog._pick_shortcut = lambda _groups, _props: pics
    dialog._choose_shortcut()
    assert dialog.items[0].submenu is None
    assert dialog.controls[211].rows[0].getProperty("hasSubmenu") == ""


def _add_named_entry(child) -> None:
    """Add an entry in the child dialog and label it."""
    child._add_item()
    entry = child.items[child.controls[211].pos]
    child.manager.set_label(child.menu_id, entry.name, "Pics")


def test_first_entry_in_a_new_submenu_marks_the_row(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path)
    harness.child_scripts.append(_add_named_entry)
    dialog.controls[211].selectItem(1)
    dialog._edit_submenu()
    assert dialog.manager.working["mainmenu/pictures"].items
    assert dialog.controls[211].rows[1].getProperty("hasSubmenu") == "true"


def _child_window_props(harness, dialog, row: int) -> dict[str, str]:
    """Menu type and disable flags a child dialog sets when editing a row's submenu."""
    seen: dict[str, str] = {}
    harness.child_scripts.append(lambda child: seen.update(child.window_props))
    dialog.controls[211].selectItem(row)
    dialog._edit_submenu()
    wanted = ("skinshortcuts-menutype", "disableBackgrounds", "disableSubmenus")
    return {key: seen.get(key, "") for key in wanted}


WIDGET_PROPS = {
    "skinshortcuts-menutype": "widgets",
    "disableBackgrounds": "true",
    "disableSubmenus": "true",
}


def test_load_time_submenu_child_gets_window_properties(harness, tmp_path: Path) -> None:
    assert _child_window_props(harness, _open(tmp_path), 2) == WIDGET_PROPS


@pytest.mark.parametrize("row", [0, 1], ids=["replaced-template", "no-template-at-load"])
def test_rebound_submenu_child_gets_window_properties(
    harness, tmp_path: Path, row: int
) -> None:
    dialog = _open(tmp_path)
    widgets = Shortcut(name="moviewidgets", label="Movies", actions=[Action(action="Noop")])
    dialog._pick_shortcut = lambda _groups, _props: widgets
    dialog.controls[211].selectItem(row)
    dialog._choose_shortcut()
    assert dialog.items[row].submenu == "moviewidgets"
    assert _child_window_props(harness, dialog, row) == WIDGET_PROPS


def test_new_plain_submenu_child_gets_menutype(harness, tmp_path: Path) -> None:
    props = _child_window_props(harness, _open(tmp_path), 1)
    assert props["skinshortcuts-menutype"] == "submenu"


def test_emptied_submenu_clears_the_row(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path)
    harness.child_scripts.append(lambda child: child._delete_item())
    dialog._edit_submenu()
    left = dialog.manager.working["mainmenu/music"].items
    assert [item.is_placeholder for item in left] == [True]
    dialog._refresh_selected_item()
    assert dialog.controls[211].rows[0].getProperty("hasSubmenu") == ""
