"""Allow attributes default to true; a false one sets its window property and refuses the action."""

from __future__ import annotations

from pathlib import Path

import pytest
from harness import harness_fixture, open_root, write_skin  # noqa: F401

from skinshortcuts.loaders.menu import load_menus
from skinshortcuts.models.menu import MenuAllow

MENUS = """<menus>
  <menu name="mainmenu">
    <allow widgets="{0}" backgrounds="{0}" submenus="{0}" />
    <item name="movies" submenu="moviesub"><label>Movies</label><action>Noop</action></item>
    <item name="music" submenu="musicwidgets"><label>Music</label><action>Noop</action></item>
  </menu>
  <submenu name="moviesub">
    <item name="m1"><label>A</label><action>Noop</action></item>
  </submenu>
  <submenu name="musicwidgets" type="widgets">
    <item name="w1"><label>W</label><action>Noop</action></item>
  </submenu>
</menus>"""

WIDGETS = """<widgets>
  <widget name="recent" label="Recent" type="movies">
    <path>videodb://recentlyaddedmovies/</path>
  </widget>
</widgets>"""


def _allow(tmp_path: Path, element: str) -> MenuAllow:
    """Allow flags parsed from a one-menu menus.xml."""
    path = tmp_path / "menus.xml"
    path.write_text(f'<menus><menu name="m">{element}</menu></menus>', encoding="utf-8")
    return load_menus(path).menus[0].allow


def test_full_element_parses_each_attribute(tmp_path: Path) -> None:
    allow = _allow(tmp_path, '<allow widgets="true" backgrounds="false" submenus="true" />')
    assert allow == MenuAllow(widgets=True, backgrounds=False, submenus=True)


def test_partial_element_leaves_unlisted_attributes_on(tmp_path: Path) -> None:
    allow = _allow(tmp_path, '<allow widgets="false" />')
    assert allow == MenuAllow(widgets=False, backgrounds=True, submenus=True)


def test_bare_element_allows_everything(tmp_path: Path) -> None:
    assert _allow(tmp_path, "<allow />") == MenuAllow()


ALLOWED = [True, False]


def _open(tmp_path: Path, allowed: bool, **files: str):
    """Open the root dialog on a skin with every allow flag set the same."""
    return open_root(write_skin(tmp_path, MENUS.format(str(allowed).lower()), **files), tmp_path)


def test_flags_set_window_properties(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path, False)
    for name in ("disableWidgets", "disableBackgrounds", "disableSubmenus"):
        assert dialog.window_props[name] == "true"


def _record(calls: list[str], name: str, result=None):
    """Record calls under a name, returning a stand-in that logs each one."""

    def record(*_args, **_kwargs):
        calls.append(name)
        return result

    return record


@pytest.mark.parametrize("allowed", ALLOWED)
def test_widget_button_picks_only_when_allowed(harness, tmp_path: Path, allowed: bool) -> None:
    """The widget button opens the widget picker only when the menu allows widgets."""
    dialog = _open(tmp_path, allowed, widgets=WIDGETS)
    calls: list[str] = []
    dialog._pick_widget_from_groups = _record(calls, "groups")
    dialog._handle_widget_property(dialog.items[0], "widget")
    assert bool(calls) is allowed


@pytest.mark.parametrize("allowed", ALLOWED)
def test_background_button_picks_only_when_allowed(harness, tmp_path: Path, allowed: bool) -> None:
    dialog = _open(tmp_path, allowed)
    calls: list[str] = []
    dialog._pick_background = _record(calls, "background")
    dialog._handle_background_property(dialog.items[0], "background")
    assert bool(calls) is allowed


@pytest.mark.parametrize("allowed", ALLOWED)
@pytest.mark.parametrize("row", [0, 1], ids=["submenu", "widget-submenu"])
def test_submenu_editing_opens_only_when_allowed(
    harness, tmp_path: Path, row: int, allowed: bool
) -> None:
    dialog = _open(tmp_path, allowed)
    calls: list[str] = []
    dialog._run_child_dialog = _record(calls, "child")
    dialog.controls[211].selectItem(row)
    dialog._edit_submenu()
    assert bool(calls) is allowed
