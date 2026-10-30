"""A real skin's override block resolves against the icons the skin ships."""
from __future__ import annotations

from pathlib import Path

import pytest

SKIN = Path(__file__).parent / "fixtures" / "skins" / "skin.arctic.zephyr.martian"
MENUS = SKIN / "shortcuts" / "menus.xml"
ICON_DIR = "special://skin/extras/icons/"
ICONS = set((SKIN / "icons.txt").read_text(encoding="utf-8").split())


def _has(path: str) -> bool:
    """Whether the skin's extras/icons folder holds this file, per the saved file list."""
    return path.startswith(ICON_DIR) and path[len(ICON_DIR):] in ICONS


@pytest.fixture
def martian(monkeypatch):
    import xbmc
    import xbmcvfs
    monkeypatch.setattr(xbmcvfs, "exists", _has, raising=False)
    monkeypatch.setattr(xbmc, "skinHasImage", _has, raising=False)
    from skinshortcuts.loaders.menu import load_menus
    return load_menus(MENUS).icon_overrides


def test_explicit_entries_resolve_against_the_source(martian):
    assert martian.get("DefaultShortcut.png") == "special://skin/extras/icons/shortcut.png"
    assert martian.get("DefaultMovies.png") == "special://skin/extras/icons/film.png"
    assert martian.get("UnknownUser.png") == "special://skin/extras/icons/actor.png"


def test_convention_still_covers_unlisted_defaults(martian):
    found = sorted(n for n in ICONS if n.startswith("Default") and n.endswith(".png"))
    for name in found:
        assert martian.get(name), f"{name} present in the folder but no override"


def test_names_the_skin_does_not_have_get_nothing(martian):
    assert martian.get("DefaultNotAThing.png") == ""
    assert "DefaultNotAThing.png" not in martian
