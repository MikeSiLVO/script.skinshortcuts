"""Widget target follows the window the provider resolved each item into."""

from __future__ import annotations

from unittest.mock import patch

from skinshortcuts.dialog import pickers
from skinshortcuts.dialog.pickers import PickersMixin
from skinshortcuts.models.menu import Content
from skinshortcuts.providers.content import ResolvedShortcut


class _Picker(PickersMixin):
    """PickersMixin with no manager, for calling its content resolution directly."""

    def __init__(self) -> None:
        self.manager = None  # type: ignore[assignment]
        self.shortcuts_path = ""
        self.menu_id = ""


def _targets(content: Content, resolved: list[ResolvedShortcut]) -> list[str]:
    """Widget targets the picker gives content a stand-in provider resolves."""
    class _Provider:
        def __init__(self, *_a, **_k) -> None:
            pass

        def resolve(self, _content):
            return resolved

    with patch.object(pickers, "ContentProvider", _Provider):
        return [w.target for w in _Picker()._resolve_content_to_widgets(content)]


def test_nodes_library_keeps_each_entry_in_its_own_window():
    targets = _targets(
        Content(source="nodes", target="library"),
        [
            ResolvedShortcut(label="Videos", action="", browse_path="library://video/",
                             browse_window="videos"),
            ResolvedShortcut(label="Music", action="", browse_path="library://music/",
                             browse_window="music"),
        ],
    )
    assert targets == ["videos", "music"]


def test_library_query_window_comes_from_its_action():
    targets = _targets(
        Content(source="library", target="musicgenres"),
        [ResolvedShortcut(label="Rock",
                          action="ActivateWindow(Music,musicdb://genres/1/,return)")],
    )
    assert targets == ["music"], "musicgenres is not in the target map, the action knows"


def test_file_source_target():
    targets = _targets(
        Content(source="sources", target="files"),
        [ResolvedShortcut(label="Drive", action="ActivateWindow(files,D:/,return)",
                          browse_path="D:/", browse_window="files")],
    )
    assert targets == ["files"]


def test_unknown_target_falls_back_to_videos():
    targets = _targets(
        Content(source="playlists", target="vidoes"),
        [ResolvedShortcut(label="Typo", action="PlayMedia(x.xsp)")],
    )
    assert targets == ["videos"]


def test_library_albums_keep_their_type():
    class _Provider:
        def __init__(self, *_a, **_k) -> None:
            pass

        def resolve(self, _content):
            return [ResolvedShortcut(label="Kind of Blue", content_type="albums",
                                     action="ActivateWindow(Music,musicdb://albums/1/,return)")]

    with patch.object(pickers, "ContentProvider", _Provider):
        widgets = _Picker()._resolve_content_to_widgets(Content(source="library", target="albums"))

    assert widgets[0].type == "albums"
    assert widgets[0].target == "music"


def test_non_media_window_does_not_reach_the_target():
    """A window favourite can name any window, including a numeric id."""
    targets = _targets(
        Content(source="favourites"),
        [ResolvedShortcut(label="Weather", action="ActivateWindow(10025)")],
    )
    assert targets == ["videos"]
