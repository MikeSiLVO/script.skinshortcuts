"""Tests for BrowseProvider art handling."""

from __future__ import annotations

from unittest.mock import patch

from skinshortcuts.providers.browse import BrowseProvider


def test_list_directory_requests_art_when_asked():
    provider = BrowseProvider()
    captured: dict = {}

    def fake_rpc(method: str, params: dict):
        captured["params"] = params
        return {"files": []}

    with patch.object(provider, "_jsonrpc", side_effect=fake_rpc):
        provider.list_directory("library://music/", include_art=True)
    assert "art" in captured["params"]["properties"]


def test_list_directory_skips_art_by_default():
    provider = BrowseProvider()
    captured: dict = {}

    def fake_rpc(method: str, params: dict):
        captured["params"] = params
        return {"files": []}

    with patch.object(provider, "_jsonrpc", side_effect=fake_rpc):
        provider.list_directory("library://music/")
    assert "art" not in captured["params"]["properties"]


def test_list_directory_prefers_poster_over_icon():
    """Poster wins over art.icon, and its remote URL is unwrapped to a stored path."""
    provider = BrowseProvider()
    fake_rpc_result = {
        "files": [
            {
                "label": "A Movie",
                "file": "D:/movies/a.mkv",
                "filetype": "file",
                "art": {
                    "poster": "image://https%3a%2f%2ffanart.tv%2fposter.jpg/",
                    "icon": "image://DefaultVideo.png/",
                },
            }
        ]
    }
    with patch.object(provider, "_jsonrpc", return_value=fake_rpc_result):
        items = provider.list_directory("videodb://movies/", include_art=True)
    assert items is not None
    assert items[0].icon == "https://fanart.tv/poster.jpg"


def test_list_directory_applies_override_to_plugin_default_icon():
    provider = BrowseProvider({"DefaultInProgressShows.png": "custom.png"})
    fake_rpc_result = {
        "files": [
            {
                "label": "Next Up",
                "file": "plugin://script.skin.info.service/nextup/",
                "filetype": "directory",
                "art": {"thumb": "image://DefaultInProgressShows.png/"},
            }
        ]
    }
    with patch.object(provider, "_jsonrpc", return_value=fake_rpc_result):
        items = provider.list_directory("plugin://script.skin.info.service/", include_art=True)
    assert items is not None
    assert items[0].icon == "custom.png"


def test_list_directory_uses_type_aware_default_when_no_per_item_art():
    """Album with empty thumb chain falls back to DefaultAlbumCover.png, not DefaultFolder."""
    provider = BrowseProvider()
    fake_rpc_result = {
        "files": [
            {
                "label": "Some Album",
                "file": "musicdb://albums/99/",
                "filetype": "directory",
                "type": "album",
                "art": {"icon": "image://DefaultAlbumCover.png/"},
            }
        ]
    }
    with patch.object(provider, "_jsonrpc", return_value=fake_rpc_result):
        items = provider.list_directory("musicdb://albums/", include_art=True)
    assert items is not None
    assert items[0].icon == "DefaultAlbumCover.png"


def test_list_directory_type_default_used_when_art_dict_empty():
    """Movie with no art at all gets DefaultMovies.png from type field."""
    provider = BrowseProvider()
    fake_rpc_result = {
        "files": [
            {
                "label": "Mystery Movie",
                "file": "videodb://movies/titles/123/",
                "filetype": "file",
                "type": "movie",
            }
        ]
    }
    with patch.object(provider, "_jsonrpc", return_value=fake_rpc_result):
        items = provider.list_directory("videodb://movies/titles/", include_art=True)
    assert items is not None
    assert items[0].icon == "DefaultMovies.png"


def test_list_directory_preserves_kodi_internal_thumb_wrapper():
    """Album art.thumb URLs use image://music@... scheme that breaks if unwrapped."""
    provider = BrowseProvider()
    fake_rpc_result = {
        "files": [
            {
                "label": "Greatest Hits",
                "file": "musicdb://albums/2/",
                "filetype": "directory",
                "art": {
                    "thumb": "image://music@D%3a%5cMusic%5cAlbum%5c01.mp3/",
                    "icon": "image://DefaultAlbumCover.png/",
                },
            }
        ]
    }
    with patch.object(provider, "_jsonrpc", return_value=fake_rpc_result):
        items = provider.list_directory("musicdb://albums/", include_art=True)
    assert items is not None
    assert items[0].icon == "image://music@D%3a%5cMusic%5cAlbum%5c01.mp3/"


def test_list_directory_falls_back_to_default_when_no_art():
    provider = BrowseProvider()
    fake_rpc_result = {
        "files": [
            {
                "label": "Something",
                "file": "smb://nas/folder/",
                "filetype": "directory",
            }
        ]
    }
    with patch.object(provider, "_jsonrpc", return_value=fake_rpc_result):
        items = provider.list_directory("smb://nas/", include_art=True)

    assert items is not None
    assert items[0].icon == "DefaultFolder.png"


def test_browse_directory_stamps_path_and_name():
    """Browse listitems carry path+name so DialogSelect layouts can bind them."""
    from skinshortcuts.dialog import pickers
    from skinshortcuts.dialog.pickers import PickersMixin
    from skinshortcuts.providers.browse import BrowseItem

    class _FakeListItem:
        def __init__(self, label: str = "", offscreen: bool = False) -> None:
            self.label = label
            self._props: dict[str, str] = {}

        def setArt(self, _art) -> None:  # noqa: N802
            pass

        def setProperty(self, name: str, value: str) -> None:  # noqa: N802
            self._props[name] = value

        def getProperty(self, name: str) -> str:  # noqa: N802
            return self._props.get(name, "")

    class _FakeProvider:
        def set_icon_overrides(self, _o) -> None:
            pass

        def list_directory(self, _path, include_art=False):
            return [
                BrowseItem("Movies", "library://video/movies/", "i", True),
                BrowseItem("A Film", "plugin://x/film", "i", False),
            ]

    picker = PickersMixin()
    picker.manager = None  # type: ignore[assignment]

    captured: dict = {}

    def fake_select(_kind, _title, listitems, **_kw):
        captured["listitems"] = listitems
        return 0  # "Use this location" ends the loop

    with patch.object(pickers, "get_browse_provider", return_value=_FakeProvider()), \
         patch.object(pickers.xbmcgui, "ListItem", _FakeListItem), \
         patch.object(pickers, "picker_select", side_effect=fake_select):
        result = picker._browse_directory("library://video/", "Videos")

    assert result == ("library://video/", "Videos", "DefaultFolder.png")

    li = captured["listitems"]
    assert li[0].getProperty("path") == "library://video/"
    assert li[0].getProperty("name") == "Videos"
    assert li[1].getProperty("path") == "library://video/movies/"
    assert li[1].getProperty("name") == "Movies"
    assert li[2].getProperty("path") == "plugin://x/film"
    assert li[2].getProperty("name") == "A Film"
