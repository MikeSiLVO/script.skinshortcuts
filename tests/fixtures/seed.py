"""Write userdata.json for the fixture skins by driving MenuManager."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

TESTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(TESTS))
import conftest  # noqa: E402,F401  stubs the xbmc modules

sys.path.insert(0, str(TESTS.parent / "resources" / "lib"))
from skinshortcuts.dialog.items import ItemsMixin  # noqa: E402
from skinshortcuts.loaders.base import iter_nested  # noqa: E402
from skinshortcuts.manager import MenuManager  # noqa: E402
from skinshortcuts.models.background import Background, BackgroundGroup  # noqa: E402
from skinshortcuts.models.menu import Action, MenuItem  # noqa: E402
from skinshortcuts.models.widget import Widget, WidgetGroup  # noqa: E402

SKINS = TESTS / "fixtures" / "skins"


def _widget(m: MenuManager, name: str) -> Widget:
    """A widget definition by name, grouped or top level."""
    found = iter_nested(m.config._widget_config.groupings, Widget, WidgetGroup)
    return next(w for w in [*found, *m.config._widget_config.widgets] if w.name == name)


def _background(m: MenuManager, name: str) -> Background:
    """A background definition by name, grouped or top level."""
    found = iter_nested(m.config._background_config.groupings, Background, BackgroundGroup)
    return next(b for b in found if b.name == name)


def _set(m: MenuManager, menu: str, item: str, values: dict[str, str]) -> None:
    """Set each value under its declared name, clearing empty ones, as the dialog does."""
    schema = m.config.property_schema
    for key, value in values.items():
        m.set_custom_property(menu, item, schema.declared_name(key), value or None)


def pick_widget(m: MenuManager, menu: str, item: str, slot: str, name: str) -> None:
    """Pick a widget the way the dialog's widget button does."""
    w = _widget(m, name)
    _set(m, menu, item, {
        f"widget{slot}": w.name,
        f"widgetLabel{slot}": w.label,
        f"widgetPath{slot}": w.path.replace("{menuitem}", item),
        f"widgetType{slot}": w.type,
        f"widgetTarget{slot}": w.target,
        f"widgetSource{slot}": w.source,
        f"widgetLimit{slot}": str(w.limit or ""),
        f"widgetSortBy{slot}": w.sort_by,
        f"widgetSortOrder{slot}": w.sort_order,
    })


def pick_background(m: MenuManager, menu: str, item: str, name: str, path: str = "") -> None:
    """Pick a background; a path stands in for a browsed image or folder."""
    bg = _background(m, name)
    _set(m, menu, item, {
        "background": bg.name,
        "backgroundLabel": bg.label,
        "backgroundPath": path or bg.path,
        "backgroundType": bg.type_name,
    })


def widget_item(m: MenuManager, name: str) -> MenuItem:
    """A widget submenu item made by the dialog's own mapping."""
    stub = types.SimpleNamespace(property_schema=m.config.property_schema)
    return ItemsMixin._create_item_from_widget(stub, _widget(m, name))


def edit_aeon_layout(m: MenuManager) -> None:
    """Edit the aeon.next layout, shared by kodebug.broken."""
    m.set_label("mainmenu", "tvshows", "Series")
    m.move_item("mainmenu", "power", -1)
    m.remove_item("buttonmenu", "reboot")
    m.add_item("mainmenu", 0, item=MenuItem(
        name="user-music", label="My Music", icon="DefaultMusicAlbums.png",
        actions=[Action(action="ActivateWindow(Music,musicdb://albums/,return)")],
    ))
    pick_widget(m, "mainmenu", "movies-a", "", "recentlyadded-movies")
    pick_widget(m, "mainmenu", "movies-a", ".2", "top250-movies")
    m.set_custom_property("mainmenu", "movies-a", "widgetStyle", "Panel")
    pick_background(m, "mainmenu", "tvshows", "weather-fanart")
    pick_background(m, "mainmenu", "settings", "custom-image", "special://skin/media/settings.jpg")

    custom = m.create_custom_widget_menu("mainmenu", "movies-b")
    _set(m, "mainmenu", "movies-b", {"widget": "customwidget", "widgetType": "custom"})
    m.add_item(custom, item=widget_item(m, "random-movies-pl"))
    m.add_item(custom, item=widget_item(m, "inprogress-movies-pl"))

    movies_a = m._get_working_item("mainmenu", "movies-a")
    movies_b = m._get_working_item("mainmenu", "movies-b")
    settings = m._get_working_item("mainmenu", "settings")
    assert movies_a and movies_b and settings
    m.ensure_item_submenu("mainmenu", movies_a)
    m.set_label("mainmenu/movies-a", "all-movies", "Every Movie")
    m.ensure_item_submenu("mainmenu", movies_b)
    m.remove_item("mainmenu/movies-b", "recent-movies")
    m.ensure_item_submenu("mainmenu", settings)
    m.set_disabled("mainmenu/settings", "addons", True)


