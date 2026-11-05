"""A flat numbered submenu (movies.1) in the dialog, the include build and an items template."""

from __future__ import annotations

import types
import xml.etree.ElementTree as ET
from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig
from skinshortcuts.dialog.base import DialogBaseMixin
from skinshortcuts.dialog.items import ItemsMixin
from skinshortcuts.dialog.subdialogs import SubdialogsMixin
from skinshortcuts.manager import MenuManager
from skinshortcuts.models.menu import SubDialog

MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies" submenu="movies">
      <label>$LOCALIZE[342]</label>
      <action>ActivateWindow(Videos,videodb://movies/titles/,return)</action>
    </item>
  </menu>
  <submenu name="movies">
    <item name="movies-titles">
      <label>test</label>
      <action>ActivateWindow(Videos,videodb://movies/titles/,return)</action>
    </item>
  </submenu>
  <submenu name="movies.1" type="widgets">
    <item name="movies-inprogress">
      <label>$LOCALIZE[31008]</label>
      <action>
        ActivateWindow(Videos,special://skin/extras/playlists/movies/inprogress.xsp,return)
      </action>
    </item>
  </submenu>
</menus>
"""

WIDGETS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<widgets>
  <widget name="recent-movies" label="Recent Movies" type="movies">
    <path>videodb://recentlyaddedmovies/</path>
  </widget>
</widgets>
"""

TEMPLATES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <template items="1" source="1">
    <controls>
      <control type="button" id="$PROPERTY[index]">
        <label>$PROPERTY[label]</label>
        <onclick>$PROPERTY[action]</onclick>
      </control>
    </controls>
  </template>

  <template include="Ring1">
    <controls>
      <control type="grouplist">
        <skinshortcuts insert="1" />
      </control>
    </controls>
  </template>
</templates>
"""


def _setup(tmp_path: Path, widgets: bool = False, templates: bool = False) -> Path:
    """Write menus.xml, plus widgets.xml and templates.xml on request, into a shortcuts folder."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS_XML)
    if widgets:
        (skin / "widgets.xml").write_text(WIDGETS_XML)
    if templates:
        (skin / "templates.xml").write_text(TEMPLATES_XML)
    return skin


def _names(root: ET.Element) -> list[str]:
    """Names of every include in the build."""
    return [inc.get("name", "") for inc in root.findall("include")]


def test_direct_open_resolves_to_the_flat_numbered_menu(tmp_path: Path):
    manager = MenuManager(_setup(tmp_path))
    movies = next(i for i in manager.working["mainmenu"].items if i.name == "movies")

    stub = types.SimpleNamespace(manager=manager, menu_id="mainmenu", _log=lambda _m: None)
    resolve = SubdialogsMixin._resolve_menu_reference.__get__(stub)

    assert resolve("{item}.1", movies, SubDialog(button_id=800, menu="{item}.1")) == "movies.1"
    assert manager.working["movies.1"].items[0].name == "movies-inprogress"


def test_direct_open_runs_the_child_in_customwidget_mode(tmp_path: Path):
    """No mode on the subdialog means the child dialog gets customwidget."""
    manager = MenuManager(_setup(tmp_path))
    opened: list[tuple[str, str]] = []

    stub = types.SimpleNamespace(
        manager=manager,
        _log=lambda _m: None,
        _run_child_dialog=lambda menu_id, mode="": opened.append((menu_id, mode)),
        _refresh_selected_item=lambda: None,
    )
    open_menu = SubdialogsMixin._open_onclose_menu.__get__(stub)
    open_menu("movies.1", SubDialog(button_id=800, menu="{item}.1"))

    assert opened == [("movies.1", "customwidget")]


def _add_item_stub(manager: MenuManager, skin: Path, mode: str):
    """Dialog stand-in holding what _add_item reads, on the movies.1 menu."""
    return types.SimpleNamespace(
        manager=manager,
        menu_id="movies.1",
        shortcuts_path=str(skin),
        dialog_mode=mode,
        items=list(manager.working["movies.1"].items),
        _get_selected_index=lambda: 0,
        _get_selected_item=lambda: None,
        _get_item_properties=lambda _i: {},
        _rebuild_list=lambda focus_index=None: None,
        _log=lambda _m: None,
    )


def test_customwidget_mode_add_button_offers_widgets(tmp_path: Path):
    """301 in a direct-opened .1 menu reaches the widget picker, never the shortcut picker."""
    skin = _setup(tmp_path, widgets=True)
    manager = MenuManager(skin)
    offered: list[str] = []

    stub = _add_item_stub(manager, skin, "customwidget")
    stub._pick_widget_for_add = ItemsMixin._pick_widget_for_add.__get__(stub)
    stub._pick_widget_from_groups = lambda items, _props, **_k: (
        offered.extend(w.name for w in items) or None
    )

    ItemsMixin._add_item.__get__(stub)()

    assert offered == ["recent-movies"]
    assert [i.name for i in manager.working["movies.1"].items] == ["movies-inprogress"]
    assert not manager.has_changes()


def test_shortcut_mode_add_button_does_add(tmp_path: Path):
    """Same menu opened without a widget mode adds a shortcut item."""
    skin = _setup(tmp_path, widgets=True)
    manager = MenuManager(skin)
    stub = _add_item_stub(manager, skin, "")

    ItemsMixin._add_item.__get__(stub)()

    assert len(manager.working["movies.1"].items) == 2
    assert manager.has_changes()


def test_menutype_property_reports_the_target_menu_type(tmp_path: Path):
    manager = MenuManager(_setup(tmp_path))
    props: dict[str, str] = {}

    stub = types.SimpleNamespace(
        manager=manager,
        menu_id="movies.1",
        setProperty=lambda key, value: props.__setitem__(key, value),
        _update_deleted_property=lambda: None,
    )
    DialogBaseMixin._update_window_properties.__get__(stub)()

    assert props["skinshortcuts-menutype"] == "widgets"


def test_numbered_submenu_gets_no_include(tmp_path: Path):
    config = SkinConfig.load(_setup(tmp_path), load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    assert not [n for n in _names(root) if "movies.1" in n]

    combined = next(
        i for i in root.findall("include") if i.get("name") == "skinshortcuts-mainmenu-submenu"
    )
    labels = [label.text for label in combined.iter("label")]
    assert labels == ["test"]
    assert "inprogress.xsp" not in ET.tostring(root, encoding="unicode")


def test_items_template_is_the_path_to_the_skin(tmp_path: Path):
    config = SkinConfig.load(_setup(tmp_path, templates=True), load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    xml = ET.tostring(root, encoding="unicode")
    assert "skinshortcuts-template-Ring1" in _names(root) or "Ring1" in xml
    assert "inprogress.xsp" in xml
