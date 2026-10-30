"""Browsing into a widget keeps its declared type and source."""

from __future__ import annotations

from unittest.mock import patch

from skinshortcuts.dialog import pickers
from skinshortcuts.dialog.pickers import PickersMixin
from skinshortcuts.models.menu import Content
from skinshortcuts.models.widget import Widget
from skinshortcuts.providers.content import ResolvedShortcut


class _FakeProvider:
    """Content provider stand-in resolving one TMDb Helper video add-on."""

    def __init__(self, *_a, **_k) -> None:
        pass

    def resolve(self, _content):
        return [ResolvedShortcut(label="TMDb Helper", action="", icon="t",
                                 browse_path="plugin://plugin.video.themoviedb.helper/",
                                 browse_window="videos")]


class _Picker(PickersMixin):
    """PickersMixin with no manager, a stub browse and a recorded type prompt."""

    def __init__(self) -> None:
        self.manager = None  # type: ignore[assignment]
        self.shortcuts_path = ""
        self.menu_id = ""
        self.prompted = False

    def _browse_directory(self, path, title="", icon=""):
        return (f"{path}titles/", "Titles", icon or "DefaultFolder.png")

    def _pick_widget_type(self, _addon_type):
        self.prompted = True
        return "videos"


def _declared(**kw) -> Widget:
    """Browsable movies widget with given extra fields."""
    return Widget(name="w", label="W", path="videodb://movies/", browse=True, **kw)


def test_declared_type_skips_prompt():
    picker = _Picker()
    result = picker._browse_widget_path(_declared(type="sets", target="videos"))
    assert result is not None
    assert not picker.prompted, "declared type must not be second-guessed"
    assert result.type == "sets"


def test_undeclared_type_still_prompts():
    picker = _Picker()
    result = picker._browse_widget_path(_declared(target="videos"))
    assert result is not None
    assert picker.prompted
    assert result.type == "videos"


def test_source_carried_not_hardcoded():
    picker = _Picker()
    result = picker._browse_widget_path(
        _declared(type="sets", target="videos", source="library")
    )
    assert result is not None
    assert result.source == "library"

    bare = picker._browse_widget_path(_declared(type="sets", target="videos"))
    assert bare is not None
    assert bare.source == "", "a widget that declared no source must not gain one"


def test_content_resolved_addon_still_prompts():
    """Addons carry no type of their own."""
    picker = _Picker()
    with patch.object(pickers, "ContentProvider", _FakeProvider):
        widgets = picker._resolve_content_to_widgets(Content(source="addons", target="video"))

    assert widgets[0].type == "", "the content target is not a widget type"

    result = picker._browse_widget_path(widgets[0])
    assert result is not None
    assert picker.prompted
    assert result.type == "videos"


class _RealTypePicker(_Picker):
    """Stand-in picker running the real widget type prompt."""

    _pick_widget_type = PickersMixin._pick_widget_type


def test_picture_and_game_targets_map_to_their_window():
    picker = _Picker()
    assert picker._map_target_to_window("image") == "pictures"
    assert picker._map_target_to_window("game") == "games"
    assert picker._map_target_to_window("games") == "games"


def test_single_type_targets_are_not_asked_about():
    picker = _RealTypePicker()
    result = picker._browse_widget_path(_declared(target="games"))
    assert result is not None
    assert result.type == "games"
    assert result.target == "games"


def test_launcher_addons_are_not_widget_content():
    picker = _Picker()

    class _MixedProvider(_FakeProvider):
        def resolve(self, _content):
            return [
                ResolvedShortcut(label="Trakt", action="RunAddon(script.trakt)", icon="t"),
                ResolvedShortcut(label="TMDb Helper", action="", icon="t",
                                 browse_path="plugin://plugin.video.themoviedb.helper/",
                                 browse_window="videos"),
            ]

    with patch.object(pickers, "ContentProvider", _MixedProvider):
        widgets = picker._resolve_content_to_widgets(
            Content(source="addons", target="executable")
        )

    assert [w.label for w in widgets] == ["TMDb Helper"]


def test_content_resolved_playlist_keeps_its_type():
    """Playlists report a real content type, which must survive resolution."""
    picker = _Picker()

    class _PlaylistProvider(_FakeProvider):
        def resolve(self, _content):
            return [ResolvedShortcut(label="Recent", action="", icon="p",
                                     content_type="movies")]

    with patch.object(pickers, "ContentProvider", _PlaylistProvider):
        widgets = picker._resolve_content_to_widgets(Content(source="playlists", target="video"))

    assert widgets[0].type == "movies"
