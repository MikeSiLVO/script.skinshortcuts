"""Action overrides substitute one hop at build time and never change what the user stored."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from skinshortcuts.config import SkinConfig
from skinshortcuts.manager import MenuManager

SILVO = Path(__file__).parent / "fixtures" / "skins" / "skin.aeon.nox.silvo"
TEMPLATE_ACTION = "ActivateWindow(Videos,videodb://recentlyaddedmovies/,return)"
HOP = "ActivateWindow(Videos,videodb://hop/,return)"
FAR = "ActivateWindow(Videos,videodb://far/,return)"
STORED = "ActivateWindow(Videos,videodb://stored/,return)"
STORED_HOP = "ActivateWindow(Videos,videodb://storedhop/,return)"
OVERRIDES = (
    f'<overrides><action replace="{TEMPLATE_ACTION}">{HOP}</action>'
    f'<action replace="{HOP}">{FAR}</action>'
    f'<action replace="{STORED}">{STORED_HOP}</action></overrides>'
)


def _skin(tmp_path: Path, two_instances: bool) -> Path:
    """A silvo copy with the overrides; optionally tvshows also links the movies submenu."""
    shortcuts = tmp_path / "shortcuts"
    shutil.copytree(SILVO / "shortcuts", shortcuts)
    menus = shortcuts / "menus.xml"
    text = menus.read_text(encoding="utf-8").replace("</menus>", f"{OVERRIDES}</menus>")
    if two_instances:
        text = text.replace('<item name="tvshows" submenu="tvshows">',
                            '<item name="tvshows" submenu="movies">')
    menus.write_text(text, encoding="utf-8")
    return shortcuts


def _stored_userdata(tmp_path: Path) -> Path:
    """Userdata where the user gave pictures an action the skin overrides."""
    path = tmp_path / "userdata.json"
    item = {"name": "pictures", "actions": [{"action": STORED}]}
    path.write_text(json.dumps({"menus": {"mainmenu": {"items": [item]}}}), encoding="utf-8")
    return path


def _built(skin: Path, tmp_path: Path) -> str:
    """Includes XML the skin builds without userdata."""
    out = tmp_path / "includes.xml"
    SkinConfig.load(skin, load_user=False).build_includes(out)
    return out.read_text(encoding="utf-8")


def test_one_instance_builds_one_hop(tmp_path: Path):
    built = _built(_skin(tmp_path, two_instances=False), tmp_path)
    assert "videodb://hop/" in built
    assert "videodb://far/" not in built


def test_two_instances_build_one_hop(tmp_path: Path):
    built = _built(_skin(tmp_path, two_instances=True), tmp_path)
    assert "videodb://hop/" in built
    assert "videodb://far/" not in built


def test_load_keeps_the_stored_action(tmp_path: Path):
    config = SkinConfig.load(_skin(tmp_path, False), userdata_path=str(_stored_userdata(tmp_path)))
    stored = config.userdata.menus["mainmenu"].items[0]
    assert stored.actions[0].action == STORED


def test_unrelated_save_keeps_the_stored_action(tmp_path: Path):
    userdata = _stored_userdata(tmp_path)
    manager = MenuManager(_skin(tmp_path, False), str(userdata))
    manager.set_label("mainmenu", "music", "Tunes")
    assert manager.save()
    saved = json.loads(userdata.read_text(encoding="utf-8"))["menus"]["mainmenu"]["items"]
    pictures = next(item for item in saved if item["name"] == "pictures")
    assert pictures["actions"] == [{"action": STORED}]


def test_defaults_keep_the_skin_action(tmp_path: Path):
    config = SkinConfig.load(_skin(tmp_path, False), load_user=False)
    template = config.get_default_menu("movies")
    assert template.get_item("movies-recent").actions[0].action == TEMPLATE_ACTION
