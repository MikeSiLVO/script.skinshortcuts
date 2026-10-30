"""Back on the playlist Display/Play prompt cancels the pick, with or without a party mode row."""

from __future__ import annotations

from pathlib import Path

import xbmcgui
from harness import harness_fixture, open_root, write_skin  # noqa: F401

from skinshortcuts.models.menu import Action, Shortcut

MENUS = """<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>ActivateWindow(Videos)</action></item>
  </menu>
  <groupings>
    <shortcut name="movies" label="Movies"><action>ActivateWindow(Videos)</action></shortcut>
  </groupings>
</menus>"""


def _back_on_prompt(harness, tmp_path: Path, monkeypatch, party: str):
    """Pick a playlist shortcut and press Back, which Kodi reports as False or -1."""
    monkeypatch.setattr(xbmcgui.Dialog, "yesno", lambda self, *a, **k: False, raising=False)
    monkeypatch.setattr(xbmcgui.Dialog, "yesnocustom", lambda self, *a, **k: -1, raising=False)
    dialog = open_root(write_skin(tmp_path, MENUS), tmp_path)
    playlist = Shortcut(
        name="playlist-0",
        label="Action Movies",
        actions=[Action(action="ActivateWindow(Videos,special://action.xsp,return)")],
        action_play="PlayMedia(special://action.xsp)",
        action_party=party,
    )
    dialog._pick_shortcut = lambda _groups, _props: playlist
    dialog._choose_shortcut()
    return dialog.items[0]


def test_back_with_party_row_cancels(harness, tmp_path: Path, monkeypatch) -> None:
    item = _back_on_prompt(harness, tmp_path, monkeypatch, "PlayerControl(PartyMode(x))")
    assert (item.label, item.action) == ("Movies", "ActivateWindow(Videos)")


def test_back_without_party_row_cancels(harness, tmp_path: Path, monkeypatch) -> None:
    item = _back_on_prompt(harness, tmp_path, monkeypatch, "")
    assert (item.label, item.action) == ("Movies", "ActivateWindow(Videos)")
