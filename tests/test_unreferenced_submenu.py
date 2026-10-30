"""Unreferenced <submenu> entries must not emit standalone includes."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig


MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="power" submenu="powermenu">
      <label>Power</label>
      <action>Noop</action>
    </item>
  </menu>

  <submenu name="powermenu">
    <item name="reboot">
      <label>Reboot</label>
      <action>Reboot</action>
    </item>
  </submenu>

  <submenu name="orphan">
    <item name="lonely">
      <label>Lonely</label>
      <action>Noop</action>
    </item>
  </submenu>
</menus>
"""


def _setup(tmp_path: Path) -> Path:
    """Write the test menus.xml into a shortcuts folder and return it."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS_XML)
    return skin


def _names(root) -> list[str]:
    """Names of every include in the build."""
    return [inc.get("name", "") for inc in root.findall("include")]


def test_unreferenced_submenu_skipped(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    names = _names(root)
    assert "skinshortcuts-orphan" not in names


def test_referenced_submenu_still_emitted(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    names = _names(root)
    assert "skinshortcuts-powermenu" in names
