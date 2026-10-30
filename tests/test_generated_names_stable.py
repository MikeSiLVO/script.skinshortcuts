"""Names generated for browsed paths and typed input depend only on the value, not the process."""

from __future__ import annotations

import types

import pytest
import xbmcgui

import skinshortcuts.dialog.pickers as pickers
from skinshortcuts.dialog.pickers import PickersMixin
from skinshortcuts.models.menu import Input
from skinshortcuts.models.widget import Widget

FOLDER = ("plugin://plugin.video.x/movies/", "Movies", "DefaultFolder.png")


def _names(monkeypatch: pytest.MonkeyPatch, make) -> list[str]:
    """The generated name under two different string hash seeds."""
    names = []
    for seed in (1, 2):
        monkeypatch.setattr(pickers, "hash", lambda _value, seed=seed: seed, raising=False)
        names.append(make().name)
    return names


def _picker() -> PickersMixin:
    """PickersMixin stand-in whose directory browse returns a fixed folder."""
    stub = types.SimpleNamespace(_browse_directory=lambda *_a, **_k: FOLDER)
    stub._map_widget_type_to_target = PickersMixin._map_widget_type_to_target.__get__(stub)
    return stub


def test_browsed_widget_name_is_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    widget = Widget(name="addons", label="Addons", path="addons://sources/video/", type="movies")
    browse = PickersMixin._browse_widget_path.__get__(_picker())
    first, second = _names(monkeypatch, lambda: browse(widget))
    assert first == second


def test_browsed_shortcut_name_is_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    browse = PickersMixin._browse_path.__get__(_picker())
    first, second = _names(monkeypatch, lambda: browse("sources://video/", "Video"))
    assert first == second


def test_typed_input_name_is_stable(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in ("INPUT_ALPHANUM", "INPUT_NUMERIC", "INPUT_IPADDRESS", "INPUT_PASSWORD"):
        monkeypatch.setattr(xbmcgui, name, 0, raising=False)
    monkeypatch.setattr(xbmcgui.Dialog, "input", lambda self, *a, **k: "Noop", raising=False)
    handle = PickersMixin._handle_input_selection.__get__(types.SimpleNamespace())
    first, second = _names(monkeypatch, lambda: handle(Input(label="Custom")))
    assert first == second
