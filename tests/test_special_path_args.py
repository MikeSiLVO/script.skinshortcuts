"""RunScript path= and output= accept special:// paths."""

from __future__ import annotations

from pathlib import Path

import pytest
import xbmcvfs

from skinshortcuts import entry

MENUS_XML = """<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>Noop</action></item>
  </menu>
</menus>"""


@pytest.fixture
def skin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, list[Path]]:
    root = tmp_path / "skin"
    (root / "shortcuts").mkdir(parents=True)
    (root / "16x9").mkdir()
    (root / "shortcuts" / "menus.xml").write_text(MENUS_XML, encoding="utf-8")

    def translate(path: str) -> str:
        text = str(path)
        if text.startswith("special://skin/"):
            return str(root / text[len("special://skin/") :])
        if text.startswith("special://"):
            return str(tmp_path / "kodi" / text[len("special://") :])
        return text

    monkeypatch.setattr(xbmcvfs, "translatePath", translate)
    warned: list[Path] = []
    monkeypatch.setattr(entry, "_warn_unsupported", lambda marker, _built: warned.append(marker))
    return root, warned


def test_buildxml_with_real_paths(skin: tuple[Path, list[Path]]) -> None:
    root, _warned = skin
    entry._dispatch({
        "type": "buildxml",
        "path": str(root / "shortcuts"),
        "output": str(root / "16x9"),
        "force": "true",
    })
    assert (root / "16x9" / "script-skinshortcuts-includes.xml").exists()


def test_buildxml_with_special_output(skin: tuple[Path, list[Path]]) -> None:
    root, _warned = skin
    entry._dispatch({
        "type": "buildxml",
        "path": str(root / "shortcuts"),
        "output": "special://skin/16x9/",
        "force": "true",
    })
    assert (root / "16x9" / "script-skinshortcuts-includes.xml").exists()


def test_buildxml_with_special_paths(skin: tuple[Path, list[Path]]) -> None:
    root, warned = skin
    entry._dispatch({
        "type": "buildxml",
        "path": "special://skin/shortcuts/",
        "output": "special://skin/16x9/",
        "force": "true",
    })
    assert not warned
    assert (root / "16x9" / "script-skinshortcuts-includes.xml").exists()


def test_manage_with_special_path(
    skin: tuple[Path, list[Path]], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, warned = skin
    opened: list[str] = []
    from skinshortcuts import dialog

    monkeypatch.setattr(
        dialog, "show_management_dialog", lambda **k: opened.append(k["shortcuts_path"])
    )
    entry._dispatch({"type": "manage", "path": "special://skin/shortcuts/"})
    assert not warned
    assert opened and Path(opened[0]) == root / "shortcuts"
