"""The addons placeholder commits with its content section's label, not the placeholder string."""

from __future__ import annotations

from skinshortcuts.dialog.pickers import _browse_placeholder_for_content
from skinshortcuts.models.menu import Content
from skinshortcuts.models.widget import Widget


def test_shortcut_placeholder_uses_content_label():
    shortcut = _browse_placeholder_for_content(
        Content(source="addons", target="video", label="Video Add-ons")
    )
    assert shortcut is not None
    assert shortcut.label == "Video Add-ons"
    assert shortcut.type == ""
    assert shortcut.actions[0].action == "ActivateWindow(videos,addons://sources/video/,return)"


def test_widget_placeholder_uses_content_label():
    widget = _browse_placeholder_for_content(
        Content(source="addons", target="video", label="Video Add-ons"), as_widget=True
    )
    assert isinstance(widget, Widget)
    assert widget.label == "Video Add-ons"


def test_placeholder_uses_parent_label_when_content_has_none():
    shortcut = _browse_placeholder_for_content(
        Content(source="addons", target="videos", label=""), parent_label="Video Add-ons"
    )
    assert shortcut is not None
    assert shortcut.label == "Video Add-ons"


def test_non_addons_content_has_no_placeholder():
    assert _browse_placeholder_for_content(
        Content(source="playlists", target="video", label="X")
    ) is None
