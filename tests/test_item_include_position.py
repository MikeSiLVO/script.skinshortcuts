"""An item's include markers keep their place before or after its actions."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.loaders.menu import load_menus


def test_includes_keep_their_place_around_onclicks(tmp_path: Path) -> None:
    """A marker before the first action goes before the onclicks, one after it after them."""
    path = tmp_path / "menus.xml"
    path.write_text(
        '<menus><menu name="mainmenu"><item name="movies"><label>Movies</label>'
        '<skinshortcuts include="Before" /><action>ActivateWindow(Videos)</action>'
        '<skinshortcuts include="After" /></item></menu></menus>'
    )
    menu = load_menus(path).menus[0]
    elem = IncludesBuilder([menu])._build_item(menu.items[0], 1, menu)
    order = [(child.tag, child.text) for child in elem if child.tag in ("include", "onclick")]
    assert order == [
        ("include", "Before"), ("onclick", "ActivateWindow(Videos)"), ("include", "After")
    ]
