"""A failed userdata write is retried once, and callers act on the real result."""

from __future__ import annotations

import json
import os
import types
from pathlib import Path

import pytest
import xbmc
import xbmcgui

from skinshortcuts import entry
from skinshortcuts import manager as manager_module
from skinshortcuts.dialog.base import DialogBaseMixin
from skinshortcuts.userdata import UserData, save_userdata


@pytest.fixture
def no_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    """A Monitor whose wait returns at once without an abort."""
    monitor = type("Monitor", (), {"abortRequested": lambda self: False,
                                    "waitForAbort": lambda self, _timeout=0: False})
    monkeypatch.setattr(xbmc, "Monitor", monitor)


def _flaky_replace(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Make the first os.replace fail as a transient lock would; returns the call log."""
    calls: list[str] = []
    real = os.replace

    def replace(src, dst):
        calls.append(str(dst))
        if len(calls) == 1:
            raise PermissionError("locked")
        return real(src, dst)

    monkeypatch.setattr(os, "replace", replace)
    return calls


def test_a_failed_write_reports_false(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    def fail(_src, _dst):
        raise PermissionError("locked")

    monkeypatch.setattr(os, "replace", fail)
    assert save_userdata(UserData(), str(tmp_path / "userdata.json")) is False


def test_a_transient_failure_is_retried_once(tmp_path: Path, monkeypatch, no_wait):
    path = tmp_path / "userdata.json"
    calls = _flaky_replace(monkeypatch)
    assert save_userdata(UserData(views={"library": {"movies": "500"}}), str(path)) is True
    assert len(calls) == 2
    assert json.loads(path.read_text(encoding="utf-8"))["views"] == {"library": {"movies": "500"}}


def test_close_reports_a_failed_save(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(xbmcgui.WindowXMLDialog, "close", lambda self: None, raising=False)
    stub = types.SimpleNamespace(
        dialog_mode="",
        is_child=False,
        changes_saved=False,
        manager=types.SimpleNamespace(has_changes=lambda: True, save=lambda: False),
    )
    DialogBaseMixin.close.__get__(stub)()
    assert stub.changes_saved is False


@pytest.mark.parametrize("args", [{"type": "resetsubmenus"}, {"type": "reset", "menu": "mainmenu"}])
def test_reset_skips_the_rebuild_after_a_failed_save(monkeypatch, args: dict[str, str]):
    builds: list[str] = []
    fake = types.SimpleNamespace(
        reset_all_submenus=lambda: True,
        reset_menu=lambda _menu: True,
        reset_menu_tree=lambda _menu: True,
        save=lambda: False,
    )
    monkeypatch.setattr(manager_module, "MenuManager", lambda _path: fake)
    monkeypatch.setattr(entry, "build_includes", lambda path, *a, **k: builds.append(path))
    monkeypatch.setattr(entry, "get_shortcuts_path", lambda: "skin")
    monkeypatch.setattr(entry, "_skin_supported", lambda *_a, **_k: True)
    monkeypatch.setattr(entry, "LANGUAGE", lambda _id: "%s")
    monkeypatch.setattr(xbmcgui.Dialog, "yesno", lambda self, *a, **k: True, raising=False)
    entry._dispatch(args)
    assert builds == []
