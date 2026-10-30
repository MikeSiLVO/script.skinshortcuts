"""A picked widget keeps its stored values; only the item's skin default follows the skin."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

from skinshortcuts.config import SkinConfig
from skinshortcuts.manager import MenuManager

SILVO = Path(__file__).parent / "fixtures" / "skins" / "skin.aeon.nox.silvo"
WIDGET = "recentlyadded-movies"
PATH = "videodb://recentlyaddedmovies/"


@pytest.fixture
def skin(tmp_path: Path) -> Path:
    shortcuts = tmp_path / "shortcuts"
    shutil.copytree(SILVO / "shortcuts", shortcuts)
    return shortcuts


def _pick(manager: MenuManager, item_name: str) -> None:
    """Pick the widget on a mainmenu item as the dialog does, storing its name and each sibling."""
    widget = manager.config.get_widget(WIDGET)
    assert widget is not None
    values = {
        "widget": widget.name,
        "widgetLabel": widget.label,
        "widgetPath": widget.path,
        "widgetType": widget.type,
        "widgetTarget": widget.target,
        "widgetSource": widget.source,
    }
    for name, value in values.items():
        manager.set_custom_property("mainmenu", item_name, name, value or None)


def _edit_widgets(skin: Path, replacement: str) -> None:
    """Edit widgets.xml by replacing the test widget's entry, asserting it appears once."""
    path = skin / "widgets.xml"
    pattern = rf'<widget name="{WIDGET}".*?</widget>'
    text, count = re.subn(pattern, replacement, path.read_text(encoding="utf-8"), flags=re.S)
    assert count == 1
    path.write_text(text, encoding="utf-8")


def _built(skin: Path, userdata: Path, item_name: str) -> dict[str, str]:
    """Item properties as the build sees them."""
    config = SkinConfig.load(skin, userdata_path=str(userdata))
    menu = config.get_menu("mainmenu")
    assert menu is not None
    config.resolve_item_properties(menu)
    item = menu.get_item(item_name)
    assert item is not None
    return item.properties


def _save_picks(skin: Path, userdata: Path) -> str:
    """Save widget picks on skin item pictures and on a user-added item; returns the added name."""
    manager = MenuManager(skin, str(userdata))
    added = manager.add_item("mainmenu", label="Mine")
    _pick(manager, "pictures")
    _pick(manager, added.name)
    assert manager.save()
    return added.name


def test_user_added_item_keeps_a_dropped_widget(skin: Path, tmp_path: Path):
    userdata = tmp_path / "userdata.json"
    added = _save_picks(skin, userdata)
    _edit_widgets(skin, "")
    assert _built(skin, userdata, added)["widgetPath"] == PATH


def test_skin_item_keeps_a_dropped_widget(skin: Path, tmp_path: Path):
    userdata = tmp_path / "userdata.json"
    _save_picks(skin, userdata)
    _edit_widgets(skin, "")
    built = _built(skin, userdata, "pictures")
    assert built["widget"] == WIDGET
    assert built.get("widgetPath") == PATH
    assert built.get("widgetType") == "movies"


def test_skin_item_keeps_the_picked_path_after_a_skin_edit(skin: Path, tmp_path: Path):
    userdata = tmp_path / "userdata.json"
    _save_picks(skin, userdata)
    _edit_widgets(
        skin,
        f'<widget name="{WIDGET}" label="Edited" type="movies">'
        "<path>videodb://x/</path></widget>",
    )
    assert _built(skin, userdata, "pictures").get("widgetPath") == PATH


def test_skin_item_stores_the_picked_values(skin: Path, tmp_path: Path):
    userdata = tmp_path / "userdata.json"
    _save_picks(skin, userdata)
    saved = json.loads(userdata.read_text(encoding="utf-8"))
    pictures = next(i for i in saved["menus"]["mainmenu"]["items"] if i["name"] == "pictures")
    assert pictures["properties"].get("widgetPath") == PATH


def test_build_fill_leaves_the_stored_diff_alone(skin: Path, tmp_path: Path):
    userdata = tmp_path / "userdata.json"
    manager = MenuManager(skin, str(userdata))
    added = manager.add_item("mainmenu", label="Mine")
    manager.set_custom_property("mainmenu", added.name, "widget", WIDGET)
    assert manager.save()
    config = SkinConfig.load(skin, userdata_path=str(userdata))
    stored = next(i for i in config.userdata.menus["mainmenu"].items if i.name == added.name)
    before = dict(stored.properties)
    menu = config.get_menu("mainmenu")
    assert menu is not None
    config.resolve_item_properties(menu)
    assert stored.properties == before
