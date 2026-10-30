"""Tests for widgets.xml parsing, especially top-level element acceptance."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.loaders.widget import load_widgets
from skinshortcuts.models.menu import Content
from skinshortcuts.models.widget import Widget, WidgetGroup


def _write(tmp: Path, body: str) -> Path:
    """Write a widgets.xml around given XML and return its path."""
    path = tmp / "widgets.xml"
    path.write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<widgets>\n{body}\n</widgets>\n')
    return path


def test_root_widget_appears_in_widgets_and_groupings(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <widget name="favs" label="Favs" type="files">
          <path>favourites://</path>
        </widget>
        """,
    )

    config = load_widgets(path)

    assert [w.name for w in config.widgets] == ["favs"]
    assert len(config.groupings) == 1
    assert isinstance(config.groupings[0], Widget)


def test_root_group_in_groupings_only(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <group name="movies" label="Movies">
          <widget name="recent" label="Recent" type="movies">
            <path>videodb://recentlyaddedmovies/</path>
          </widget>
        </group>
        """,
    )

    config = load_widgets(path)

    assert config.widgets == []
    assert len(config.groupings) == 1
    group = config.groupings[0]
    assert isinstance(group, WidgetGroup)
    assert group.name == "movies"
    assert len(group.items) == 1


def test_root_content_appears_in_groupings(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <content source="playlists" target="videos" folder="Video Playlists" />
        """,
    )

    config = load_widgets(path)

    assert config.widgets == []
    assert len(config.groupings) == 1
    content = config.groupings[0]
    assert isinstance(content, Content)
    assert content.source == "playlists"
    assert content.folder == "Video Playlists"


def test_mixed_root_children_preserved_in_order(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <widget name="favs" label="Favs" type="files">
          <path>favourites://</path>
        </widget>
        <group name="movies" label="Movies" />
        <content source="addons" target="videos" />
        """,
    )

    config = load_widgets(path)

    assert [w.name for w in config.widgets] == ["favs"]
    types = [type(item).__name__ for item in config.groupings]
    assert types == ["Widget", "WidgetGroup", "Content"]


def test_unknown_root_tags_ignored(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <bogus />
        <widget name="favs" label="Favs" type="files">
          <path>favourites://</path>
        </widget>
        """,
    )

    config = load_widgets(path)

    assert [w.name for w in config.widgets] == ["favs"]
    assert len(config.groupings) == 1


def test_flat_group_parses_without_label(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <group name="home-widgets" flat="true" condition="widgetSlot=home">
          <widget name="recent" label="Recent" type="movies">
            <path>videodb://recentlyaddedmovies/</path>
          </widget>
        </group>
        """,
    )

    config = load_widgets(path)

    assert len(config.groupings) == 1
    group = config.groupings[0]
    assert isinstance(group, WidgetGroup)
    assert group.flat is True
    assert group.label == ""
    assert group.condition == "widgetSlot=home"
    assert len(group.items) == 1


def test_flat_group_with_label_ignored_silently(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <group name="home-widgets" label="Should Be Ignored" flat="true">
          <widget name="recent" label="Recent" type="movies">
            <path>videodb://recentlyaddedmovies/</path>
          </widget>
        </group>
        """,
    )

    config = load_widgets(path)

    assert len(config.groupings) == 1
    group = config.groupings[0]
    assert isinstance(group, WidgetGroup)
    assert group.flat is True
    # label kept on the model but unused at render time
    assert group.label == "Should Be Ignored"


def test_non_flat_group_missing_label_dropped(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <group name="movies">
          <widget name="recent" label="Recent" type="movies">
            <path>videodb://recentlyaddedmovies/</path>
          </widget>
        </group>
        <widget name="favs" label="Favs" type="files">
          <path>favourites://</path>
        </widget>
        """,
    )

    config = load_widgets(path)

    assert [type(item).__name__ for item in config.groupings] == ["Widget"]
    assert [w.name for w in config.widgets] == ["favs"]


def test_target_aliases_normalize(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <widget name="pics" label="Pics" target="image">
          <path>addons://sources/image/</path>
        </widget>
        """,
    )

    assert load_widgets(path).widgets[0].target == "pictures"


def test_unmapped_target_kept_as_written(tmp_path: Path):
    """The map holds media contexts, not every Kodi window."""
    path = _write(
        tmp_path,
        """
        <widget name="recs" label="Recordings" target="tvrecordings">
          <path>pvr://recordings/tv/active/</path>
        </widget>
        """,
    )

    assert load_widgets(path).widgets[0].target == "tvrecordings"


def test_group_missing_name_dropped(tmp_path: Path):
    path = _write(
        tmp_path,
        """
        <group label="Movies" flat="true">
          <widget name="recent" label="Recent" type="movies">
            <path>videodb://recentlyaddedmovies/</path>
          </widget>
        </group>
        """,
    )

    config = load_widgets(path)

    assert config.groupings == []
