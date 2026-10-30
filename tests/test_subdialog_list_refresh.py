"""Container 212 follows every 211 rebuild in a subdialog and never empties or reads 211 back."""

from __future__ import annotations

from pathlib import Path

from harness import harness_fixture, open_root, write_skin  # noqa: F401

MENUS = """<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>Noop</action></item>
    <item name="tvshows"><label>TV</label><action>Noop</action></item>
    <item name="music"><label>Music</label><action>Noop</action></item>
  </menu>
</menus>"""


def _widgets_child(tmp_path: Path):
    """A dialog in a subdialog mode with no edited item, as an _edit_submenu child runs."""
    dialog = open_root(write_skin(tmp_path, MENUS), tmp_path)
    dialog.dialog_mode = "widgets"
    dialog._rebuild_list(focus_index=0)
    return dialog


def _edited(dialog) -> str:
    """Name of the row container 212 shows, or empty."""
    rows = dialog.controls[212].rows
    return rows[0].getProperty("name") if rows else ""


def test_delete_moves_212_to_the_row_211_selects(harness, tmp_path: Path) -> None:
    dialog = _widgets_child(tmp_path)
    dialog.controls[211].selectItem(2)
    dialog._delete_item()
    assert dialog.controls[211].pos == 1
    assert _edited(dialog) == "tvshows"


def test_move_keeps_212_on_the_moved_row(harness, tmp_path: Path) -> None:
    dialog = _widgets_child(tmp_path)
    dialog._move_item(1)
    assert dialog.controls[211].names()[1] == "movies"
    assert _edited(dialog) == "movies"


def test_212_keeps_its_row_when_no_item_resolves(harness, tmp_path: Path) -> None:
    dialog = _widgets_child(tmp_path)
    dialog.items = []
    dialog._populate_subdialog_list(5)
    assert _edited(dialog) == "movies"
    assert 0 not in dialog.controls[212].sizes


def test_subdialog_refresh_follows_its_own_item_not_the_211_cursor(
    harness, tmp_path: Path
) -> None:
    dialog = _widgets_child(tmp_path)
    dialog._selected_index = 1
    dialog.controls[211].selectItem(2)
    dialog._refresh_selected_item()
    assert dialog.controls[211].pos == 1
    assert _edited(dialog) == "tvshows"
