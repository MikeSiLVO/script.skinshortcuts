"""Tests for content provider target aliasing and normalization."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from skinshortcuts.providers.browse import normalize_image
from skinshortcuts.providers.content import (
    _ADDONS_TARGET_ALIASES,
    _PLAYLIST_TARGET_ALIASES,
    _SOURCES_TARGET_ALIASES,
    ContentProvider,
)


@pytest.fixture
def provider() -> ContentProvider:
    return ContentProvider()


@pytest.mark.parametrize(
    "target,expected",
    [
        ("video", "video"),
        ("videos", "video"),
        ("music", "music"),
        ("pictures", "pictures"),
        ("picture", "pictures"),
        ("files", "files"),
        ("file", "files"),
        ("programs", "programs"),
        ("program", "programs"),
    ],
)
def test_sources_aliases(target: str, expected: str):
    assert _SOURCES_TARGET_ALIASES[target] == expected


@pytest.mark.parametrize(
    "target,expected",
    [
        ("video", "video"),
        ("videos", "video"),
        ("audio", "audio"),
        ("music", "audio"),
        ("image", "image"),
        ("images", "image"),
        ("picture", "image"),
        ("pictures", "image"),
        ("executable", "executable"),
        ("program", "executable"),
        ("programs", "executable"),
        ("game", "game"),
        ("games", "game"),
    ],
)
def test_addons_aliases(target: str, expected: str):
    assert _ADDONS_TARGET_ALIASES[target] == expected


def test_playlist_aliases_drops_audio():
    assert _PLAYLIST_TARGET_ALIASES == {
        "video": "video",
        "videos": "video",
        "music": "music",
    }
    assert "audio" not in _PLAYLIST_TARGET_ALIASES


def test_sources_unknown_target_returns_empty(provider: ContentProvider):
    result = provider._resolve_sources("tvshows")
    assert result == []


def test_addons_unknown_target_returns_empty(provider: ContentProvider):
    result = provider._resolve_addons("bogus")
    assert result == []


def test_playlists_unknown_target_returns_empty(provider: ContentProvider):
    result = provider._resolve_playlists("bogus")
    assert result == []


def test_sources_empty_target_defaults_to_video(provider: ContentProvider):
    captured: dict = {}

    def fake_rpc(method: str, params: dict):
        captured["params"] = params
        return {"sources": []}

    with patch.object(provider, "_jsonrpc", side_effect=fake_rpc):
        provider._resolve_sources("")

    assert captured["params"]["media"] == "video"


def test_addons_empty_target_defaults_to_video(provider: ContentProvider):
    captured: dict = {}

    def fake_rpc(method: str, params: dict):
        captured["params"] = params
        return {"addons": []}

    with patch.object(provider, "_jsonrpc", side_effect=fake_rpc):
        provider._resolve_addons("")

    assert captured["params"]["content"] == "video"


def test_normalize_image_unwraps_and_decodes():
    encoded = "image://special%3a%2f%2fskin%2fmedia%2fmovies.png/"
    assert normalize_image(encoded) == "special://skin/media/movies.png"


def test_normalize_image_passes_plain_paths_through():
    assert normalize_image("DefaultMovies.png") == "DefaultMovies.png"
    assert normalize_image("") == ""


def test_addons_pluginsource_is_browsable_under_executable(provider: ContentProvider):
    fake_rpc = {
        "addons": [
            {
                "addonid": "plugin.program.autowidget",
                "name": "AutoWidget",
                "type": "xbmc.python.pluginsource",
                "thumbnail": "",
            },
            {
                "addonid": "script.globalsearch",
                "name": "Global Search",
                "type": "xbmc.python.script",
                "thumbnail": "",
            },
        ]
    }
    with patch.object(provider, "_jsonrpc", return_value=fake_rpc):
        result = provider._resolve_addons("programs")

    by_label = {r.label: r for r in result}

    aw = by_label["AutoWidget"]
    assert aw.browse_path == "plugin://plugin.program.autowidget/"
    assert aw.browse_window == "programs"
    assert aw.action == ""

    gs = by_label["Global Search"]
    assert gs.action == "RunAddon(script.globalsearch)"
    assert gs.browse_path == ""


def test_addons_does_not_request_invalid_type_property(provider: ContentProvider):
    captured: dict = {}

    def fake_rpc(method: str, params: dict):
        captured["params"] = params
        return {"addons": []}

    with patch.object(provider, "_jsonrpc", side_effect=fake_rpc):
        provider._resolve_addons("video")

    assert "type" not in captured["params"]["properties"]


def test_addons_script_under_video_target_launches_not_browses(provider: ContentProvider):
    fake_rpc = {
        "addons": [
            {
                "addonid": "script.somevideohelper",
                "name": "Video Helper",
                "type": "xbmc.python.script",
                "thumbnail": "",
            },
        ]
    }
    with patch.object(provider, "_jsonrpc", return_value=fake_rpc):
        result = provider._resolve_addons("video")

    assert len(result) == 1
    assert result[0].action == "RunAddon(script.somevideohelper)"
    assert result[0].browse_path == ""


def test_sources_populates_browse_path(provider: ContentProvider):
    fake_rpc = {
        "sources": [
            {"file": "smb://server/movies/", "label": "Movies"},
            {"file": "/home/user/tvshows/", "label": "TV"},
        ]
    }
    with patch.object(provider, "_jsonrpc", return_value=fake_rpc):
        result = provider._resolve_sources("videos")

    assert len(result) == 2
    assert result[0].browse_path == "smb://server/movies/"
    assert result[0].browse_window == "videos"
    assert result[1].browse_path == "/home/user/tvshows/"
    assert result[1].browse_window == "videos"


def test_sources_plural_videos_normalizes(provider: ContentProvider):
    captured: dict = {}

    def fake_rpc(method: str, params: dict):
        captured["params"] = params
        return {"sources": []}

    with patch.object(provider, "_jsonrpc", side_effect=fake_rpc):
        provider._resolve_sources("videos")

    assert captured["params"] == {"media": "video"}


def test_sources_skips_kodi_addons_row(provider: ContentProvider):
    """Kodi's computed addons:// row is not a configured source."""
    from skinshortcuts.models.menu import Content

    fake_rpc = {
        "sources": [
            {"file": "D:\\HD Movies\\", "label": "Movies (D)"},
            {"file": "multipath://B%3a%5cMy%20TV%5c/", "label": "TV (B)"},
            {"file": "addons://sources/video/", "label": "Video add-ons"},
        ]
    }

    with patch.object(provider, "_jsonrpc", return_value=fake_rpc):
        resolved = provider.resolve(Content(source="sources", target="video"))

    assert [r.label for r in resolved] == ["Movies (D)", "TV (B)"]
