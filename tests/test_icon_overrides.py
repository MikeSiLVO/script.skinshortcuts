"""Tests for icon override parsing and application in the menu loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.loaders.menu import load_groupings, load_menus


def _write_menus(tmp_path: Path, body: str) -> Path:
    """Write a menus.xml around given XML and return its path."""
    menus_xml = tmp_path / "menus.xml"
    menus_xml.write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<menus>\n{body}\n</menus>\n')
    return menus_xml


def test_explicit_icon_override_parsed(tmp_path: Path):
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()
    path = _write_menus(
        tmp_path,
        f"""
        <icons>{icons_dir}/</icons>
        <overrides>
            <icons>
                <source>{icons_dir}/</source>
                <icon replace="DefaultFolder.png">files.png</icon>
            </icons>
        </overrides>
        <menu name="mainmenu"/>
        """,
    )

    config = load_menus(path)

    assert config.icon_overrides.get("DefaultFolder.png") == f"{icons_dir}/files.png"


def test_convention_scan_picks_up_default_named_files(tmp_path: Path):
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()
    (icons_dir / "DefaultMovies.png").write_bytes(b"")
    (icons_dir / "DefaultTVShows.png").write_bytes(b"")
    (icons_dir / "unrelated.png").write_bytes(b"")

    path = _write_menus(
        tmp_path,
        f"""
        <overrides>
            <icons>
                <source>{icons_dir}/</source>
            </icons>
        </overrides>
        <menu name="mainmenu"/>
        """,
    )

    config = load_menus(path)

    assert config.icon_overrides.get("DefaultMovies.png") == f"{icons_dir}/DefaultMovies.png"
    assert config.icon_overrides.get("DefaultTVShows.png") == f"{icons_dir}/DefaultTVShows.png"
    assert "unrelated.png" not in config.icon_overrides


def test_explicit_wins_over_convention(tmp_path: Path):
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()
    (icons_dir / "DefaultFolder.png").write_bytes(b"")

    path = _write_menus(
        tmp_path,
        f"""
        <overrides>
            <icons>
                <source>{icons_dir}/</source>
                <icon replace="DefaultFolder.png">my-files.png</icon>
            </icons>
        </overrides>
        <menu name="mainmenu"/>
        """,
    )

    config = load_menus(path)

    assert config.icon_overrides["DefaultFolder.png"] == f"{icons_dir}/my-files.png"


def test_override_block_without_source_skips_convention_scan(tmp_path: Path):
    """Root <icons> is NOT reused as override source; skinner must opt in explicitly."""
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()
    (icons_dir / "DefaultFolder.png").write_bytes(b"")

    path = _write_menus(
        tmp_path,
        f"""
        <icons>{icons_dir}/</icons>
        <overrides>
            <icons>
                <icon replace="DefaultMovies.png">special://skin/movies.png</icon>
            </icons>
        </overrides>
        <menu name="mainmenu"/>
        """,
    )

    config = load_menus(path)

    assert "DefaultFolder.png" not in config.icon_overrides
    assert config.icon_overrides["DefaultMovies.png"] == "special://skin/movies.png"


def test_relative_override_without_source_is_dropped(tmp_path: Path):
    """No <source> means no base path; relative override values get logged and skipped."""
    path = _write_menus(
        tmp_path,
        """
        <overrides>
            <icons>
                <icon replace="DefaultFolder.png">files.png</icon>
            </icons>
        </overrides>
        <menu name="mainmenu"/>
        """,
    )

    config = load_menus(path)

    assert "DefaultFolder.png" not in config.icon_overrides


def test_absolute_replacement_path_kept_as_is(tmp_path: Path):
    path = _write_menus(
        tmp_path,
        """
        <overrides>
            <icons>
                <icon replace="DefaultFolder.png">special://skin/extras/icons/files.png</icon>
            </icons>
        </overrides>
        <menu name="mainmenu"/>
        """,
    )

    config = load_menus(path)

    assert config.icon_overrides["DefaultFolder.png"] == "special://skin/extras/icons/files.png"


@pytest.mark.xfail(strict=True, reason="Shortcut groupings ignore the skin's icon overrides")
def test_shortcut_icon_falls_back_to_override(tmp_path: Path):
    """A shortcut with no icon gets the default icon's override; an explicit one stays literal."""
    icons_dir = tmp_path / "icons"
    icons_dir.mkdir()
    (icons_dir / "DefaultShortcut.png").write_bytes(b"")

    path = _write_menus(
        tmp_path,
        f"""
        <icons>{icons_dir}/</icons>
        <overrides>
            <icons>
                <source>{icons_dir}/</source>
            </icons>
        </overrides>
        <groupings>
            <group name="common" label="Common">
                <shortcut name="no-icon-shortcut" label="X">
                    <action>noop</action>
                </shortcut>
                <shortcut name="explicit-shortcut" label="Y" icon="DefaultShortcut.png">
                    <action>noop</action>
                </shortcut>
            </group>
        </groupings>
        <menu name="mainmenu"/>
        """,
    )

    group = load_groupings(path)[0]
    assert hasattr(group, "items")
    items = group.items  # type: ignore[union-attr]

    assert items[0].icon == f"{icons_dir}/DefaultShortcut.png"
    assert items[1].icon == "DefaultShortcut.png"
