"""A Kodi library node types a widget without asking; anything else leaves the type open."""

from __future__ import annotations

from unittest.mock import patch

from skinshortcuts.providers.content import library_node_type

_NODES = {
    "special://profile/library/video/addons.xml": (
        '<node type="folder"><label>1037</label><path>addons://sources/video/</path></node>'
    ),
    "special://profile/library/video/movies/genres.xml": (
        '<node type="filter"><content>movies</content><group>genres</group></node>'
    ),
    "special://profile/library/video/movies/titles.xml": (
        '<node type="filter"><content>movies</content></node>'
    ),
    "special://profile/library/video/movies/tvshows.xml": (
        '<node type="folder"><path>videodb://tvshows/titles/</path></node>'
    ),
    "special://xbmc/system/library/music/albums.xml": (
        '<node type="filter"><content>albums</content></node>'
    ),
}

_DIRS = {
    "special://profile/library/video/",
    "special://profile/library/video/movies/",
    "special://xbmc/system/library/music/",
}


class _FakeFile:
    """Stand-in xbmcvfs.File reading node XML from the fixture map."""

    def __init__(self, path: str) -> None:
        self._content = _NODES[path]

    def read(self) -> str:
        return self._content

    def close(self) -> None:
        pass


def _fake_exists(path: str) -> bool:
    """Stand-in xbmcvfs.exists for the fixture nodes and folders."""
    return path in _NODES or path in _DIRS


def _node_type(path: str) -> str:
    """Node type library_node_type reports for a path against the fixture nodes."""
    with patch("xbmcvfs.exists", side_effect=_fake_exists), \
         patch("xbmcvfs.File", _FakeFile):
        return library_node_type(path)


def test_addons_folder_node_types_as_addons():
    assert _node_type("library://video/addons.xml/") == "addons"


def test_grouped_filter_node_types_as_its_rows():
    assert _node_type("library://video/movies/genres.xml/") == "genres"


def test_ungrouped_filter_node_types_as_its_content():
    assert _node_type("library://video/movies/titles.xml/") == "movies"


def test_other_folder_node_leaves_the_type_open():
    assert _node_type("library://video/movies/tvshows.xml/") == ""


def test_folder_of_nodes_leaves_the_type_open():
    assert _node_type("library://video/movies/") == ""
    assert _node_type("library://video/") == ""


def test_non_library_path_leaves_the_type_open():
    assert _node_type("plugin://plugin.video.youtube/") == ""


def test_system_library_serves_a_host_the_profile_lacks():
    assert _node_type("library://music/albums.xml/") == "albums"
