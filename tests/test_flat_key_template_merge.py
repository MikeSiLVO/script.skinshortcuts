"""Userdata at non-referenced submenu templates merges into the template."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from skinshortcuts.config import SkinConfig


MENUS_XML = """<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label></item>
  </menu>
  <submenu name="movies.1" type="widgets">
    <item name="default-widget"><label>Default</label></item>
  </submenu>
</menus>"""


def _build_skin(tmp: Path) -> Path:
    """Build a shortcuts folder holding the test menus.xml and return it."""
    shortcuts = tmp / "shortcuts"
    shortcuts.mkdir()
    (shortcuts / "menus.xml").write_text(MENUS_XML)
    return shortcuts


def test_userdata_at_non_referenced_template_merges():
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        shortcuts = _build_skin(td_path)
        userdata = td_path / "ud.json"
        userdata.write_text(json.dumps({
            "menus": {
                "mainmenu": {"items": [{"name": "movies"}]},
                "movies.1": {"items": [
                    {"name": "user-widget", "is_new": True, "label": "User Widget"},
                ]},
            }
        }))

        cfg = SkinConfig.load(shortcuts, userdata_path=str(userdata))
        movies_template = next((m for m in cfg.menus if m.name == "movies.1"), None)
        assert movies_template is not None
        names = [i.name for i in movies_template.items]
        assert "default-widget" in names
        assert "user-widget" in names


def test_referenced_template_uses_per_item_form():
    menus_xml = MENUS_XML.replace(
        '<item name="movies"><label>Movies</label></item>',
        '<item name="movies" submenu="movies.1"><label>Movies</label></item>',
    )
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        shortcuts = td_path / "shortcuts"
        shortcuts.mkdir()
        (shortcuts / "menus.xml").write_text(menus_xml)
        userdata = td_path / "ud.json"
        userdata.write_text(json.dumps({
            "menus": {
                "mainmenu": {"items": [{"name": "movies"}]},
                "mainmenu/movies": {"items": [
                    {"name": "user-widget", "is_new": True, "label": "User Widget"},
                ]},
            }
        }))

        cfg = SkinConfig.load(shortcuts, userdata_path=str(userdata))
        per_item = next((m for m in cfg.menus if m.name == "mainmenu/movies"), None)
        assert per_item is not None
        names = [i.name for i in per_item.items]
        assert "default-widget" in names
        assert "user-widget" in names
