"""Every content resolver treats a null, missing or empty JSON-RPC collection the same."""

from __future__ import annotations

import xbmc
import pytest

from skinshortcuts.models.menu import Content
from skinshortcuts.providers.content import ContentProvider, _collection


@pytest.mark.parametrize(
    "result,key,expected",
    [
        ({"favourites": [1, 2]}, "favourites", [1, 2]),
        ({"favourites": None}, "favourites", []),
        ({"limits": {}}, "favourites", []),
        ({"favourites": []}, "favourites", []),
        (None, "favourites", []),  # JSON-RPC failed
    ],
)
def test_collection_collapses_null_missing_empty(result, key, expected):
    assert _collection(result, key) == expected


_NULL_KEY_BY_METHOD = {
    "Favourites.GetFavourites": "favourites",
    "Files.GetSources": "sources",
    "Addons.GetAddons": "addons",
    "PVR.GetChannels": "channels",
    "Files.GetDirectory": "files",
    "VideoLibrary.GetGenres": "genres",
    "AudioLibrary.GetGenres": "genres",
    "AudioLibrary.GetArtists": "artists",
    "AudioLibrary.GetAlbums": "albums",
    "VideoLibrary.GetMovies": "movies",
    "VideoLibrary.GetTVShows": "tvshows",
    "VideoLibrary.GetEpisodes": "episodes",
}


def _null_rpc(method: str, _params: dict | None = None) -> dict:
    """Mimic Kodi returning an empty collection as a null-valued key."""
    key = _NULL_KEY_BY_METHOD.get(method)
    return {key: None, "limits": {}} if key else {}


@pytest.mark.parametrize(
    "source,target",
    [
        ("favourites", ""),
        ("sources", "video"),
        ("addons", "video"),
        ("pvr", "tv"),
        ("nodes", "video"),
        ("library", "genres"),
        ("library", "tvgenres"),
        ("library", "musicgenres"),
        ("library", "years"),
        ("library", "studios"),
        ("library", "actors"),
        ("library", "directors"),
        ("library", "tvdirectors"),
        ("library", "artists"),
        ("library", "albums"),
    ],
)
def test_resolve_survives_null_collection(monkeypatch, source: str, target: str):
    # PVR resolvers gate on HasTVChannels/HasRadioChannels before querying
    monkeypatch.setattr(xbmc, "getCondVisibility", lambda _expr: True)

    provider = ContentProvider()
    monkeypatch.setattr(provider, "_jsonrpc", _null_rpc)

    assert provider.resolve(Content(source=source, target=target)) == []
