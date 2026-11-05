"""A <submenu standalone="false"> suppresses the per-template skinshortcuts-{name} include."""

from __future__ import annotations

import json
from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig

MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies" submenu="movies">
      <label>Movies</label>
      <action>ActivateWindow(Videos,videodb://movies/,return)</action>
    </item>
    <item name="tvshows" submenu="tvshows">
      <label>TV Shows</label>
      <action>ActivateWindow(Videos,videodb://tvshows/,return)</action>
    </item>
  </menu>

  <submenu name="movies" standalone="false">
    <item name="movies-recent">
      <label>Recently Added</label>
      <action>ActivateWindow(Videos,videodb://recentlyaddedmovies/,return)</action>
    </item>
  </submenu>

  <submenu name="tvshows">
    <item name="tvshows-recent">
      <label>Recently Added</label>
      <action>ActivateWindow(Videos,videodb://recentlyaddedepisodes/,return)</action>
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


def test_standalone_false_skips_per_template_include(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    names = _names(root)
    assert "skinshortcuts-movies" not in names
    assert "skinshortcuts-tvshows" in names


def test_standalone_false_keeps_combined_include(tmp_path: Path):
    skin = _setup(tmp_path)
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    combined = next(
        (
            inc for inc in root.findall("include")
            if inc.get("name") == "skinshortcuts-mainmenu-submenu"
        ),
        None,
    )
    assert combined is not None

    parents = [
        next((p.text for p in item.findall("property") if p.get("name") == "parent"), None)
        for item in combined.findall("item")
    ]
    assert "movies" in parents
    assert "tvshows" in parents


def test_standalone_default_true(tmp_path: Path):
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies" submenu="movies">
      <label>Movies</label>
      <action>Noop</action>
    </item>
  </menu>
  <submenu name="movies">
    <item name="movies-recent">
      <label>Recent</label>
      <action>Noop</action>
    </item>
  </submenu>
</menus>
""")
    config = SkinConfig.load(skin, load_user=False)
    root = IncludesBuilder(config.menus, templates=config.templates).build()

    names = _names(root)
    assert "skinshortcuts-movies" in names


def test_standalone_false_survives_userdata_override(tmp_path: Path):
    """Userdata customizing the submenu must keep standalone=false through merge_menu."""
    skin = _setup(tmp_path)
    userdata = tmp_path / "userdata.json"
    userdata.write_text(json.dumps({
        "menus": {
            "mainmenu/movies": {
                "items": [
                    {
                        "name": "custom-movie-item",
                        "label": "Custom",
                        "actions": [{"action": "Noop"}],
                        "icon": "DefaultShortcut.png",
                        "is_new": True,
                        "position": 0,
                    }
                ]
            }
        }
    }))

    config = SkinConfig.load(skin, load_user=True, userdata_path=str(userdata))
    root = IncludesBuilder(
        config.menus,
        templates=config.templates,
        userdata=config.userdata,
    ).build()

    names = _names(root)
    assert "skinshortcuts-movies" not in names
