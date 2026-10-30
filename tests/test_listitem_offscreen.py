"""The management list builds its rows offscreen and replaces a row rather than writing it."""

from __future__ import annotations

from pathlib import Path

import pytest
import xbmcgui
from harness import FakeListItem, harness_fixture, open_root, write_skin  # noqa: F401

from skinshortcuts.dialog.base import _create_listitem, _ListItemValues

MENUS = """<menus>
  <menu name="mainmenu">
    <item name="music" icon="DefaultMusic.png"><label>Music</label><action>Noop</action></item>
    <item name="pictures"><label>Pictures</label><action>Noop</action></item>
    <item name="movies"><label>Movies</label><action>Noop</action></item>
  </menu>
</menus>"""


class RecordingListItem(FakeListItem):
    """FakeListItem that records each setter call."""

    def __init__(self, label: str = "", label2: str = "", offscreen: bool = False) -> None:
        super().__init__(label, label2, offscreen)
        self.calls: list[tuple] = []

    def setLabel(self, label: str) -> None:  # noqa: N802
        self.calls.append(("label", label))
        super().setLabel(label)

    def setLabel2(self, label: str) -> None:  # noqa: N802
        self.calls.append(("label2", label))
        super().setLabel2(label)

    def setProperty(self, key: str, value: str) -> None:  # noqa: N802
        self.calls.append(("property", key, value))
        super().setProperty(key, value)

    def setArt(self, art: dict[str, str]) -> None:  # noqa: N802
        self.calls.append(("art", art))
        super().setArt(art)


@pytest.fixture(name="recording")
def recording_fixture(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(xbmcgui, "ListItem", RecordingListItem)


def test_create_is_offscreen_and_skips_empty_properties(recording) -> None:
    values = _ListItemValues("Music", "Noop", "icon.png", {"name": "music", "widget": ""})
    listitem = _create_listitem(values)
    assert listitem.offscreen
    assert (listitem.label, listitem.label2) == ("Music", "Noop")
    assert listitem.calls == [
        ("art", {"thumb": "icon.png", "icon": "icon.png"}),
        ("property", "name", "music"),
    ]


def test_every_row_and_the_edited_item_are_offscreen(harness, tmp_path: Path) -> None:
    dialog = open_root(write_skin(tmp_path, MENUS), tmp_path)
    assert all(row.offscreen for row in dialog.controls[211].rows)
    dialog.dialog_mode = "widget"
    dialog._populate_subdialog_list(0)
    assert all(row.offscreen for row in dialog.controls[212].rows)


def test_refresh_replaces_rows_and_writes_none_in_the_list(
    harness, monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(xbmcgui, "ListItem", RecordingListItem)
    dialog = open_root(write_skin(tmp_path, MENUS), tmp_path)
    before = list(dialog.controls[211].rows)
    for row in before:
        row.calls.clear()
    dialog._set_item_property(dialog.items[0], "foo", "bar")
    dialog._refresh_selected_item()
    after = dialog.controls[211].rows
    assert [row.calls for row in before] == [[], [], []]
    assert not {id(row) for row in after} & {id(row) for row in before}
    assert after[0].getProperty("foo") == "bar"


def test_edited_item_list_never_empties_on_refresh(
    harness, monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(xbmcgui, "ListItem", RecordingListItem)
    dialog = open_root(write_skin(tmp_path, MENUS), tmp_path)
    dialog.dialog_mode = "widget"
    dialog._selected_index = 0
    dialog._populate_subdialog_list(0)
    edited = dialog.controls[212]
    old = edited.rows[0]
    old.calls.clear()
    edited.sizes.clear()
    dialog._set_item_property(dialog.items[0], "foo", "bar")
    dialog._refresh_selected_item()
    assert 0 not in edited.sizes
    assert old.calls == []
    assert len(edited.rows) == 1 and edited.rows[0] is not old
    assert edited.rows[0].getProperty("foo") == "bar"


def test_move_rebuilds_the_rows_in_the_new_order(harness, tmp_path: Path) -> None:
    dialog = open_root(write_skin(tmp_path, MENUS), tmp_path)
    dialog._move_item(1)
    rows = dialog.controls[211].rows
    assert [row.getProperty("name") for row in rows] == ["pictures", "music", "movies"]


def test_cleared_property_leaves_the_selected_row(harness, tmp_path: Path) -> None:
    dialog = open_root(write_skin(tmp_path, MENUS), tmp_path)
    item = dialog.items[0]
    dialog._set_item_property(item, "foo", "bar")
    dialog._refresh_selected_item()
    assert dialog.controls[211].rows[0].getProperty("foo") == "bar"
    dialog._set_item_property(item, "foo", None)
    dialog._refresh_selected_item()
    assert dialog.controls[211].rows[0].getProperty("foo") == ""
