"""An item's submenuPath holds the first widget path of its per-item widgets submenu."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig

MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies" submenu="movies"><label>Movies</label><action>Noop</action></item>
    <item name="music" submenu="music"><label>Music</label><action>Noop</action></item>
    <item name="settings"><label>Settings</label><action>ActivateWindow(Settings)</action></item>
    <item name="empties" submenu="empties"><label>Empties</label><action>Noop</action></item>
  </menu>

  <dialogs>
    <subdialog buttonID="406" menu="{item}.widgets" />
  </dialogs>

  <!-- No type="widgets": runtime-added widget submenus carry no type, detection must
       still recognize them by their widgetPath content. -->
  <submenu name="movies.widgets">
    <item name="w1">
      <label>W1</label>
      <property name="widgetPath">videodb://movies/recent/</property>
    </item>
    <item name="w2">
      <label>W2</label>
      <property name="widgetPath">videodb://movies/random/</property>
    </item>
  </submenu>

  <submenu name="music.widgets" type="widgets">
    <item name="m1"><label>M1</label><property name="widgetPath">musicdb://recent/</property></item>
    <item name="m2"><label>M2</label><property name="widgetPath">musicdb://random/</property></item>
  </submenu>

  <submenu name="empties.widgets" type="widgets">
    <item name="d1">
      <label>D1</label>
      <disabled>true</disabled>
      <property name="widgetPath">videodb://x/</property>
    </item>
    <item name="nopath"><label>NoPath</label></item>
  </submenu>
</menus>
"""


CW_MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="cw">
      <label>CustomWidgetItem</label>
      <action>Noop</action>
      <property name="customWidget">custom1</property>
    </item>
  </menu>

  <dialogs>
    <subdialog buttonID="800" menu="{item}.customwidget" />
  </dialogs>

  <submenu name="cw.customwidget" type="widgets">
    <item name="c1"><label>C1</label><property name="widgetPath">plugin://custom/</property></item>
  </submenu>
</menus>
"""


PROPERTIES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <property name="submenuPath" templateonly="true" />
</properties>
"""


GLOBAL_OPTIN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <submenuPath>all</submenuPath>
  <menu name="mainmenu">
    <item name="movies" submenu="movies"><label>Movies</label><action>Noop</action></item>
  </menu>
  <dialogs>
    <subdialog buttonID="406" menu="{item}.widgets" />
  </dialogs>
  <submenu name="movies.widgets">
    <item name="w1">
      <label>W1</label>
      <property name="widgetPath">videodb://movies/recent/</property>
    </item>
    <item name="w2">
      <label>W2</label>
      <property name="widgetPath">videodb://movies/random/</property>
    </item>
  </submenu>
</menus>
"""


PERMENU_OPTIN_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu" submenuPath="all">
    <item name="movies" submenu="movies"><label>Movies</label><action>Noop</action></item>
  </menu>
  <dialogs>
    <subdialog buttonID="406" menu="{item}.widgets" />
  </dialogs>
  <submenu name="movies.widgets">
    <item name="w1">
      <label>W1</label>
      <property name="widgetPath">videodb://movies/recent/</property>
    </item>
    <item name="w2">
      <label>W2</label>
      <property name="widgetPath">videodb://movies/random/</property>
    </item>
  </submenu>
</menus>
"""


def _build(tmp_path: Path, menus: str, properties: str | None = None):
    """Build includes from a menus.xml and an optional properties.xml."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(menus)
    if properties is not None:
        (skin / "properties.xml").write_text(properties)
    config = SkinConfig.load(skin, load_user=False)
    return IncludesBuilder(
        config.menus,
        templates=config.templates,
        property_schema=config.property_schema,
        subdialogs=config.subdialogs,
        submenu_path_all=config.submenu_path_all,
    ).build()


def _item_props(root, include_name: str, item_name: str) -> dict[str, str]:
    """Properties of one item in one include, empty when absent."""
    for inc in root.findall("include"):
        if inc.get("name") != include_name:
            continue
        for item in inc.findall("item"):
            props = {p.get("name"): (p.text or "") for p in item.findall("property")}
            if props.get("name") == item_name:
                return props
    return {}


def test_scalar_submenu_path_always_emitted(tmp_path: Path):
    root = _build(tmp_path, MENUS_XML)
    props = _item_props(root, "skinshortcuts-mainmenu", "movies")
    assert props.get("submenuPath") == "videodb://movies/recent/"
    assert "submenuPath.2" not in props


def test_no_tail_without_optin(tmp_path: Path):
    root = _build(tmp_path, MENUS_XML)
    props = _item_props(root, "skinshortcuts-mainmenu", "music")
    assert props.get("submenuPath") == "musicdb://recent/"
    assert "submenuPath.2" not in props


def test_no_widgets_submenu_no_property(tmp_path: Path):
    root = _build(tmp_path, MENUS_XML)
    props = _item_props(root, "skinshortcuts-mainmenu", "settings")
    assert "submenuPath" not in props


def test_disabled_and_pathless_widgets_skipped(tmp_path: Path):
    root = _build(tmp_path, MENUS_XML)
    props = _item_props(root, "skinshortcuts-mainmenu", "empties")
    assert "submenuPath" not in props


def test_custom_widget_reference_excluded(tmp_path: Path):
    root = _build(tmp_path, CW_MENUS_XML)
    props = _item_props(root, "skinshortcuts-mainmenu", "cw")
    assert "submenuPath" not in props


def test_templateonly_suppresses_submenu_path(tmp_path: Path):
    root = _build(tmp_path, MENUS_XML, properties=PROPERTIES_XML)
    props = _item_props(root, "skinshortcuts-mainmenu", "movies")
    assert "submenuPath" not in props


def test_global_optin_emits_tail_for_templateless_submenu(tmp_path: Path):
    root = _build(tmp_path, GLOBAL_OPTIN_XML)
    props = _item_props(root, "skinshortcuts-mainmenu", "movies")
    assert props.get("submenuPath") == "videodb://movies/recent/"
    assert props.get("submenuPath.2") == "videodb://movies/random/"


def test_permenu_optin_emits_tail_for_templateless_submenu(tmp_path: Path):
    root = _build(tmp_path, PERMENU_OPTIN_XML)
    props = _item_props(root, "skinshortcuts-mainmenu", "movies")
    assert props.get("submenuPath") == "videodb://movies/recent/"
    assert props.get("submenuPath.2") == "videodb://movies/random/"


def test_widget_path_read_in_any_case(tmp_path: Path):
    root = _build(tmp_path, GLOBAL_OPTIN_XML.replace('name="widgetPath"', 'name="widgetpath"'))
    props = _item_props(root, "skinshortcuts-mainmenu", "movies")
    assert props.get("submenuPath") == "videodb://movies/recent/"
    assert props.get("submenuPath.2") == "videodb://movies/random/"


def test_custom_widget_reference_read_in_any_case(tmp_path: Path):
    menus = CW_MENUS_XML.replace('name="customWidget"', 'name="customwidget"').replace(
        '<submenu name="cw.customwidget" type="widgets">', '<submenu name="custom1" type="widgets">'
    )
    root = _build(tmp_path, menus)
    assert "skinshortcuts-cw-customwidget" in {inc.get("name") for inc in root.findall("include")}
