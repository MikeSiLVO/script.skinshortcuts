"""Stub Kodi modules and put resources/lib on sys.path, for importing the add-on outside Kodi."""

from __future__ import annotations

import os
import sys
import tempfile
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESOURCES_LIB = ROOT / "resources" / "lib"
if str(RESOURCES_LIB) not in sys.path:
    sys.path.insert(0, str(RESOURCES_LIB))

_KODI_TMP = Path(tempfile.gettempdir()) / "skinshortcuts-tests-kodi"


def _translate_path(p: str) -> str:
    """Translate Kodi special:// paths into a tempdir so tests don't pollute the repo."""
    s = str(p)
    if s.startswith("special://"):
        return str(_KODI_TMP / s[len("special://"):])
    return s


def _stub_module(name: str, **attrs: object) -> types.ModuleType:
    """Stub a module in sys.modules with given attributes, reusing one already there."""
    mod = sys.modules.get(name) or types.ModuleType(name)
    for key, val in attrs.items():
        setattr(mod, key, val)
    sys.modules[name] = mod
    return mod


class _FakeAddon:
    """Stub Addon returning empty settings and strings."""

    def getAddonInfo(self, _key: str) -> str:  # noqa: N802
        return ""

    def getSettingString(self, _key: str) -> str:  # noqa: N802
        return ""

    def getSettingBool(self, _key: str) -> bool:  # noqa: N802
        return False

    def getSettingInt(self, _key: str) -> int:  # noqa: N802
        return 0

    def getLocalizedString(self, _id: int) -> str:  # noqa: N802
        return ""


_stub_module(
    "xbmc",
    log=lambda *a, **k: None,
    LOGDEBUG=0,
    LOGINFO=1,
    LOGWARNING=2,
    LOGERROR=3,
    LOGFATAL=4,
    getCondVisibility=lambda _expr: False,
    getInfoLabel=lambda _key: "",
    getLocalizedString=lambda _id: "",
    executebuiltin=lambda *a, **k: None,
    translatePath=_translate_path,
    getSkinDir=lambda: "test.skin",
    Monitor=type(
        "Monitor",
        (),
        {"abortRequested": lambda self: False, "waitForAbort": lambda self, _t=0: False},
    ),
)
_stub_module("xbmcaddon", Addon=lambda *_a, **_k: _FakeAddon())


def _listdir(p: str) -> tuple[list[str], list[str]]:
    """List directory contents, returning (dirs, files) tuple. Uses real filesystem."""
    import os

    resolved = _translate_path(p)
    if not os.path.isdir(resolved):
        return [], []
    dirs: list[str] = []
    files: list[str] = []
    for name in sorted(os.listdir(resolved)):
        full = os.path.join(resolved, name)
        if os.path.isdir(full):
            dirs.append(name)
        else:
            files.append(name)
    return dirs, files


def _delete(p: str) -> bool:
    """Delete a file at its translated path; False when removal fails."""
    import os

    try:
        os.remove(_translate_path(p))
        return True
    except OSError:
        return False


_stub_module(
    "xbmcvfs",
    translatePath=_translate_path,
    exists=lambda p: os.path.exists(_translate_path(p)),
    mkdirs=lambda _p: True,
    listdir=_listdir,
    delete=_delete,
    File=type("File", (), {}),
)


class _FakeWindow:
    """Stub Window whose properties persist per window id, shared across instances."""

    _instances: dict = {}

    def __init__(self, window_id: int = 0) -> None:
        self.window_id = window_id
        self.props = _FakeWindow._instances.setdefault(window_id, {})

    def setProperty(self, name: str, value: str) -> None:  # noqa: N802
        self.props[name] = value

    def clearProperty(self, name: str) -> None:  # noqa: N802
        self.props.pop(name, None)

    def getProperty(self, name: str) -> str:  # noqa: N802
        return self.props.get(name, "")


_stub_module(
    "xbmcgui",
    Dialog=type(
        "Dialog",
        (),
        {"notification": lambda self, *a, **k: None, "ok": lambda self, *a, **k: None},
    ),
    WindowXMLDialog=type("WindowXMLDialog", (), {}),
    ListItem=type("ListItem", (), {}),
    Window=_FakeWindow,
    getCurrentWindowDialogId=lambda: 0,
)
_stub_module("xbmcplugin")


@pytest.fixture(autouse=True)
def _fresh_notify_state():
    """Clear the log module's dedupe sets per test, as each RunScript starts a fresh interpreter."""
    from skinshortcuts import log

    log._logged.clear()
    log._notified.clear()
