"""Userdata round-trips property clears and never saves derived widget data."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.manager import MenuManager

MENUS = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies" widget="moviewidget">
      <label>Movies</label>
      <action>ActivateWindow(Videos)</action>
    </item>
    <item name="tvshows" widget="moviewidget">
      <label>TV</label>
      <action>ActivateWindow(Videos)</action>
    </item>
  </menu>
</menus>
"""

WIDGETS = """<?xml version="1.0" encoding="UTF-8"?>
<widgets>
  <widget name="moviewidget" label="Recent Movies">
    <path>videodb://movies/recent/</path>
    <target>videos</target>
  </widget>
  <widget name="tvwidget" label="Recent TV">
    <path>videodb://tvshows/recent/</path>
    <target>videos</target>
  </widget>
</widgets>
"""


def _setup(tmp_path: Path):
    """Write the test menus and widgets into a shortcuts folder; return it and a userdata path."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS)
    (skin / "widgets.xml").write_text(WIDGETS)
    return skin, tmp_path / "userdata.json"


def _item(manager, menu, name):
    """Working item of a given name in a menu."""
    return next(i for i in manager.working[menu].items if i.name == name)


def test_cleared_widget_stays_cleared(tmp_path: Path):
    skin, ud = _setup(tmp_path)
    m = MenuManager(skin, userdata_path=str(ud))
    assert _item(m, "mainmenu", "movies").properties.get("widget") == "moviewidget"

    for key in ("widget", "widgetPath", "widgetTarget", "widgetLabel"):
        m.set_custom_property("mainmenu", "movies", key, None)
    m._changed = True
    m.save()

    m2 = MenuManager(skin, userdata_path=str(ud))
    assert not _item(m2, "mainmenu", "movies").properties.get("widget")
    assert not _item(m2, "mainmenu", "movies").properties.get("widgetPath")


def test_untouched_item_saves_no_widget_data(tmp_path: Path):
    skin, ud = _setup(tmp_path)
    m = MenuManager(skin, userdata_path=str(ud))
    m.set_label("mainmenu", "tvshows", "TV Shows")
    m._changed = True
    m.save()

    text = ud.read_text()
    assert "widgetPath" not in text
    assert "widgetLabel" not in text


def test_skinner_path_change_reaches_saved_item(tmp_path: Path):
    skin, ud = _setup(tmp_path)
    m = MenuManager(skin, userdata_path=str(ud))
    m.set_label("mainmenu", "movies", "My Movies")  # touch it so it's in userdata
    m._changed = True
    m.save()

    (skin / "widgets.xml").write_text(
        WIDGETS.replace("videodb://movies/recent/", "videodb://movies/new/")
    )
    m2 = MenuManager(skin, userdata_path=str(ud))
    assert _item(m2, "mainmenu", "movies").properties["widgetPath"] == "videodb://movies/new/"
    assert _item(m2, "mainmenu", "movies").label == "My Movies"


def test_reassigned_widget_saves_its_values(tmp_path: Path):
    skin, ud = _setup(tmp_path)
    m = MenuManager(skin, userdata_path=str(ud))
    m.set_custom_property("mainmenu", "movies", "widget", "tvwidget")
    m.set_custom_property("mainmenu", "movies", "widgetPath", "videodb://tvshows/recent/")
    m.set_custom_property("mainmenu", "movies", "widgetLabel", "Recent TV")
    m.set_custom_property("mainmenu", "movies", "widgetTarget", "videos")
    m._changed = True
    m.save()

    text = ud.read_text()
    assert '"widget": "tvwidget"' in text
    assert "videodb://tvshows/recent/" in text

    m2 = MenuManager(skin, userdata_path=str(ud))
    it = _item(m2, "mainmenu", "movies")
    assert it.properties["widget"] == "tvwidget"
    assert it.properties["widgetPath"] == "videodb://tvshows/recent/"


def test_renamed_label_survives_and_path_still_resolves(tmp_path: Path):
    skin, ud = _setup(tmp_path)
    m = MenuManager(skin, userdata_path=str(ud))
    m.set_custom_property("mainmenu", "movies", "widgetLabel", "Fresh Films")
    m._changed = True
    m.save()

    text = ud.read_text()
    assert "Fresh Films" in text
    assert "widgetPath" not in text

    m2 = MenuManager(skin, userdata_path=str(ud))
    it = _item(m2, "mainmenu", "movies")
    assert it.properties["widgetLabel"] == "Fresh Films"
    assert it.properties["widgetPath"] == "videodb://movies/recent/"
