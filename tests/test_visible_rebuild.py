"""A visible= attribute decided at build time triggers a rebuild when its result changes."""

from __future__ import annotations

from pathlib import Path

import pytest
import xbmc

from skinshortcuts import hashing, userdata
from skinshortcuts.config import SkinConfig

MENUS_XML = """<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>Noop</action></item>
    <item name="reboot" visible="System.HasAddon(service.libreelec.settings)">
      <label>Reboot</label><action>Reboot</action>
    </item>
  </menu>
</menus>"""


@pytest.fixture
def skin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, dict[str, bool]]:
    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()
    (shortcuts / "menus.xml").write_text(MENUS_XML, encoding="utf-8")
    monkeypatch.setattr(userdata, "get_userdata_path", lambda: str(tmp_path / "userdata.json"))
    monkeypatch.setattr(hashing, "get_hash_file_path", lambda: str(tmp_path / "hashes"))
    state = {"System.HasAddon(service.libreelec.settings)": False}
    monkeypatch.setattr(xbmc, "getCondVisibility", lambda cond: state.get(cond, False))
    return shortcuts, state


def test_build_follows_the_attribute(skin: tuple[Path, dict[str, bool]]) -> None:
    shortcuts, state = skin
    names = [i.name for i in SkinConfig.load(str(shortcuts)).get_menu("mainmenu").items]
    assert names == ["movies"]
    state["System.HasAddon(service.libreelec.settings)"] = True
    names = [i.name for i in SkinConfig.load(str(shortcuts)).get_menu("mainmenu").items]
    assert names == ["movies", "reboot"]


def test_flipped_attribute_needs_a_rebuild(skin: tuple[Path, dict[str, bool]]) -> None:
    shortcuts, state = skin
    hashing.write_hashes(hashing.generate_config_hashes(shortcuts))
    assert hashing.needs_rebuild(shortcuts) is False
    state["System.HasAddon(service.libreelec.settings)"] = True
    assert hashing.needs_rebuild(shortcuts) is True


def test_no_visible_attribute_matches_older_stored_hashes(skin) -> None:
    shortcuts, _state = skin
    (shortcuts / "menus.xml").write_text(MENUS_XML.replace(
        ' visible="System.HasAddon(service.libreelec.settings)"', ""), encoding="utf-8")
    stored = hashing.generate_config_hashes(shortcuts)
    assert stored.pop("visible") is None
    hashing.write_hashes(stored)
    assert hashing.needs_rebuild(shortcuts) is False
