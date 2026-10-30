"""The Home mirror of skinshortcuts-dialog and -suffix tracks whichever dialog is on top."""

from __future__ import annotations

from pathlib import Path

import pytest
import xbmcgui
from harness import harness_fixture, home, open_root, write_skin  # noqa: F401

MENUS = """<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>Noop</action></item>
  </menu>
  <menu name="globalwidgets" type="widgets">
    <item name="gw1"><label>Recent</label><action>Noop</action></item>
  </menu>
  <menu name="extras">
    <item name="e1"><label>Extra</label><action>Noop</action></item>
  </menu>
</menus>"""

WIDGET2 = {"skinshortcuts-dialog": "widget2", "skinshortcuts-suffix": ".2"}


def _nest(harness, tmp_path: Path, inner_mode: str) -> dict[str, dict[str, str]]:
    """Nest dialogs: a widget2 subdialog, and from inside it a second child on another menu."""
    root = open_root(write_skin(tmp_path, MENUS), tmp_path)
    seen: dict[str, dict[str, str]] = {}

    def outer(child) -> None:
        seen["outer"] = dict(home())
        child._run_child_dialog("extras", inner_mode)
        seen["after inner"] = dict(home())

    harness.child_scripts.extend([outer, lambda _child: seen.update(inner=dict(home()))])
    root._run_child_dialog("mainmenu", "widget2", property_suffix=".2", selected_index=0)
    seen["after outer"] = dict(home())
    return seen


def test_single_subdialog_sets_then_clears_home(harness, tmp_path: Path) -> None:
    seen = _nest(harness, tmp_path, "customwidget")
    assert seen["outer"] == WIDGET2
    assert seen["after outer"] == {}


def test_inner_close_restores_the_outer_mode(harness, tmp_path: Path) -> None:
    assert _nest(harness, tmp_path, "customwidget")["after inner"] == WIDGET2


def test_inner_without_suffix_does_not_show_the_outer_suffix(harness, tmp_path: Path) -> None:
    assert _nest(harness, tmp_path, "customwidget")["inner"] == {
        "skinshortcuts-dialog": "customwidget"
    }


def test_inner_without_mode_does_not_show_the_outer_mode(harness, tmp_path: Path) -> None:
    assert _nest(harness, tmp_path, "")["inner"] == {}


def test_child_that_raises_clears_additional_dialog(harness, tmp_path: Path) -> None:
    root = open_root(write_skin(tmp_path, MENUS), tmp_path)

    def fail(_child) -> None:
        raise RuntimeError("child failed")

    harness.child_scripts.append(fail)
    with pytest.raises(RuntimeError):
        root._run_child_dialog("extras", "customwidget")
    assert "additionalDialog" not in root.window_props


ONCLOSE = MENUS.replace("<menus>", """<menus>
  <dialogs>
    <subdialog buttonID="800" mode="widget1">
      <onclose action="menu" menu="extras" />
    </subdialog>
  </dialogs>""")


def test_onclose_menu_opens_with_this_dialog_still_covered(harness, tmp_path: Path) -> None:
    root = open_root(write_skin(tmp_path, ONCLOSE), tmp_path)
    root.controls[211].selectItem(0)
    between: dict = {}
    handle = root._handle_onclose

    def record(subdialog, item) -> None:
        between.update(home=dict(home()), cover=root.window_props.get("additionalDialog"))
        handle(subdialog, item)

    root._handle_onclose = record
    root._spawn_subdialog(root._subdialogs[800])
    assert between == {"home": {"skinshortcuts-dialog": "widget1"}, "cover": "true"}
    assert home() == {}
    assert "additionalDialog" not in root.window_props


def test_onclose_menu_waits_for_the_closing_subdialog(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    ids = [10]
    monkeypatch.setattr(xbmcgui, "getCurrentWindowDialogId", lambda: ids.pop(0))
    root = open_root(write_skin(tmp_path, ONCLOSE), tmp_path)
    root.controls[211].selectItem(0)
    # subdialog opens as 11, is still on top for two polls, then the menu opens as 12
    ids.extend([11, 11, 11, 10, 12])
    left: list[list[int]] = []
    harness.child_scripts.extend([lambda _child: None, lambda _child: left.append(list(ids))])
    root._spawn_subdialog(root._subdialogs[800])
    assert left == [[]]


def test_subdialog_close_restores_a_moded_root(harness, tmp_path: Path) -> None:
    root = open_root(write_skin(tmp_path, MENUS), tmp_path, menu_id="globalwidgets")
    assert home() == {"skinshortcuts-dialog": "widgets"}
    root._run_child_dialog("globalwidgets", "widget2", property_suffix=".2", selected_index=0)
    assert home() == {"skinshortcuts-dialog": "widgets"}
