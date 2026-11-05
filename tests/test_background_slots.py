"""Background buttons read the slot they write, and a new background drops the old one's keys."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from harness import harness_fixture, open_root, write_skin  # noqa: F401

from skinshortcuts.config import SkinConfig
from skinshortcuts.models.background import Background, BackgroundType

MENUS = """<menus>
  <menu name="mainmenu">
    <item name="music"><label>Music</label><action>ActivateWindow(Music)</action></item>
  </menu>
</menus>"""

PROPERTIES = """<properties>
  <buttons>
    <button id="310" property="background" type="background" suffix="true" />
    <button id="320" property="background" type="background" />
  </buttons>
</properties>"""

LIVE_PLAYLIST = Background("live-playlist", "Playlist", type=BackgroundType.LIVE_PLAYLIST)
WEATHER = Background(name="weather", label="Weather", path="$INFO[x]", type=BackgroundType.PROPERTY)
BROWSE = Background(name="browse", label="Browse", type=BackgroundType.BROWSE)


def _open(tmp_path: Path, suffix: str = ""):
    """Open the root dialog, as a widget2 subdialog when suffixed."""
    skin = write_skin(tmp_path, MENUS, properties=PROPERTIES)
    mode = "widget2" if suffix else ""
    return open_root(skin, tmp_path, property_suffix=suffix, dialog_mode=mode)


def _current_background(dialog, button_id: int) -> str:
    """Current value a property button passes to the background picker."""
    seen: list[str] = []

    def pick(_props, current_value="", _positions=None, **_kwargs):
        seen.append(current_value)

    dialog._pick_background = pick
    dialog._handle_property_button(button_id)
    return seen[0]


def test_unsuffixed_dialog_reads_the_base_background(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path)
    dialog.items[0].properties.update({"background": "base", "background.2": "slot"})
    assert _current_background(dialog, 310) == "base"


def test_suffixed_button_reads_its_slot(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path, ".2")
    dialog.items[0].properties.update({"background": "base", "background.2": "slot"})
    assert _current_background(dialog, 310) == "slot"


def test_unsuffixed_button_reads_the_key_it_writes(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path, ".2")
    dialog.items[0].properties.update({"background": "base", "background.2": "slot"})
    assert _current_background(dialog, 320) == "base"


def test_suffixed_button_preselects_its_playlist(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path, ".2")
    dialog.items[0].properties["backgroundPath.2"] = "special://slot.xsp"
    picks = [LIVE_PLAYLIST, None]
    seen: list[str] = []
    dialog._pick_background = lambda *_a, **_k: picks.pop(0)
    dialog._pick_playlist = lambda _sources, _label, current: seen.append(current)
    dialog._handle_property_button(310)
    assert seen == ["special://slot.xsp"]


def _set_songs_playlist(dialog, prefix: str) -> None:
    """Set a songs live playlist background on the first item and check its type key."""
    item = dialog.items[0]
    dialog._set_background_properties_custom(
        item, prefix, LIVE_PLAYLIST, "special://Rock.xsp", "Rock", "songs"
    )
    assert item.properties[prefix.replace("background", "backgroundPlaylistType")] == "songs"


def test_playlist_to_playlist_replaces_the_type(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path)
    _set_songs_playlist(dialog, "background")
    item = dialog.items[0]
    dialog._set_background_properties_custom(
        item, "background", LIVE_PLAYLIST, "special://Pop.xsp", "Pop", "albums"
    )
    assert item.properties["backgroundPlaylistType"] == "albums"


@pytest.mark.parametrize("prefix", ["background", "background.2"])
def test_static_background_drops_the_playlist_type(harness, tmp_path: Path, prefix: str) -> None:
    dialog = _open(tmp_path)
    _set_songs_playlist(dialog, prefix)
    dialog._set_background_properties(dialog.items[0], prefix, WEATHER)
    assert not any("PlaylistType" in key for key in dialog.items[0].properties)


def test_browsed_background_drops_the_playlist_type(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path)
    _set_songs_playlist(dialog, "background")
    dialog._set_background_properties_custom(dialog.items[0], "background", BROWSE, "/pics/a.jpg")
    assert "backgroundPlaylistType" not in dialog.items[0].properties


def test_playlist_type_does_not_reach_userdata_or_includes(harness, tmp_path: Path) -> None:
    dialog = _open(tmp_path)
    _set_songs_playlist(dialog, "background")
    dialog._set_background_properties(dialog.items[0], "background", WEATHER)
    dialog.manager.save()

    userdata = tmp_path / "userdata.json"
    output = tmp_path / "includes.xml"
    SkinConfig.load(dialog.shortcuts_path, userdata_path=str(userdata)).build_includes(output)
    stored = json.dumps(json.loads(userdata.read_text()))
    found = ["backgroundPlaylistType" in text for text in (stored, output.read_text())]
    assert found == [False, False]
