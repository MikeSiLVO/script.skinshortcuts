"""A widget or background button's heading heads its picker; without one the fixed heading shows."""

from __future__ import annotations

from pathlib import Path

import pytest
from harness import harness_fixture, open_root, write_skin  # noqa: F401

MENUS = """<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>Noop</action></item>
  </menu>
</menus>"""

PROPERTIES = """<properties>
  <buttons>
    <button id="309" property="widget" type="widget" heading="Choose a widget" />
    <button id="310" property="background" type="background" heading="Choose a background" />
    <button id="311" property="widget" type="widget" />
    <button id="312" property="background" type="background" />
    <button id="313" property="widget" type="widget" title="Old widget heading" />
  </buttons>
</properties>"""

WIDGETS = """<widgets>
  <widget name="recent" label="Recent" type="movies">
    <path>videodb://recentlyaddedmovies/</path>
  </widget>
</widgets>"""

BACKGROUNDS = """<backgrounds>
  <background name="folder" label="Folder" type="browse" />
</backgrounds>"""


def _heading(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, button_id: int) -> str:
    """Heading of the picker a property button opens."""
    monkeypatch.setattr("skinshortcuts.dialog.pickers.LANGUAGE", lambda string_id: f"#{string_id}")
    skin = write_skin(
        tmp_path, MENUS, properties=PROPERTIES, widgets=WIDGETS, backgrounds=BACKGROUNDS
    )
    dialog = open_root(skin, tmp_path)
    seen: list[str] = []
    dialog._pick_from_hierarchy = lambda *_args, **kwargs: seen.append(kwargs["title"])
    dialog._handle_property_button(button_id)
    return seen[0]


@pytest.mark.parametrize(
    ("button_id", "heading"),
    [
        (309, "Choose a widget"),
        (310, "Choose a background"),
        (311, "#32044"),
        (312, "#32045"),
        (313, "Old widget heading"),
    ],
    ids=["widget", "background", "widget-default", "background-default", "old-title"],
)
def test_picker_heading(
    harness, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, button_id: int, heading: str
) -> None:
    """The heading heads the picker, else the fixed "Select widget" or "Select background"."""
    assert _heading(tmp_path, monkeypatch, button_id) == heading
