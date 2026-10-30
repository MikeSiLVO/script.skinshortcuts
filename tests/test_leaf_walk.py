"""Picker-tree walks: name lookups, duplicate warnings and migration targets agree."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.config import SkinConfig
from skinshortcuts.loaders.background import load_backgrounds
from skinshortcuts.loaders.widget import load_widgets
from skinshortcuts.migrations import apply_overrides
from skinshortcuts.models.property import PropertySchema
from skinshortcuts.userdata import MenuItemDiff, MenuDiff, UserData

WIDGETS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<widgets>
  <group name="g1" label="G1">
    <widget name="dup" label="Nested Dup"><path>nested://dup</path></widget>
    <group name="g2" label="G2">
      <widget name="deep" label="Deep"><path>deep://</path></widget>
    </group>
  </group>
  <widget name="top" label="Top"><path>top://</path></widget>
  <widget name="dup" label="Top Dup"><path>top://dup</path></widget>
  <content source="playlists" target="videos" />
  <overrides>
    <widget replace="old-deep">deep</widget>
  </overrides>
</widgets>
"""

BACKGROUNDS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
  <group name="bg1" label="BG1">
    <group name="bg2" label="BG2">
      <background name="deepbg" label="Deep BG"><path>deep.jpg</path></background>
    </group>
  </group>
  <background name="topbg" label="Top BG"><path>top.jpg</path></background>
</backgrounds>
"""

MENUS_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<menus><menu name="mainmenu"><item name="a"><label>A</label>'
    "<action>Noop</action></item></menu></menus>\n"
)


def _skin(tmp_path: Path) -> Path:
    """Write the test widgets, backgrounds and menus into the temp folder."""
    (tmp_path / "widgets.xml").write_text(WIDGETS_XML)
    (tmp_path / "backgrounds.xml").write_text(BACKGROUNDS_XML)
    (tmp_path / "menus.xml").write_text(MENUS_XML)
    return tmp_path


def test_get_widget_every_depth(tmp_path):
    config = SkinConfig.load(_skin(tmp_path), load_user=False)
    assert config.get_widget("top").path == "top://"
    assert config.get_widget("deep").path == "deep://"
    assert config.get_widget("missing") is None
    assert config.get_widget("g1") is None


def test_get_widget_duplicate_prefers_top_level(tmp_path):
    config = SkinConfig.load(_skin(tmp_path), load_user=False)
    assert config.get_widget("dup").path == "top://dup"


def test_get_background_every_depth(tmp_path):
    config = SkinConfig.load(_skin(tmp_path), load_user=False)
    assert config.get_background("topbg").path == "top.jpg"
    assert config.get_background("deepbg").path == "deep.jpg"
    assert config.get_background("bg2") is None


def test_duplicate_warning_sees_nested_and_top(tmp_path, monkeypatch):
    from skinshortcuts.loaders import base

    warned = []
    monkeypatch.setattr(base, "notify", lambda _h, _m, detail: warned.append(detail))
    load_widgets(_skin(tmp_path) / "widgets.xml")
    assert len(warned) == 1 and "'dup'" in warned[0]
    warned.clear()
    load_backgrounds(tmp_path / "backgrounds.xml")
    assert warned == []


def test_migration_reaches_nested_target(tmp_path):
    skin = _skin(tmp_path)
    widgets = load_widgets(skin / "widgets.xml")
    backgrounds = load_backgrounds(skin / "backgrounds.xml")
    userdata = UserData(menus={
        "mainmenu": MenuDiff(items=[
            MenuItemDiff(name="a", properties={"widget": "old-deep"}),
        ])
    })
    assert apply_overrides(userdata, PropertySchema(), widgets, backgrounds) > 0
    assert userdata.menus["mainmenu"].items[0].properties["widget"] == "deep"


def test_migration_known_matches_lookup_on_duplicates(tmp_path, monkeypatch):
    from skinshortcuts import migrations

    seen = {}
    real = migrations._usable

    def spy(override, kind, known):
        if kind == "widget":
            seen.update(known)
        return real(override, kind, known)

    monkeypatch.setattr(migrations, "_usable", spy)
    skin = _skin(tmp_path)
    apply_overrides(
        UserData(), PropertySchema(), load_widgets(skin / "widgets.xml"),
        load_backgrounds(skin / "backgrounds.xml"),
    )
    config = SkinConfig.load(skin, load_user=False)
    assert set(seen) == {"dup", "deep", "top"}
    assert seen["dup"] is not None and seen["dup"].path == config.get_widget("dup").path
