"""Folder rows in a picker carry name/type/count, and a path only when real."""

from __future__ import annotations

from skinshortcuts.dialog.pickers import (
    PLACEHOLDER_PREFIX,
    _content_folder_path,
    stamp_picker_props,
)
from skinshortcuts.models.background import Background, BackgroundGroup
from skinshortcuts.models.menu import Content, Shortcut, ShortcutGroup
from skinshortcuts.models.widget import Widget, WidgetGroup


class _FakeListItem:
    """ListItem stand-in keeping properties readable."""

    def __init__(self) -> None:
        self.props: dict[str, str] = {}

    def setProperty(self, key: str, value: str) -> None:  # noqa: N802
        self.props[key] = value


def _stamp(item, item_props: dict[str, str] | None = None, resolver=None) -> dict[str, str]:
    """Stamp picker properties on a stand-in ListItem and return them."""
    listitem = _FakeListItem()
    stamp_picker_props(listitem, item, item_props, resolver)
    return listitem.props


def test_plain_group_has_no_path():
    group = WidgetGroup(
        name="program-addons",
        label="Programs",
        items=[Widget(name="a", label="A", path="plugin://a/")],
    )

    props = _stamp(group)

    assert props["name"] == "program-addons"
    assert props["type"] == "group"
    assert props["path"] == ""
    assert props["count"] == "1"


def test_content_folder_carries_real_path():
    group = ShortcutGroup(
        name="folder-Video add-ons",
        label="Video add-ons",
        path="addons://sources/video/",
        items=[Shortcut(name="tmdb", label="TMDb Helper")],
    )

    props = _stamp(group)

    assert props["path"] == "addons://sources/video/"
    assert props["type"] == "group"


def test_count_excludes_placeholder():
    group = WidgetGroup(
        name="folder-Video add-ons",
        label="Video add-ons",
        items=[
            Widget(name=f"{PLACEHOLDER_PREFIX}addons-video", label="Create here", path="addons://"),
            Widget(name="a", label="A", path="plugin://a/"),
            Widget(name="b", label="B", path="plugin://b/"),
        ],
    )

    assert _stamp(group)["count"] == "2"


def test_empty_group_counts_zero():
    assert _stamp(WidgetGroup(name="empty", label="Empty"))["count"] == "0"


def test_bare_content_needs_a_resolver():
    group = ShortcutGroup(
        name="program-addons",
        label="Programs",
        items=[
            Content(source="addons", target="programs"),
            Shortcut(name="apps", label="Apps"),
        ],
    )

    assert _stamp(group)["count"] == ""


def test_bare_content_counts_the_rows_it_expands_to():
    group = ShortcutGroup(
        name="program-addons",
        label="Programs",
        items=[
            Content(source="addons", target="programs"),
            Shortcut(name="apps", label="Apps"),
        ],
    )

    def resolver(_content):
        return [Shortcut(name=f"a{i}", label=f"A{i}") for i in range(4)]

    assert _stamp(group, resolver=resolver)["count"] == "5"


def test_folder_content_counts_one_row_each():
    group = ShortcutGroup(
        name="addons",
        label="Add-ons",
        items=[
            ShortcutGroup(name="program-addons", label="Programs"),
            Content(source="addons", target="videos", folder="1037"),
            Content(source="addons", target="music", folder="1038"),
            Content(source="addons", target="pictures", folder="1039"),
            Shortcut(name="game-addons", label="Games"),
        ],
    )

    def resolver(_content):
        return [Shortcut(name="a", label="A"), Shortcut(name="b", label="B")]

    assert _stamp(group, resolver=resolver)["count"] == "5"


def test_empty_folder_content_is_not_counted():
    group = ShortcutGroup(
        name="playlists",
        label="Playlists",
        items=[
            Content(source="playlists", target="videos", folder="20012"),
            Content(source="playlists", target="music", folder="20011"),
            Content(source="playlists", folder="31514", path="special://skin/extras/playlists/"),
        ],
    )

    def resolver(content):
        return [] if content.target else [Shortcut(name="a", label="A")]

    assert _stamp(group, resolver=resolver)["count"] == "1"


def test_empty_addons_folder_counts_its_placeholder_row():
    group = ShortcutGroup(
        name="addons",
        label="Add-ons",
        items=[Content(source="addons", target="videos", folder="1037")],
    )

    assert _stamp(group, resolver=lambda _content: [])["count"] == "1"


def test_count_skips_children_filtered_out():
    group = ShortcutGroup(
        name="mixed",
        label="Mixed",
        items=[
            Shortcut(name="shown", label="Shown"),
            Shortcut(name="hidden", label="Hidden", condition="widgetStyle=Panel"),
        ],
    )

    assert _stamp(group, {"widgetStyle": "Wide"})["count"] == "1"
    assert _stamp(group, {"widgetStyle": "Panel"})["count"] == "2"


def test_flat_child_group_counts_its_rows():
    group = ShortcutGroup(
        name="outer",
        label="Outer",
        items=[
            Shortcut(name="a", label="A"),
            ShortcutGroup(
                name="inner",
                label="Inner",
                flat=True,
                items=[Shortcut(name="b", label="B"), Shortcut(name="c", label="C")],
            ),
        ],
    )

    assert _stamp(group)["count"] == "3"


def test_background_group_stamps_like_other_groups():
    group = BackgroundGroup(
        name="fanart",
        label="Fanart",
        items=[Background(name="a", label="A"), Background(name="b", label="B")],
    )

    props = _stamp(group)

    assert props["name"] == "fanart"
    assert props["type"] == "group"
    assert props["count"] == "2"
    assert props["path"] == ""


def test_content_folder_path_only_for_addons():
    assert _content_folder_path(Content(source="addons", target="videos")) == "addons://sources/video/"
    assert _content_folder_path(Content(source="addons", target="music")) == "addons://sources/audio/"
    assert _content_folder_path(Content(source="playlists", target="video")) == ""
    assert _content_folder_path(Content(source="addons", target="bogus")) == ""


def test_addons_content_defaults_to_video():
    assert _content_folder_path(Content(source="addons")) == "addons://sources/video/"

