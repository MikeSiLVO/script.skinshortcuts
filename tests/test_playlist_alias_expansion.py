"""Playlist scanning resolves multipath aliases to concrete component paths."""

from __future__ import annotations

from unittest.mock import patch

from skinshortcuts.providers.content import scan_playlist_files

_VIDEOPLAYLISTS_MULTIPATH = (
    "multipath://special%3a%2f%2fprofile%2fplaylists%2fvideo%2f"
    "/special%3a%2f%2fprofile%2fplaylists%2fmixed%2f/"
)

_COMPONENT_FILES = {
    "special://profile/playlists/video/": ["Action.xsp"],
    "special://profile/playlists/mixed/": ["Mixed.xsp"],
}


def _fake_listdir(directory: str):
    """Stand-in xbmcvfs.listdir returning the fixture files for a component folder."""
    return [], _COMPONENT_FILES.get(directory, [])


def test_alias_expands_to_component_paths():
    with patch("xbmcvfs.translatePath", return_value=_VIDEOPLAYLISTS_MULTIPATH), \
         patch("xbmcvfs.listdir", side_effect=_fake_listdir):
        result = scan_playlist_files("special://videoplaylists/")

    assert ("Action", "special://profile/playlists/video/Action.xsp") in result
    assert ("Mixed", "special://profile/playlists/mixed/Mixed.xsp") in result
    # the corrupt alias+filename form must never be stored
    assert all(not path.startswith("special://videoplaylists/") for _, path in result)


def test_plain_dir_passes_through_unchanged():
    def fake_listdir(directory: str):
        assert directory == "special://profile/playlists/video/"
        return [], ["Action.xsp"]

    with patch("xbmcvfs.translatePath", return_value="/tmp/x/video/"), \
         patch("xbmcvfs.listdir", side_effect=fake_listdir):
        result = scan_playlist_files("special://profile/playlists/video/")

    assert result == [("Action", "special://profile/playlists/video/Action.xsp")]
