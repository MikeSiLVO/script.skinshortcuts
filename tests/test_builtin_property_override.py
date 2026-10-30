"""A skin property named like a built-in replaces it instead of emitting twice."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.config import SkinConfig

MENUS = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies">
      <label>Movies</label>
      <action>ActivateWindow(Videos,videodb://movies/,return)</action>
      <property name="submenuVisibility">CUSTOM</property>
      <property name="path">OVERRIDE</property>
    </item>
    <item name="tv">
      <label>TV</label>
      <action>Noop</action>
    </item>
  </menu>
</menus>
"""


def _item_properties(tmp_path: Path, name: str) -> list[tuple[str, str]]:
    """Every (name, value) property emitted for one menu item, in order."""
    import xml.etree.ElementTree as ET

    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir(exist_ok=True)
    (shortcuts / "menus.xml").write_text(MENUS)

    config = SkinConfig.load(shortcuts, userdata_path=str(tmp_path / "ud.json"))
    out = tmp_path / "includes.xml"
    config.build_includes(out)

    root = ET.parse(out).getroot()
    for item in root.iter("item"):
        props = [(p.get("name") or "", p.text or "") for p in item.findall("property")]
        if dict(props).get("name") == name:
            return props
    raise AssertionError(f"item {name} not found")


def test_no_duplicate_property_names(tmp_path: Path):
    names = [n for n, _ in _item_properties(tmp_path, "movies")]

    assert len(names) == len(set(names)), f"duplicate property names: {names}"


def test_skin_value_wins_over_builtin(tmp_path: Path):
    props = dict(_item_properties(tmp_path, "movies"))

    assert props["submenuVisibility"] == "CUSTOM"
    assert props["path"] == "OVERRIDE"


def test_override_keeps_the_builtin_slot(tmp_path: Path):
    names = [n for n, _ in _item_properties(tmp_path, "movies")]

    assert names[:6] == ["id", "name", "menu", "action", "path", "submenuVisibility"]


def test_builtins_still_default_without_an_override(tmp_path: Path):
    props = dict(_item_properties(tmp_path, "tv"))

    assert props["submenuVisibility"] == "tv"
    assert props["name"] == "tv"
    assert props["menu"] == "mainmenu"
