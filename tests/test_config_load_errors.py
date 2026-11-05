"""A config file that cannot be loaded stops each action with the loader's toast, no traceback."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from harness import HarnessDialog, harness_fixture  # noqa: F401

from skinshortcuts import entry

ACTIONS = [
    ["type=buildxml", "force=true"],
    ["type=manage"],
    ["type=reset", "menu=mainmenu"],
    ["type=resetsubmenus"],
    ["type=clear", "menu=mainmenu", "item=movies"],
    ["type=viewselect", "content=movies"],
    ["type=skinstring"],
]


@pytest.fixture
def broken(tmp_path: Path) -> Path:
    """A shortcuts folder whose menus.xml and widgets.xml do not parse."""
    for name in ("menus", "widgets"):
        (tmp_path / f"{name}.xml").write_text(f"<{name}><", encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("args", ACTIONS, ids=[a[0].removeprefix("type=") for a in ACTIONS])
def test_action_stops_with_one_toast(
    harness, broken: Path, monkeypatch: pytest.MonkeyPatch, args: list[str]
) -> None:
    """The action returns with no error line, and the loader's toast is the only one."""
    lines: list[tuple[int, str]] = []
    toasts: list[str] = []
    monkeypatch.setattr("xbmc.log", lambda msg, level: lines.append((level, msg)))
    monkeypatch.setattr(
        "xbmcgui.Dialog.notification", lambda _self, h, m, *_: toasts.append(f"{h}: {m}")
    )
    monkeypatch.setattr("xbmcgui.Dialog.yesno", lambda *_a, **_k: True, raising=False)
    monkeypatch.setattr(entry, "LANGUAGE", lambda _id: "%s")
    monkeypatch.setattr(sys, "argv", ["default.py", *args, f"path={broken}", f"output={broken}"])
    entry.main()
    assert [msg for level, msg in lines if level >= 3] == []
    assert len(toasts) == 1 and "could not be loaded (see log)" in toasts[0]


def test_dialog_closes_on_load_error(harness, broken: Path) -> None:
    """The management dialog closes from onInit, showing no items."""
    dialog = HarnessDialog(menu_id="mainmenu", shortcuts_path=str(broken))
    dialog.onInit()
    assert dialog.closed
    assert dialog.manager is None and dialog.items == []
