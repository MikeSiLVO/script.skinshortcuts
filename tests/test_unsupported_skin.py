"""A skin without v3 config warns, and only one with built includes can be ignored."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
import xbmcgui

from skinshortcuts import entry

WARNED = "skinshortcuts-unsupported-warned"
SKIN_SETTING = "ActivateWindow(InterfaceSettings,lookandfeel.skin)"
ADDON_BROWSER = "ActivateWindow(AddonBrowser,addons://)"


@pytest.fixture(autouse=True)
def _fresh_session() -> Iterator[None]:
    xbmcgui.Window(10000).clearProperty(WARNED)
    yield
    xbmcgui.Window(10000).clearProperty(WARNED)


@pytest.fixture
def skin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, Path]:
    shortcuts = tmp_path / "skin" / "shortcuts"
    res = tmp_path / "skin" / "1080i"
    shortcuts.mkdir(parents=True)
    res.mkdir()
    marker = tmp_path / "data" / "test.skin.unsupported-ack"
    monkeypatch.setattr(entry, "get_output_paths", lambda: [str(res)])
    monkeypatch.setattr(entry, "_unsupported_marker", lambda: marker)
    return shortcuts, res, marker


@pytest.fixture
def warned(monkeypatch: pytest.MonkeyPatch) -> list[bool]:
    calls: list[bool] = []
    monkeypatch.setattr(
        entry, "_warn_unsupported", lambda _marker, built, _user_action: calls.append(built)
    )
    return calls


@pytest.fixture
def kodi(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    state: dict[str, Any] = {"choice": 0, "addons": False, "dialogs": [], "builtins": []}

    class Dialog:
        def yesno(self, _heading: str, _message: str, **_kwargs: str) -> bool:
            state["dialogs"].append("yesno")
            return state["addons"]

        def yesnocustom(self, _heading: str, _message: str, **_kwargs: str) -> int:
            state["dialogs"].append("yesnocustom")
            return state["choice"]

    monkeypatch.setattr(xbmcgui, "Dialog", Dialog)
    monkeypatch.setattr(entry.xbmc, "executebuiltin", state["builtins"].append)
    return state


def _touch(path: Path) -> None:
    """Create an empty file, making its parent folders."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()


def test_v3_config_is_supported_and_clears_the_marker(
    skin: tuple[Path, Path, Path], warned: list[bool]
) -> None:
    shortcuts, _res, marker = skin
    (shortcuts / "menus.xml").write_text("<menus/>", encoding="utf-8")
    _touch(marker)
    assert entry._skin_supported(str(shortcuts))
    assert not marker.exists()
    assert warned == []


@pytest.mark.parametrize(
    ("built", "ignored", "expected"),
    [(True, False, [True]), (True, True, []), (False, True, [False]), (False, False, [False])],
)
def test_unsupported_skin_warns_unless_ignored_and_built(
    skin: tuple[Path, Path, Path], warned: list[bool], built: bool, ignored: bool,
    expected: list[bool],
) -> None:
    shortcuts, res, marker = skin
    if built:
        (res / entry.INCLUDES_FILE).write_text("<includes/>", encoding="utf-8")
    if ignored:
        _touch(marker)
    assert not entry._skin_supported(str(shortcuts))
    assert warned == expected


@pytest.mark.parametrize(("built", "calls"), [(True, 1), (False, 2)])
def test_only_a_built_skin_warns_once_per_session(
    skin: tuple[Path, Path, Path], warned: list[bool], built: bool, calls: int
) -> None:
    shortcuts, res, _marker = skin
    if built:
        (res / entry.INCLUDES_FILE).write_text("<includes/>", encoding="utf-8")
    entry._skin_supported(str(shortcuts))
    entry._skin_supported(str(shortcuts))
    assert len(warned) == calls


def test_manage_warns_every_call_even_when_ignored(
    skin: tuple[Path, Path, Path], warned: list[bool]
) -> None:
    shortcuts, res, marker = skin
    (res / entry.INCLUDES_FILE).write_text("<includes/>", encoding="utf-8")
    _touch(marker)
    entry._skin_supported(str(shortcuts), menus_only=True, user_action=True)
    entry._skin_supported(str(shortcuts), menus_only=True, user_action=True)
    assert warned == [True, True]


def test_manage_needs_menus_not_views(skin: tuple[Path, Path, Path], warned: list[bool]) -> None:
    shortcuts, _res, _marker = skin
    (shortcuts / "views.xml").write_text("<views/>", encoding="utf-8")
    assert entry._skin_supported(str(shortcuts))
    assert not entry._skin_supported(str(shortcuts), menus_only=True, user_action=True)


@pytest.mark.parametrize(("addons", "window"), [(False, SKIN_SETTING), (True, ADDON_BROWSER)])
def test_unbuilt_skin_opens_one_window(
    kodi: dict[str, Any], tmp_path: Path, addons: bool, window: str
) -> None:
    kodi["addons"] = addons
    entry._warn_unsupported(tmp_path / "marker", False, False)
    assert kodi["dialogs"] == ["yesno"]
    assert kodi["builtins"] == [window]


@pytest.mark.parametrize(
    ("choice", "builtins", "marked"),
    [(1, [SKIN_SETTING], False), (2, [], True), (0, [], False), (-1, [], False)],
)
def test_built_skin_choices(
    kodi: dict[str, Any], tmp_path: Path, choice: int, builtins: list[str], marked: bool
) -> None:
    kodi["choice"] = choice
    marker = tmp_path / "data" / "marker"
    entry._warn_unsupported(marker, True, False)
    assert kodi["dialogs"] == ["yesnocustom"]
    assert kodi["builtins"] == builtins
    assert marker.exists() == marked


@pytest.mark.parametrize(
    ("choice", "builtins"),
    [(1, [SKIN_SETTING]), (2, [ADDON_BROWSER]), (0, []), (-1, [])],
)
def test_user_action_choices_never_mark(
    kodi: dict[str, Any], tmp_path: Path, choice: int, builtins: list[str]
) -> None:
    kodi["choice"] = choice
    marker = tmp_path / "data" / "marker"
    entry._warn_unsupported(marker, True, True)
    assert kodi["builtins"] == builtins
    assert not marker.exists()


@pytest.mark.parametrize(
    ("action", "calls"),
    [("widgets", 2), ("shortcuts", 2), ("resetall", 2), ("reset", 2), ("hidesubmenu", 0)],
)
def test_v2_skin_actions_warn_instead_of_running(
    skin: tuple[Path, Path, Path], warned: list[bool], monkeypatch: pytest.MonkeyPatch,
    action: str, calls: int,
) -> None:
    shortcuts, res, marker = skin
    (res / entry.INCLUDES_FILE).write_text("<includes/>", encoding="utf-8")
    _touch(marker)
    ran: list[str] = []
    monkeypatch.setattr(entry, "reset_all", lambda *_a: ran.append("resetall"))
    entry._dispatch({"type": action, "path": str(shortcuts), "menu": "mainmenu"})
    entry._dispatch({"type": action, "path": str(shortcuts), "menu": "mainmenu"})
    assert len(warned) == calls
    assert ran == []


def test_unknown_action_on_a_v3_skin_stays_quiet(
    skin: tuple[Path, Path, Path], warned: list[bool]
) -> None:
    shortcuts, _res, _marker = skin
    (shortcuts / "views.xml").write_text("<views/>", encoding="utf-8")
    entry._dispatch({"type": "widgets", "path": str(shortcuts)})
    assert warned == []
