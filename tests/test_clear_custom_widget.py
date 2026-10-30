"""RunScript type=clear with property= clears the same widget keys the dialog clears."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from skinshortcuts import entry, userdata
from skinshortcuts.manager import MenuManager

MENUS_XML = """<menus>
  <menu name="mainmenu">
    <item name="movies">
      <label>Movies</label>
      <action>ActivateWindow(Videos,videodb://movies/titles/,return)</action>
    </item>
  </menu>
</menus>"""

PROPERTIES_XML = """<properties>
  <property name="widget" type="widget" />
  <property name="widgetLimit" />
  <property name="widgetSortby" />
</properties>"""

PICKED = {
    "widget": "recent",
    "widgetLabel": "Recent",
    "widgetPath": "videodb://recentlyaddedmovies/",
    "widgetType": "movies",
    "widgetTarget": "videos",
    "widgetSource": "library",
    "widgetLimit": "25",
    "widgetSortby": "random",
}


@pytest.fixture
def skin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()
    (shortcuts / "menus.xml").write_text(MENUS_XML, encoding="utf-8")
    (shortcuts / "properties.xml").write_text(PROPERTIES_XML, encoding="utf-8")
    stored = tmp_path / "userdata.json"
    monkeypatch.setattr(userdata, "get_userdata_path", lambda: str(stored))
    monkeypatch.setattr(entry, "build_includes", lambda *a, **k: True)
    return shortcuts, stored


def stored_keys(stored: Path) -> set[str]:
    """Property keys saved on mainmenu's items."""
    data = json.loads(stored.read_text(encoding="utf-8"))
    items = data.get("menus", {}).get("mainmenu", {}).get("items", [])
    return {key for item in items for key in item.get("properties", {})}


def test_clear_leaves_no_widget_keys(skin: tuple[Path, Path]) -> None:
    shortcuts, stored = skin
    manager = MenuManager(shortcuts)
    for key, value in PICKED.items():
        manager.set_custom_property("mainmenu", "movies", key, value)
    manager.save()
    assert stored_keys(stored) >= set(PICKED)

    entry.clear_custom_widget("mainmenu", "movies", "", "widget", str(shortcuts))
    assert not {key for key in stored_keys(stored) if key.lower().startswith("widget")}