def edit_rounded(m: MenuManager) -> None:
    """Edit rounded: its {item}.1 widget menus, a new one, and the power menu."""
    m.set_label("mainmenu", "music", "Tunes")
    m.remove_item("mainmenu", "games")
    m.move_item("mainmenu", "weather", -1)
    m.add_item("mainmenu", 9, item=MenuItem(
        name="user-youtube", label="YouTube", icon="DefaultAddonVideo.png",
        actions=[Action(action="ActivateWindow(Videos,plugin://plugin.video.youtube/,return)")],
    ))
    pick_background(m, "mainmenu", "movies", "custom-image", "special://skin/media/movies.jpg")

    m.remove_item("movies.1", "movies-random")
    m.move_item("movies.1", "movies-new", -1)
    m.set_label("movies.1", "movies-tmdb-popular", "Popular Now")
    m.set_custom_property("tvshows.1", "tvshows-random", "widgetaspect", None)
    m.add_item("pictures.1", item=widget_item(m, "RandomMovies"))

    tvshows = m._get_working_item("mainmenu", "tvshows")
    assert tvshows
    m.ensure_item_submenu("mainmenu", tvshows)
    m.remove_item("mainmenu/tvshows", "tvshows-years")

    m.remove_item("powermenu", "power-mastermode")
    m.set_disabled("powermenu", "power-rebootandroid", True)


def edit_silvo_custom_widgets(m: MenuManager) -> None:
    """Edit in a custom widget for both silvo widget slots, as its onclose actions make them."""
    pick_widget(m, "mainmenu", "music", "", "customwidget")
    custom = m.create_custom_widget_menu("mainmenu", "music")
    m.add_item(custom, item=widget_item(m, "random-movies-pl"))
    m.add_item(custom, item=widget_item(m, "recent-tvshows-pl"))
    pick_widget(m, "mainmenu", "movies", ".2", "customwidget2")
    custom = m.create_custom_widget_menu("mainmenu", "movies", ".2")
    m.add_item(custom, item=widget_item(m, "recent-tvshows-pl"))


def patch_silvo() -> None:
    """Patch silvo's real userdata with custom widgets, copying in only the new parts."""
    fixture = SKINS / "skin.aeon.nox.silvo" / "userdata.json"
    data = json.loads(fixture.read_text(encoding="utf-8"))
    if any(name.startswith("custom-") for name in data["menus"]):
        print("skin.aeon.nox.silvo: already has a custom widget")
        return
    with tempfile.TemporaryDirectory() as tmp:
        userdata = Path(tmp) / "userdata.json"
        shutil.copy(fixture, userdata)
        manager = MenuManager(SKINS / "skin.aeon.nox.silvo" / "shortcuts", str(userdata))
        edit_silvo_custom_widgets(manager)
        assert manager.save()
        saved = json.loads(userdata.read_text(encoding="utf-8"))["menus"]
    for name, menu in saved.items():
        if name.startswith("custom-"):
            data["menus"][name] = menu
    edited = {i["name"]: i for i in saved["mainmenu"]["items"]}
    for item in data["menus"]["mainmenu"]["items"]:
        if item["name"] in ("music", "movies"):
            item["properties"] = edited[item["name"]]["properties"]
    fixture.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("skin.aeon.nox.silvo: custom widgets added")


EDITS = {
    "skin.aeon.next": (edit_aeon_layout, {"library": {"movies": "51", "tvshows": "500"}}),
    "skin.kodebug.broken": (edit_aeon_layout, {}),
    "skin.arctic.zephyr.rounded": (edit_rounded, {}),
}


def main() -> None:
    """Build each skin's userdata in a scratch copy into its fixture, then patch silvo's."""
    for skin, (edit, views) in EDITS.items():
        with tempfile.TemporaryDirectory() as tmp:
            userdata = Path(tmp) / "userdata.json"
            shortcuts = Path(tmp) / "shortcuts"
            shutil.copytree(SKINS / skin / "shortcuts", shortcuts)
            manager = MenuManager(shortcuts, str(userdata))
            edit(manager)
            assert manager.save(), skin
            data = json.loads(userdata.read_text(encoding="utf-8"))
            if views:
                data["views"] = views
            (SKINS / skin / "userdata.json").write_text(
                json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n"
            )
            print(f"{skin}: {len(data.get('menus', {}))} menus")
    patch_silvo()


if __name__ == "__main__":
    main()
