"""Named submenus emit their own includes and keep their name in the menu property."""

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
    <item name="movies" submenu="movies">
      <label>Movies</label>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
    </item>
  </menu>

  <submenu name="powermenu">
    <item name="reboot">
      <label>Reboot</label>
      <action>Reboot</action>
    </item>
    <item name="shutdown">
      <label>Shutdown</label>
      <action>ShutDown()</action>
    </item>
  </submenu>

  <submenu name="movies">
    <item name="recent">
      <label>Recently Added</label>
      <action>ActivateWindow(Videos,videodb://recentlyaddedmovies/)</action>
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


def test_named_submenus_emit_their_includes(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    names = _names(root)
    assert "skinshortcuts-mainmenu" in names
    assert "skinshortcuts-mainmenu-submenu" in names
    assert "skinshortcuts-powermenu" in names
    assert "skinshortcuts-movies" in names


def test_per_item_key_not_in_include_names(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    for name in _names(root):
        assert "/" not in name, f"include name should not contain '/': {name!r}"


def test_submenu_items_property_menu_uses_template_name(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    powermenu = next(
        i for i in root.findall("include") if i.get("name") == "skinshortcuts-powermenu"
    )
    items = powermenu.findall("item")
    assert items, "powermenu should have items"
    for item in items:
        menu_prop = next(
            (p.text for p in item.findall("property") if p.get("name") == "menu"), None
        )
        assert menu_prop == "powermenu", (
            f"Property(menu) should be 'powermenu', got {menu_prop!r}"
        )


def test_combined_submenu_property_menu_uses_template_name(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    combined = next(
        i for i in root.findall("include") if i.get("name") == "skinshortcuts-mainmenu-submenu"
    )
    for item in combined.findall("item"):
        parent = next(
            (p.text for p in item.findall("property") if p.get("name") == "parent"), None
        )
        menu_prop = next(
            (p.text for p in item.findall("property") if p.get("name") == "menu"), None
        )
        if parent == "power":
            assert menu_prop == "powermenu"
        elif parent == "movies":
            assert menu_prop == "movies"
