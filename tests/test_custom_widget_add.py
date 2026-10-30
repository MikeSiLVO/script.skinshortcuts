"""Add in a custom widget menu makes a blank shortcut item; a widget list still picks a widget."""

from __future__ import annotations

from pathlib import Path

import pytest
from harness import harness_fixture, open_root, write_skin  # noqa: F401

MENUS = """<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>Noop</action></item>
  </menu>
  <submenu name="movies.widgets" type="widgets">
    <item name="recent">
      <label>Recent</label>
      <property name="widgetPath">videodb://recentlyaddedmovies/</property>
    </item>
  </submenu>
</menus>"""


def _add(harness, tmp_path: Path, mode: str, custom: bool) -> tuple[list[str], list]:
    """Run Add in a child dialog on a custom widget menu or widget list; picker calls, new items."""
    root = open_root(write_skin(tmp_path, MENUS), tmp_path)
    assert root.manager is not None
    if custom:
        menu_id = root.manager.create_custom_widget_menu("mainmenu", "movies")
    else:
        menu_id = "movies.widgets"
    calls: list[str] = []
    added: list = []

    def add(child) -> None:
        child._pick_widget_for_add = lambda: calls.append("widget")
        before = list(child.items)
        child._add_item()
        added.extend(item for item in child.items if item not in before)

    harness.child_scripts.append(add)
    root._run_child_dialog(menu_id, mode)
    return calls, added


@pytest.mark.parametrize("mode", ["customwidget", "custom-widget1", "custom-shelf"])
def test_custom_widget_add_makes_a_blank_item(harness, tmp_path: Path, mode: str) -> None:
    calls, added = _add(harness, tmp_path, mode, custom=True)
    assert calls == []
    assert [(item.is_placeholder, item.actions[0].action) for item in added] == [(True, "noop")]


@pytest.mark.parametrize("mode", ["widgets", "custom-widgets", "customwidget"])
def test_widget_list_add_picks_a_widget(harness, tmp_path: Path, mode: str) -> None:
    calls, added = _add(harness, tmp_path, mode, custom=False)
    assert calls == ["widget"]
    assert added == []
