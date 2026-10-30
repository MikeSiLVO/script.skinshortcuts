"""Background groups pass icon overrides down, and a content element is skipped with a warning."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.loaders.background import load_backgrounds
from skinshortcuts.log import Logger
from skinshortcuts.models.background import Background, BackgroundGroup
from skinshortcuts.models.menu import Content, IconOverrides

OVERRIDES = IconOverrides(explicit={"DefaultPlaylist.png": "special://skin/playlist.png"})


def playlist(name: str) -> str:
    """A playlist background with one source and no explicit source icon."""
    return (
        f'<background name="{name}" label="{name}" type="playlist">'
        "<source label='Video'>special://videoplaylists/</source></background>"
    )


GROUPED = f"""<backgrounds>
  {playlist("top")}
  <group name="outer" label="Outer">
    {playlist("grouped")}
    <group name="inner" label="Inner">
      {playlist("nested")}
    </group>
  </group>
</backgrounds>"""

CONTENT = """<backgrounds>
  <content source="playlists" target="videos" />
  <group name="library" label="Library">
    <background name="a" label="A"><path>special://skin/a.jpg</path></background>
    <content source="playlists" target="videos" />
  </group>
</backgrounds>"""


@pytest.fixture
def warned(monkeypatch) -> list[str]:
    captured: list[str] = []
    monkeypatch.setattr(Logger, "warning", lambda _self, msg: captured.append(msg))
    return captured


def source_icons(tmp_path: Path) -> dict[str, str]:
    """Source icon per background name, nested groups included."""
    path = tmp_path / "backgrounds.xml"
    path.write_text(GROUPED, encoding="utf-8")
    config = load_backgrounds(path, icon_overrides=OVERRIDES)

    icons: dict[str, str] = {}

    def walk(items: list) -> None:
        for item in items:
            if isinstance(item, BackgroundGroup):
                walk(item.items)
            elif isinstance(item, Background):
                icons[item.name] = item.sources[0].icon

    walk(config.groupings)
    return icons


def test_top_level_background_takes_the_override(tmp_path: Path) -> None:
    assert source_icons(tmp_path)["top"] == "special://skin/playlist.png"


@pytest.mark.parametrize("name", ["grouped", "nested"])
def test_grouped_background_takes_the_override(tmp_path: Path, name: str) -> None:
    assert source_icons(tmp_path)[name] == "special://skin/playlist.png"


def test_content_is_skipped_with_a_warning(tmp_path: Path, warned: list[str]) -> None:
    path = tmp_path / "backgrounds.xml"
    path.write_text(CONTENT, encoding="utf-8")
    config = load_backgrounds(path)

    group = config.groupings[0]
    assert isinstance(group, BackgroundGroup)
    assert [type(item) for item in group.items] == [Background]
    assert not any(isinstance(item, Content) for item in group.items)
    assert len([msg for msg in warned if "content" in msg]) == 2
