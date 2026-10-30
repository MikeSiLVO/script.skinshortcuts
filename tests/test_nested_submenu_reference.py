"""A submenu linked only from inside another submenu is flat to config and manager alike."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from skinshortcuts.config import SkinConfig
from skinshortcuts.manager import MenuManager

SILVO = Path(__file__).parent / "fixtures" / "skins" / "skin.aeon.nox.silvo"
EXTRAS = (
    '<submenu name="extras"><item name="extra-one"><label>Extra one</label>'
    "<action>Noop</action></item></submenu>"
)


@pytest.fixture
def skin(tmp_path: Path) -> Path:
    """A silvo copy whose movies submenu links submenu extras, plus a user diff for extras."""
    shortcuts = tmp_path / "shortcuts"
    shutil.copytree(SILVO / "shortcuts", shortcuts)
    menus = shortcuts / "menus.xml"
    text = menus.read_text(encoding="utf-8")
    old = '<item name="movies-recent"'
    text = text.replace(f"{old}>", f'{old} submenu="extras">')
    menus.write_text(text.replace("</menus>", f"{EXTRAS}</menus>"), encoding="utf-8")
    diff = {"menus": {"extras": {"items": [{"name": "extra-one", "label": "My extra"}]}}}
    (tmp_path / "userdata.json").write_text(json.dumps(diff), encoding="utf-8")
    return shortcuts


def test_config_builds_extras_flat_with_the_user_diff(skin: Path, tmp_path: Path):
    config = SkinConfig.load(skin, userdata_path=str(tmp_path / "userdata.json"))
    extras = config.get_menu("extras")
    assert extras is not None
    assert [item.label for item in extras.items] == ["My extra"]


def test_manager_can_edit_extras(skin: Path, tmp_path: Path):
    manager = MenuManager(skin, str(tmp_path / "userdata.json"))
    assert [item.label for item in manager.get_menu_items("extras")] == ["My extra"]


def test_unrelated_save_keeps_the_extras_diff(skin: Path, tmp_path: Path):
    userdata = tmp_path / "userdata.json"
    manager = MenuManager(skin, str(userdata))
    manager.set_label("mainmenu", "music", "Tunes")
    assert manager.save()
    assert "extras" in json.loads(userdata.read_text(encoding="utf-8"))["menus"]
