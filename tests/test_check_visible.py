"""The check_visible helper gates on Kodi's condition; the userdata merge filters through it."""

from __future__ import annotations

import xbmc

from skinshortcuts import conditions
from skinshortcuts.conditions import check_visible
from skinshortcuts.models.menu import Menu, MenuItem
from skinshortcuts.userdata import MenuDiff, merge_menu


def test_empty_passes_without_asking_kodi(monkeypatch):
    calls = []
    monkeypatch.setattr(xbmc, "getCondVisibility", lambda e: calls.append(e) or False)
    assert check_visible("")
    assert not calls


def test_condition_goes_to_kodi(monkeypatch):
    monkeypatch.setattr(xbmc, "getCondVisibility", lambda e: e == "System.HasAddon(x)")
    assert check_visible("System.HasAddon(x)")
    assert not check_visible("System.HasAddon(y)")


def test_outside_kodi_passes(monkeypatch):
    monkeypatch.setattr(conditions, "IN_KODI", False)
    monkeypatch.setattr(xbmc, "getCondVisibility", lambda e: False)
    assert check_visible("System.HasAddon(x)")


def _menu() -> Menu:
    """Mainmenu with one plain item and one gated by dialog visibility."""
    return Menu(name="mainmenu", items=[
        MenuItem(name="shown", label="Shown"),
        MenuItem(name="gated", label="Gated", dialog_visible="System.HasAddon(x)"),
    ])


def test_merge_filters_dialog_visible(monkeypatch):
    monkeypatch.setattr(xbmc, "getCondVisibility", lambda e: False)
    assert [i.name for i in merge_menu(_menu(), None).items] == ["shown"]
    assert [i.name for i in merge_menu(_menu(), MenuDiff()).items] == ["shown"]
    monkeypatch.setattr(xbmc, "getCondVisibility", lambda e: True)
    assert [i.name for i in merge_menu(_menu(), None).items] == ["shown", "gated"]
    assert [i.name for i in merge_menu(_menu(), MenuDiff()).items] == ["shown", "gated"]
