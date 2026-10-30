"""End to end check of unlimited widgets per menu item via {item}.N."""

from __future__ import annotations

import json
import types
import xml.etree.ElementTree as ET
from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig
from skinshortcuts.dialog.items import ItemsMixin
from skinshortcuts.loaders.widget import load_widgets
from skinshortcuts.manager import MenuManager


MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies">
      <label>$LOCALIZE[342]</label>
      <action>ActivateWindow(Videos,videodb://movies/titles/,return)</action>
    </item>
  </menu>
  <submenu name="movies.1" type="widgets">
    <item name="movies-inprogress">
      <label>Inprogress</label>
      <action>ActivateWindow(Videos,special://skin/extras/playlists/movies/inprogress.xsp)</action>
    </item>
    <item name="movies-recently added">
      <label>Recently added</label>
      <action>ActivateWindow(Videos,videodb://recentlyaddedmovies/)</action>
    </item>
  </submenu>
  <dialogs>
    <subdialog buttonID="800" menu="{item}.1" />
  </dialogs>
</menus>
"""

WIDGETS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<widgets>
  <widget name="recent-movies" label="Recently Added" type="movies" target="videos">
    <path>videodb://recentlyaddedmovies/</path>
  </widget>
  <widget name="random-movies" label="Random" type="movies" target="videos">
    <path>videodb://movies/titles/?sort=random</path>
  </widget>
</widgets>
"""


def _templates(source: str, prop: str) -> str:
    """Templates XML holding a submenu template and an items template feeding it."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <template include="submenu" menu="mainmenu">
    <controls>
      <control type="grouplist" id="$MATH[9000 + (index * 100)]">
        <visible>String.IsEqual(Container(9000).ListItem.Property(submenuVisibility),\
$PROPERTY[submenuVisibility])</visible>
        <skinshortcuts insert="widget" />
      </control>
    </controls>
  </template>
  <template items="widget" source="{source}">
    <controls>
      <include content="PanelWidget">
        <param name="id">$MATH[9000 + ($PARENT[index] * 100) + index]</param>
        <param name="path">$PROPERTY[{prop}]</param>
      </include>
    </controls>
  </template>
</templates>
"""


def _skin(tmp_path: Path, menus: str = MENUS_XML, widgets: str = WIDGETS_XML,
          source: str = "1", prop: str = "path") -> Path:
    """Write a test skin's shortcuts folder and return its path."""
    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()
    (shortcuts / "menus.xml").write_text(menus)
    if widgets:
        (shortcuts / "widgets.xml").write_text(widgets)
    (shortcuts / "templates.xml").write_text(_templates(source, prop))
    return shortcuts


def _build(shortcuts: Path, userdata: Path | None = None) -> ET.Element:
    """Build includes for a skin folder, with or without a user file."""
    config = SkinConfig.load(
        shortcuts, load_user=userdata is not None,
        userdata_path=str(userdata) if userdata else None,
    )
    return IncludesBuilder(config.menus, templates=config.templates).build()


def _params(root: ET.Element, name: str) -> list[str]:
    """Text of every <param> of a given name in the build."""
    return [p.text or "" for p in root.iter("param") if p.get("name") == name]


def _pick_widget(shortcuts: Path, widget_name: str):
    """Pick a widgets.xml entry and return the menu item the widget picker makes from it."""
    widget = next(w for w in load_widgets(shortcuts / "widgets.xml").widgets
                  if w.name == widget_name)
    stub = types.SimpleNamespace(property_schema=None)
    return ItemsMixin._create_item_from_widget.__get__(stub)(widget)


def test_skin_defined_items_build_one_widget_each(tmp_path: Path):
    """Shipped .1 items produce a widget per item."""
    root = _build(_skin(tmp_path))

    paths = _params(root, "path")
    assert paths == [
        "special://skin/extras/playlists/movies/inprogress.xsp",
        "videodb://recentlyaddedmovies/",
    ]
    assert _params(root, "id") == ["9101", "9102"]


def test_picked_widget_carries_no_action(tmp_path: Path):
    """A picked widget stores widgetPath; a template reading path emits the noop stand-in."""
    shortcuts = _skin(tmp_path)
    userdata = tmp_path / "ud.json"

    manager = MenuManager(shortcuts, userdata_path=str(userdata))
    manager.working["movies.1"].items.clear()
    manager.add_item("movies.1", after_index=None, item=_pick_widget(shortcuts, "recent-movies"))
    assert manager.save()

    stored = json.loads(userdata.read_text())["menus"]["movies.1"]["items"][0]
    assert stored["properties"]["widgetPath"] == "videodb://recentlyaddedmovies/"
    assert "action" not in stored

    # userdata gives an actionless item a noop action, which is what path resolves to
    assert _params(_build(shortcuts, userdata), "path") == ["noop"]


def test_widgetpath_is_the_property_to_read(tmp_path: Path):
    """Same pick, template reading widgetPath: the widget reaches the skin."""
    shortcuts = _skin(tmp_path, prop="widgetPath")
    userdata = tmp_path / "ud.json"

    manager = MenuManager(shortcuts, userdata_path=str(userdata))
    manager.working["movies.1"].items.clear()
    manager.add_item("movies.1", after_index=None, item=_pick_widget(shortcuts, "recent-movies"))
    manager.add_item("movies.1", after_index=None, item=_pick_widget(shortcuts, "random-movies"))
    assert manager.save()

    root = _build(shortcuts, userdata)
    assert _params(root, "path") == [
        "videodb://recentlyaddedmovies/",
        "videodb://movies/titles/?sort=random",
    ]
    assert _params(root, "id") == ["9101", "9102"]


def test_user_widgets_stack_on_top_of_skin_defaults(tmp_path: Path):
    """Unlimited: the picked widget lands beside the shipped items, all iterated."""
    shortcuts = _skin(tmp_path, prop="widgetPath")
    userdata = tmp_path / "ud.json"

    manager = MenuManager(shortcuts, userdata_path=str(userdata))
    manager.add_item("movies.1", after_index=None, item=_pick_widget(shortcuts, "random-movies"))
    assert manager.save()

    root = _build(shortcuts, userdata)
    assert len(_params(root, "id")) == 3
    assert _params(root, "path")[-1] == "videodb://movies/titles/?sort=random"


def test_submenu_name_is_free(tmp_path: Path):
    """A .widgets suffix behaves the same as .1; the source attribute is the only link."""
    menus = MENUS_XML.replace('name="movies.1"', 'name="movies.widgets"').replace(
        'menu="{item}.1"', 'menu="{item}.widgets"'
    )
    shortcuts = _skin(tmp_path, menus=menus, source="widgets")

    assert _params(_build(shortcuts), "path") == [
        "special://skin/extras/playlists/movies/inprogress.xsp",
        "videodb://recentlyaddedmovies/",
    ]


def test_picker_offers_the_widgets_xml_entries(tmp_path: Path):
    """Add (301) in a widgets dialog reaches the widget picker with what widgets.xml defines."""
    shortcuts = _skin(tmp_path)
    offered: list[str] = []

    stub = types.SimpleNamespace(
        shortcuts_path=str(shortcuts),
        _get_selected_item=lambda: None,
        _get_item_properties=lambda _i: {},
        _pick_widget_from_groups=lambda items, _props, **_k: (
            offered.extend(w.name for w in items) or None
        ),
    )
    ItemsMixin._pick_widget_for_add.__get__(stub)()

    assert offered == ["recent-movies", "random-movies"]


def test_picker_has_nothing_to_offer_without_widgets_xml(tmp_path: Path):
    """No widgets.xml: the picker returns before opening."""
    shortcuts = _skin(tmp_path, widgets="")
    called: list[str] = []

    stub = types.SimpleNamespace(
        shortcuts_path=str(shortcuts),
        _get_selected_item=lambda: None,
        _get_item_properties=lambda _i: {},
        _pick_widget_from_groups=lambda *_a, **_k: called.append("opened"),
    )

    assert ItemsMixin._pick_widget_for_add.__get__(stub)() is None
    assert not called


SHIPPED_WIDGETS_MENUS = MENUS_XML.replace(
    "      <action>ActivateWindow(Videos,special://skin/extras/playlists/movies/inprogress.xsp)"
    "</action>",
    "      <property name=\"widgetPath\">special://skin/extras/playlists/movies/inprogress.xsp"
    "</property>\n      <property name=\"widgetType\">movies</property>",
).replace(
    "      <action>ActivateWindow(Videos,videodb://recentlyaddedmovies/)</action>",
    "      <property name=\"widgetPath\">videodb://recentlyaddedmovies/</property>\n"
    "      <property name=\"widgetType\">movies</property>",
)


def test_shipped_defaults_carry_widget_properties(tmp_path: Path):
    """Skin-shipped items in the submenu are the defaults; give them widgetPath, not an action."""
    shortcuts = _skin(tmp_path, menus=SHIPPED_WIDGETS_MENUS, prop="widgetPath")
    userdata = tmp_path / "ud.json"

    manager = MenuManager(shortcuts, userdata_path=str(userdata))
    manager.add_item("movies.1", after_index=None, item=_pick_widget(shortcuts, "random-movies"))
    assert manager.save()

    assert _params(_build(shortcuts, userdata), "path") == [
        "special://skin/extras/playlists/movies/inprogress.xsp",
        "videodb://recentlyaddedmovies/",
        "videodb://movies/titles/?sort=random",
    ]


def test_submenu_attribute_breaks_the_items_lookup(tmp_path: Path):
    """Referencing the submenu with submenu="movies.1" moves it to a per-item key."""
    menus = MENUS_XML.replace('<item name="movies">', '<item name="movies" submenu="movies.1">')
    shortcuts = _skin(tmp_path, menus=menus)

    unreferenced = tmp_path / "plain"
    unreferenced.mkdir()

    assert _params(_build(shortcuts), "path") == []
    assert _params(_build(_skin(unreferenced)), "path") != []


def test_binding_is_the_item_name(tmp_path: Path):
    """The tie is the parent item's name; a user-added item gets its own list too."""
    shortcuts = _skin(tmp_path, prop="widgetPath")
    userdata = tmp_path / "ud.json"
    userdata.write_text(json.dumps({"menus": {
        "mainmenu": {"items": [
            {"name": "movies"},
            {"name": "user-abc123", "is_new": True, "label": "Mine"},
        ]},
        "user-abc123.1": {"items": [
            {"name": "w1", "is_new": True, "label": "Mine",
             "properties": {"widgetPath": "videodb://movies/titles/?sort=random"}},
        ]},
    }}))

    root = _build(shortcuts, userdata)
    assert "videodb://movies/titles/?sort=random" in _params(root, "path")
    assert _params(root, "id") == ["9101", "9102", "9201"]


TWO_LIST_MENUS = MENUS_XML.replace("</menus>", """  <submenu name="movies.hub" type="widgets">
    <item name="movies-hub-1">
      <label>Hub</label>
      <property name="widgetPath">videodb://movies/genres/</property>
    </item>
  </submenu>
</menus>""")

TWO_LIST_TEMPLATES = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <template include="submenu" menu="mainmenu">
    <controls>
      <control type="grouplist" id="$MATH[9000 + (index * 100)]">
        <skinshortcuts insert="first" />
        <skinshortcuts insert="second" />
      </control>
    </controls>
  </template>
  <template items="first" source="1">
    <controls>
      <include content="PanelWidget">
        <param name="path">$PROPERTY[path]</param>
      </include>
    </controls>
  </template>
  <template items="second" source="hub">
    <controls>
      <include content="PanelWidget">
        <param name="path">$PROPERTY[widgetPath]</param>
      </include>
    </controls>
  </template>
</templates>
"""


def test_one_item_can_carry_several_lists(tmp_path: Path):
    """The suffix is free text; movies.1 and movies.hub are two lists on the same item."""
    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()
    (shortcuts / "menus.xml").write_text(TWO_LIST_MENUS)
    (shortcuts / "widgets.xml").write_text(WIDGETS_XML)
    (shortcuts / "templates.xml").write_text(TWO_LIST_TEMPLATES)

    assert _params(_build(shortcuts), "path") == [
        "special://skin/extras/playlists/movies/inprogress.xsp",
        "videodb://recentlyaddedmovies/",
        "videodb://movies/genres/",
    ]
