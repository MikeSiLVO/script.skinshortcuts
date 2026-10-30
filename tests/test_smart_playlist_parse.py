"""Smart playlist name and type reach both the content provider and the background picker."""

from __future__ import annotations

from pathlib import Path

import pytest
import xbmcvfs

from skinshortcuts.dialog import properties
from skinshortcuts.models.background import PlaylistSource
from skinshortcuts.providers.content import ContentProvider

XSP = '<?xml version="1.0"?><smartplaylist type="{type}"><name>{name}</name></smartplaylist>'


class _RealFile:
    """Stand-in xbmcvfs.File reading from disk."""

    def __init__(self, path):
        self._path = path

    def read(self):
        return Path(self._path).read_text(encoding="utf-8")

    def close(self):
        pass


@pytest.fixture
def playlist_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(xbmcvfs, "File", _RealFile)
    (tmp_path / "films.xsp").write_text(XSP.format(type="movies", name="My Films"))
    (tmp_path / "songs.xsp").write_text(XSP.format(type="songs", name="My Songs"))
    (tmp_path / "noname.xsp").write_text('<smartplaylist type="tvshows"></smartplaylist>')
    (tmp_path / "broken.xsp").write_text("<smartplaylist")
    (tmp_path / "plain.m3u").write_text("#EXTM3U\n")
    return str(tmp_path) + "/"


def _by_label(shortcuts):
    """Shortcuts keyed by label."""
    return {s.label: s for s in shortcuts}


def test_content_all_targets(playlist_dir):
    got = _by_label(ContentProvider()._scan_playlist_directory(playlist_dir, "videos"))
    assert set(got) == {"My Films", "My Songs", "noname", "broken", "plain"}
    assert got["My Films"].content_type == "movies"
    assert got["My Songs"].content_type == "songs"
    assert got["My Songs"].action_party.startswith("PlayerControl(PartyMode(")
    assert got["noname"].content_type == "tvshows"
    assert got["broken"].content_type == "unknown"
    assert got["plain"].content_type == ""


def test_content_video_target_drops_music_and_unreadable(playlist_dir):
    got = _by_label(ContentProvider()._scan_playlist_directory(playlist_dir, "videos", "video"))
    assert set(got) == {"My Films", "noname", "plain"}


def test_content_music_target(playlist_dir):
    got = _by_label(ContentProvider()._scan_playlist_directory(playlist_dir, "music", "music"))
    assert set(got) == {"My Songs", "plain"}


class _ListItem:
    """ListItem stand-in keeping its label readable."""

    def __init__(self, label="", offscreen=False):
        self._label = label

    def getLabel(self):  # noqa: N802
        return self._label

    def setArt(self, _art):  # noqa: N802
        pass


class _Picker(properties.PropertiesMixin):
    """PropertiesMixin with a silent log, for calling the playlist picker directly."""

    def _log(self, msg):
        pass


def test_background_picker_labels_and_types(playlist_dir, monkeypatch):
    shown = []

    def fake_select(_kind, _title, listitems, **_kw):
        shown.extend(listitems)
        return next(i for i, li in enumerate(listitems) if li.getLabel() == "Src: My Films")

    monkeypatch.setattr(properties, "picker_select", fake_select)
    monkeypatch.setattr(properties.xbmcgui, "ListItem", _ListItem)
    source = PlaylistSource(label="Src", path=playlist_dir)
    result = _Picker()._pick_playlist_from_source(source, "Src", "")
    assert result is not None
    path, label, ptype = result
    assert path.endswith("films.xsp") and label == "Src: My Films" and ptype == "movies"
    labels = sorted(li.getLabel() for li in shown)
    assert labels == ["Src: My Films", "Src: My Songs", "Src: broken", "Src: noname", "Src: plain"]
