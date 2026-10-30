"""A subdialog keeps acting on the item it was opened for through a delete or move inside it."""

from __future__ import annotations

from pathlib import Path

from harness import harness_fixture, open_root, write_skin  # noqa: F401

MENUS = """<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>Noop</action></item>
    <item name="tvshows"><label>TV</label><action>Noop</action></item>
    <item name="music"><label>Music</label><action>Noop</action></item>
    <item name="livetv"><label>Live</label><action>Noop</action></item>
  </menu>
  <dialogs>
    <subdialog buttonID="800" mode="widget">
      <onclose action="menu" menu="{item}.customwidget" />
    </subdialog>
  </dialogs>
</menus>"""


def _run(harness, tmp_path: Path, script):
    """Run a given step inside the widget subdialog on tvshows; return root and what it saw."""
    root = open_root(write_skin(tmp_path, MENUS), tmp_path)
    root.controls[211].selectItem(1)
    seen: dict[str, object] = {}
    harness.child_scripts.extend([lambda child: script(child, seen), lambda _onclose: None])
    root._spawn_subdialog(root._subdialogs[800])
    return root, seen


def _move_down(child, seen) -> None:
    """Move the edited row down and record the item still being edited."""
    child._move_item(1)
    seen["editing"] = child._get_selected_item().name


def _delete(child, seen) -> None:
    """Delete the edited row and record what the child edits next, None once closed."""
    child._delete_item()
    seen["after delete"] = None if child.closed else child._get_selected_item().name


def _custom_widget_owners(root) -> list[str]:
    """Names of root items holding a customWidget."""
    return [item.name for item in root.items if "customWidget" in item.properties]


def test_untouched_subdialog_runs_onclose_for_its_item(harness, tmp_path: Path) -> None:
    root, _seen = _run(harness, tmp_path, lambda _child, _seen: None)
    assert _custom_widget_owners(root) == ["tvshows"]


def test_move_keeps_editing_the_same_item(harness, tmp_path: Path) -> None:
    _root, seen = _run(harness, tmp_path, _move_down)
    assert seen["editing"] == "tvshows"


def test_move_leaves_parent_rows_current(harness, tmp_path: Path) -> None:
    root, _seen = _run(harness, tmp_path, _move_down)
    rows = root.controls[211]
    assert rows.names() == [item.name for item in root.items]
    assert rows.getSelectedItem().getProperty("name") == "tvshows"


def test_move_runs_onclose_for_the_moved_item(harness, tmp_path: Path) -> None:
    root, _seen = _run(harness, tmp_path, _move_down)
    assert _custom_widget_owners(root) == ["tvshows"]


def test_delete_stops_editing_a_neighbour(harness, tmp_path: Path) -> None:
    _root, seen = _run(harness, tmp_path, _delete)
    assert seen["after delete"] is None


def test_delete_leaves_parent_rows_current(harness, tmp_path: Path) -> None:
    root, _seen = _run(harness, tmp_path, _delete)
    assert root.controls[211].names() == [item.name for item in root.items]


def test_delete_skips_onclose(harness, tmp_path: Path) -> None:
    root, _seen = _run(harness, tmp_path, _delete)
    assert _custom_widget_owners(root) == []
