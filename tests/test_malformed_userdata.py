"""A damaged userdata file falls back to skin defaults and is kept as a .bak copy."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from skinshortcuts.config import SkinConfig
from skinshortcuts.manager import MenuManager
from skinshortcuts.userdata import load_userdata

SILVO = Path(__file__).parent / "fixtures" / "skins" / "skin.aeon.nox.silvo" / "shortcuts"

ITEM = {"name": "movies", "label": "Films"}
DAMAGED = {
    "unknown item key": json.dumps({"menus": {"mainmenu": {"items": [{**ITEM, "later": 1}]}}}),
    "unknown action key": json.dumps(
        {"menus": {"mainmenu": {"items": [{**ITEM, "actions": [{"action": "x", "later": 1}]}]}}}
    ),
    "top-level list": json.dumps([ITEM]),
    "item without name": json.dumps({"menus": {"mainmenu": {"items": [{"label": "Films"}]}}}),
}
TRUNCATED = json.dumps({"menus": {"mainmenu": {"items": [ITEM]}}})[:-5]


@pytest.mark.parametrize("text", DAMAGED.values(), ids=DAMAGED.keys())
def test_damaged_file_loads_defaults_and_keeps_a_copy(tmp_path: Path, text: str):
    path = tmp_path / "userdata.json"
    path.write_text(text, encoding="utf-8")
    config = SkinConfig.load(SILVO, userdata_path=str(path))
    assert config.userdata.menus == {}
    assert (tmp_path / "userdata.json.bak").read_text(encoding="utf-8") == text


def test_bad_encoding_loads_defaults_and_keeps_a_copy(tmp_path: Path):
    path = tmp_path / "userdata.json"
    raw = json.dumps({"menus": {"mainmenu": {"items": [ITEM]}}}).encode("utf-16")
    path.write_bytes(raw)
    assert load_userdata(str(path)).menus == {}
    assert (tmp_path / "userdata.json.bak").read_bytes() == raw


def test_truncated_file_loads_defaults(tmp_path: Path):
    path = tmp_path / "userdata.json"
    path.write_text(TRUNCATED, encoding="utf-8")
    assert load_userdata(str(path)).menus == {}


def test_failed_copy_still_loads_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    path = tmp_path / "userdata.json"
    path.write_text(TRUNCATED, encoding="utf-8")

    def refuse(*_args):
        raise OSError("No space left on device")

    monkeypatch.setattr("skinshortcuts.userdata.shutil.copyfile", refuse)
    assert load_userdata(str(path)).menus == {}
    assert path.read_text(encoding="utf-8") == TRUNCATED


def test_truncated_file_survives_the_next_save(tmp_path: Path):
    path = tmp_path / "userdata.json"
    path.write_text(TRUNCATED, encoding="utf-8")
    manager = MenuManager(SILVO, str(path))
    manager.set_label("mainmenu", "music", "Tunes")
    assert manager.save()
    assert (tmp_path / "userdata.json.bak").read_text(encoding="utf-8") == TRUNCATED
