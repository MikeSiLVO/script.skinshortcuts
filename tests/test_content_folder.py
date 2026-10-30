"""Content folder="" wraps into one navigable folder, same as a <group>."""
from __future__ import annotations

from unittest.mock import patch

from skinshortcuts.dialog import pickers
from skinshortcuts.dialog.pickers import PickersMixin
from skinshortcuts.models.menu import Content, Shortcut, ShortcutGroup
from skinshortcuts.providers.content import ResolvedShortcut


class _FakeProvider:
    """Content provider stand-in resolving one pluginsource video add-on."""

    def __init__(self, *_a, **_k) -> None:
        pass

    def resolve(self, _content):
        return [
            ResolvedShortcut(label="TMDb Helper", action="", icon="t",
                             browse_path="plugin://plugin.video.themoviedb.helper/",
                             browse_window="videos"),
        ]


class _Picker(PickersMixin):
    """PickersMixin with no manager, for calling its filters directly."""

    def __init__(self) -> None:
        self.manager = None  # type: ignore[assignment]
        self.shortcuts_path = ""
        self.menu_id = ""


def _folder_group(label, items, icon, path):
    """Folder group the picker wraps folder content in."""
    return ShortcutGroup(name=f"folder-{label}", label=label,
                         icon=icon or "DefaultFolder.png", items=items, path=path)


def test_addons_folder_wraps_placeholder_and_takes_icon():
    picker = _Picker()
    content = Content(source="addons", target="video",
                      folder="Video Add-ons", icon="special://skin/vid.png")
    with patch.object(pickers, "ContentProvider", _FakeProvider):
        items = picker._filter_picker_items(
            [content], {}, leaf_types=(Shortcut,), group_types=(),
            content_resolver=picker._resolve_content_to_shortcuts,
            create_folder_group=_folder_group,
        )

    assert len(items) == 1, "folder should be the single top-level item"
    folder = items[0]
    assert isinstance(folder, ShortcutGroup)
    assert folder.icon == "special://skin/vid.png"

    inside = {it.name: it for it in folder.items}
    assert "content-placeholder-addons-video" in inside, "placeholder belongs inside"
    assert "dynamic-addons-0" in inside

    placeholder = inside["content-placeholder-addons-video"]
    assert placeholder.icon == "special://skin/vid.png", "the picker row icon is committed"
    assert placeholder.label == "Video Add-ons", "folder names the committed menu item"


def _placeholder(content: Content, **parent):
    """The placeholder the shortcut picker builds for a content element."""
    picker = _Picker()
    with patch.object(pickers, "ContentProvider", _FakeProvider):
        items = picker._filter_picker_items(
            [content], {}, leaf_types=(Shortcut,), group_types=(),
            content_resolver=picker._resolve_content_to_shortcuts,
            create_folder_group=_folder_group, **parent,
        )
    return next(it for it in items if it.name.startswith("content-placeholder-"))


def test_placeholder_falls_back_to_its_group():
    """A bare <content> inside a group commits that group's label and icon."""
    got = _placeholder(
        Content(source="addons", target="video"),
        parent_label="$LOCALIZE[24001]", parent_icon="DefaultAddons.png",
    )

    assert got.label == "$LOCALIZE[24001]", "raw, so a language switch still moves it"
    assert got.icon == "DefaultAddons.png"


def test_content_attributes_beat_the_group():
    got = _placeholder(
        Content(source="addons", target="video", label="Mine", icon="mine.png"),
        parent_label="Group", parent_icon="group.png",
    )

    assert (got.label, got.icon) == ("Mine", "mine.png")


def test_addons_without_folder_keeps_flat_layout():
    picker = _Picker()
    with patch.object(pickers, "ContentProvider", _FakeProvider):
        items = picker._filter_picker_items(
            [Content(source="addons", target="video")], {},
            leaf_types=(Shortcut,), group_types=(),
            content_resolver=picker._resolve_content_to_shortcuts,
            create_folder_group=_folder_group,
        )

    names = [it.name for it in items]
    assert names == ["content-placeholder-addons-video", "dynamic-addons-0"]
