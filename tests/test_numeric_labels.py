"""Digit-only labels from the user or the script show as numbers, not Kodi string IDs."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
import xbmc

from skinshortcuts.dialog.items import ItemsMixin
from skinshortcuts.localize import resolve_label
from skinshortcuts.models.menu import Menu, MenuItem
from skinshortcuts.providers.content import ContentProvider


def test_skin_string_ids_still_resolve(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(xbmc, "getLocalizedString", lambda num: {744: "Files"}.get(num, ""))
    assert resolve_label("744") == "Files"


def test_number_wrapper_resolves_to_its_digits() -> None:
    assert resolve_label("$NUMBER[2019]") == "2019"


def test_library_years_are_not_string_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = ContentProvider()
    reply = {"movies": [{"year": 2019}]}
    monkeypatch.setattr(provider, "_jsonrpc", lambda *_a, **_k: json.loads(json.dumps(reply)))
    labels = [shortcut.label for shortcut in provider._get_video_years("movie")]
    assert labels == ["$NUMBER[2019]"]


def test_digit_only_rename_is_not_a_string_id(monkeypatch: pytest.MonkeyPatch) -> None:
    item = MenuItem(name="movies", label="Movies")
    stored: dict[str, str] = {}

    class Keyboard:
        def __init__(self, *_a: object) -> None:
            pass

        def doModal(self) -> None:  # noqa: N802
            pass

        def isConfirmed(self) -> bool:  # noqa: N802
            return True

        def getText(self) -> str:  # noqa: N802
            return "24"

    monkeypatch.setattr(xbmc, "Keyboard", Keyboard, raising=False)
    manager = SimpleNamespace(
        working={"mainmenu": Menu(name="mainmenu")},
        set_label=lambda _menu, _item, label: stored.setdefault("label", label),
    )
    dialog = SimpleNamespace(
        manager=manager,
        menu_id="mainmenu",
        _get_selected_item=lambda: item,
        _refresh_selected_item=lambda: None,
    )
    ItemsMixin._set_label(dialog)  # type: ignore[arg-type]
    assert stored["label"] == "$NUMBER[24]"


def test_digit_only_typed_label_is_not_a_string_id(monkeypatch: pytest.MonkeyPatch) -> None:
    import types

    import xbmcgui

    from skinshortcuts.dialog.pickers import PickersMixin
    from skinshortcuts.models.menu import Input

    for name in ("INPUT_ALPHANUM", "INPUT_NUMERIC", "INPUT_IPADDRESS", "INPUT_PASSWORD"):
        monkeypatch.setattr(xbmcgui, name, 0, raising=False)
    monkeypatch.setattr(xbmcgui.Dialog, "input", lambda self, *a, **k: "24", raising=False)
    handle = PickersMixin._handle_input_selection.__get__(types.SimpleNamespace())
    shortcut = handle(Input(label="Custom", for_="label"))
    assert shortcut.label == "$NUMBER[24]"
