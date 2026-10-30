"""Widget and background sibling keys: dialog set/clear and build derivation agree."""

from __future__ import annotations

from skinshortcuts import constants
from skinshortcuts.config import SkinConfig
from skinshortcuts.dialog.properties import PropertiesMixin
from skinshortcuts.models.background import Background, BackgroundType
from skinshortcuts.models.menu import MenuItem
from skinshortcuts.models.widget import Widget

WIDGET_PARTS = constants.WIDGET_SIBLINGS + constants.WIDGET_EXTRAS

FULL_WIDGET = Widget(
    name="w", label="W", path="plugin://x/{menuitem}", type="movies", target="videos",
    source="library", limit=10, sort_by="title", sort_order="ascending",
)
FULL_BG = Background(name="b", label="B", path="b.jpg", type=BackgroundType.STATIC)


class _Recorder(PropertiesMixin):
    """PropertiesMixin that records each property write with its related keys."""

    def __init__(self):
        self.manager = None
        self.menu_id = "mainmenu"
        self.calls: list[tuple[str, str, dict]] = []

    def _log(self, msg):
        pass

    def _set_item_property(self, item, name, value, related=None, apply_suffix=True):
        self.calls.append((name, value, dict(related or {})))


def _keys(base: str, parts, tail: str = "") -> set[str]:
    """Sibling keys built from a base, each part and an optional slot suffix."""
    return {f"{base}{p}{tail}" for p in parts}


def test_dialog_widget_set_and_clear_cover_every_part():
    rec = _Recorder()
    item = MenuItem(name="movies", label="Movies")
    rec._set_widget_properties(item, "widget.2", FULL_WIDGET)
    rec._clear_widget_properties(item, "widget.2")
    (_, value, set_related), (_, cleared, clear_related) = rec.calls
    assert value == "w" and cleared == ""
    assert set(set_related) == _keys("widget", WIDGET_PARTS, ".2")
    assert set(clear_related) == _keys("widget", WIDGET_PARTS, ".2")
    assert all(v is None for v in clear_related.values())
    assert set_related["widgetPath.2"] == "plugin://x/movies"
    assert set_related["widgetLimit.2"] == "10"


def test_dialog_background_set_and_clear():
    rec = _Recorder()
    item = MenuItem(name="movies", label="Movies")
    rec._set_background_properties(item, "background", FULL_BG)
    rec._set_background_properties_custom(item, "background", FULL_BG, "c.jpg", None, "movies")
    rec._clear_background_properties(item, "background")
    set_related, custom_related, clear_related = (c[2] for c in rec.calls)
    all_bg = _keys("background", constants.BACKGROUND_SIBLINGS)
    assert set(set_related) == all_bg
    assert set_related["backgroundPlaylistType"] is None
    assert set(custom_related) == all_bg
    assert set(clear_related) == all_bg


def test_build_derives_same_keys(tmp_path):
    (tmp_path / "menus.xml").write_text(
        '<?xml version="1.0"?><menus><menu name="m"><item name="i"><label>I</label>'
        "<action>Noop</action></item></menu></menus>"
    )
    config = SkinConfig.load(tmp_path, load_user=False)
    config.get_widget = lambda n: FULL_WIDGET
    config.get_background = lambda n: FULL_BG
    item = MenuItem(name="movies", label="M", properties={"widget.3": "w", "background": "b"})
    derived = config.derived_item_properties(item)
    assert {k for k in derived if k.startswith("widget")} == _keys("widget", WIDGET_PARTS, ".3")
    assert {k for k in derived if k.startswith("background")} == _keys(
        "background", constants.BACKGROUND_SIBLINGS
    ) - {"backgroundPlaylistType"}
