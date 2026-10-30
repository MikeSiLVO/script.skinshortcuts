"""The skinstring picker stores each picked value whole and clears a value the new widget lacks."""

from __future__ import annotations

from pathlib import Path

import pytest
import xbmc

from skinshortcuts import skinstring
from skinshortcuts.models.widget import Widget

MENUS_XML = "<menus><menu name='mainmenu' /></menus>"
WIDGETS_XML = "<widgets><widget name='w' label='W'><path>videodb://x/</path></widget></widgets>"
ALBUMS = Widget(name="a", label="Albums", path="musicdb://albums/", type="albums")
PARAMS = {"skinPath": "W.Path", "skinLabel": "W.Label", "skinType": "W.Type"}


def _trim(param: str) -> str:
    """Trim one pair of surrounding quotes, or the quotes of a name="value" form."""
    if len(param) > 1 and param[0] == '"' and param[-1] == '"':
        return param[1:-1]
    if len(param) > 3 and param[-1] == '"':
        quote = param.find('"')
        if 1 < quote < len(param) - 1 and param[quote - 1] == "=":
            return param[:quote] + param[quote + 1 : -1]
    return param


def split_params(text: str) -> list[str]:
    """Split a builtin's parameters as Kodi's CUtil::SplitParams does."""
    params: list[str] = []
    param = ""
    in_quotes = last_escaped = False
    in_function = white = 0
    for pos, ch in enumerate(text):
        escaped = pos > 0 and text[pos - 1] == "\\" and not last_escaped
        last_escaped = escaped
        if in_quotes:
            if ch == '"' and not escaped:
                in_quotes = False
        else:
            if ch == '"' and not escaped:
                in_quotes = True
            if in_function and ch == ")":
                in_function -= 1
            if ch == "(":
                in_function += 1
            if not in_function and ch == ",":
                params.append(_trim(param[:white] if white else param))
                param, white = "", 0
                continue
        if ch in '"\\' and escaped:
            param = param[:-1] + ch
            continue
        if ch == " " and not in_quotes:
            if not param:
                continue
            white = white or len(param)
        else:
            white = 0
        param += ch
    param = _trim(param[:white] if white else param)
    if param or params:
        params.append(param)
    return params


class SkinStrings:
    """Skin string store driven the way Kodi runs Skin.SetString and Skin.Reset."""

    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def execute(self, builtin: str) -> None:
        """Execute a Skin.SetString or Skin.Reset builtin on the store."""
        function = builtin[: builtin.find("(")].lower()
        params = split_params(builtin[builtin.find("(") + 1 : builtin.rfind(")")])
        if function == "skin.setstring" and len(params) > 1:
            self.values[params[0]] = params[1]
        elif function == "skin.reset":
            self.values.pop(params[0], None)


@pytest.fixture
def store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[SkinStrings, Path]:
    (tmp_path / "menus.xml").write_text(MENUS_XML, encoding="utf-8")
    (tmp_path / "widgets.xml").write_text(WIDGETS_XML, encoding="utf-8")
    strings = SkinStrings()
    monkeypatch.setattr(xbmc, "executebuiltin", strings.execute)
    return strings, tmp_path


def pick(monkeypatch: pytest.MonkeyPatch, path: Path, widget: Widget) -> None:
    """Pick a given widget through the skinstring picker."""
    monkeypatch.setattr(
        skinstring._StandalonePicker, "_pick_widget_from_groups", lambda self, *a, **k: widget
    )
    skinstring.pick_widget_skinstring(str(path), PARAMS)


def test_split_params_port_matches_kodi() -> None:
    assert split_params('W.Path,"a,b"') == ["W.Path", "a,b"]
    assert split_params("W.Path,a,b") == ["W.Path", "a", "b"]
    assert split_params(r'W.Path,"\\\\nas\\share"') == ["W.Path", r"\\nas\share"]


def test_plain_values_are_stored(
    store: tuple[SkinStrings, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    strings, path = store
    pick(monkeypatch, path, ALBUMS)
    assert strings.values == {
        "W.Path": "musicdb://albums/", "W.Label": "Albums", "W.Type": "albums",
    }


@pytest.mark.parametrize(
    ("path_value", "label"),
    [
        ("plugin://plugin.video.themoviedb.helper/?info=discover&with_genres=28,12", "Action"),
        ("videodb://movies/titles/", "Action, Adventure"),
        (r"\\nas\share\films", "Films"),
    ],
)
def test_values_are_stored_whole(
    store: tuple[SkinStrings, Path], monkeypatch: pytest.MonkeyPatch, path_value: str, label: str
) -> None:
    strings, path = store
    pick(monkeypatch, path, Widget(name="w", label=label, path=path_value, type="movies"))
    assert strings.values["W.Path"] == path_value
    assert strings.values["W.Label"] == label


def test_untyped_widget_clears_the_previous_type(
    store: tuple[SkinStrings, Path], monkeypatch: pytest.MonkeyPatch
) -> None:
    strings, path = store
    pick(monkeypatch, path, ALBUMS)
    pick(monkeypatch, path, Widget(name="m", label="Movies", path="videodb://movies/titles/"))
    assert "W.Type" not in strings.values
