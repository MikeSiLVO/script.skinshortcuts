"""A repeated name in any lookup-by-name config warns at load."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.loaders.background import load_backgrounds
from skinshortcuts.loaders.menu import load_menus
from skinshortcuts.loaders.views import load_views
from skinshortcuts.loaders.widget import load_widgets


@pytest.fixture
def sent(monkeypatch):
    captured = []
    monkeypatch.setattr("skinshortcuts.loaders.base.notify", lambda h, m, *_: captured.append(m))
    return captured


def _write(tmp_path: Path, name: str, body: str) -> Path:
    """Write a config file into the temp folder and return its path."""
    path = tmp_path / name
    path.write_text(body)
    return path


MENUS = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="a"><label>A</label><action>Noop</action></item>
    <item name="a"><label>Repeat</label><action>Noop</action></item>
  </menu>
  <submenu name="mainmenu">
    <item name="b"><label>B</label><action>Noop</action></item>
  </submenu>
</menus>
"""


def test_menu_and_item_duplicates(tmp_path: Path, sent):
    load_menus(_write(tmp_path, "menus.xml", MENUS))

    assert "item 'a' defined twice in menu 'mainmenu'" in sent
    assert "'mainmenu' defined twice" in sent


def test_submenu_shares_the_menu_namespace(tmp_path: Path, sent):
    xml = MENUS.replace('<item name="a"><label>Repeat</label><action>Noop</action></item>\n', "")
    load_menus(_write(tmp_path, "menus.xml", xml))

    assert sent == ["'mainmenu' defined twice"]


def test_duplicate_widget_name_nested_in_a_group(tmp_path: Path, sent):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<widgets>
  <widget name="recent" label="Recent Movies" type="movies"><path>videodb://a/</path></widget>
  <group name="tv" label="TV">
    <widget name="recent" label="Recent Episodes" type="episodes"><path>videodb://b/</path></widget>
  </group>
</widgets>
"""
    load_widgets(_write(tmp_path, "widgets.xml", xml))

    assert sent == ["'recent' defined twice"]


def test_duplicate_background_name(tmp_path: Path, sent):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
  <background name="fanart" label="Fanart" type="single"><path>a.jpg</path></background>
  <background name="fanart" label="Other" type="single"><path>b.jpg</path></background>
</backgrounds>
"""
    load_backgrounds(_write(tmp_path, "backgrounds.xml", xml))

    assert sent == ["'fanart' defined twice"]


def test_duplicate_view_id_and_content_name(tmp_path: Path, sent):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<views>
  <view id="50" label="List" />
  <view id="50" label="Poster" />
  <rules>
    <content name="movies" label="Movies" library="50">
      <visible>Container.Content(movies)</visible>
      <views>50</views>
    </content>
    <content name="movies" label="Films" library="50">
      <visible>Container.Content(movies)</visible>
      <views>50</views>
    </content>
  </rules>
</views>
"""
    load_views(_write(tmp_path, "views.xml", xml))

    assert sent == ["'50' defined twice", "content 'movies' defined twice"]


def test_unique_names_are_silent(tmp_path: Path, sent):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="a"><label>A</label><action>Noop</action></item>
    <item name="b"><label>B</label><action>Noop</action></item>
  </menu>
  <submenu name="settings">
    <item name="a"><label>A</label><action>Noop</action></item>
  </submenu>
</menus>
"""
    load_menus(_write(tmp_path, "menus.xml", xml))

    assert sent == []
