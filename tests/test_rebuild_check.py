"""The rebuild check: stored hashes, the generated includes files, then the config."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts import hashing, userdata
from skinshortcuts.constants import INCLUDES_FILE


@pytest.fixture
def skin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    """Shortcuts and output folders with a built includes file; hashes and userdata kept beside."""
    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir()
    (shortcuts / "menus.xml").write_text('<menus><menu name="mainmenu"/></menus>', encoding="utf-8")
    output = tmp_path / "16x9"
    output.mkdir()
    (output / INCLUDES_FILE).write_text("<includes />", encoding="utf-8")
    monkeypatch.setattr(userdata, "get_userdata_path", lambda: str(tmp_path / "userdata.json"))
    monkeypatch.setattr(hashing, "get_hash_file_path", lambda: str(tmp_path / "hashes"))
    return shortcuts, output


def store(shortcuts: Path, output: Path) -> None:
    """Store hashes as a finished build does: the config plus the includes file."""
    hashes = hashing.generate_config_hashes(shortcuts)
    hashes[f"includes:{output}"] = hashing.hash_file(output / INCLUDES_FILE)
    assert hashing.write_hashes(hashes)


def test_nothing_stored_needs_a_rebuild(skin: tuple[Path, Path]) -> None:
    """With no stored hashes there is always a rebuild."""
    shortcuts, output = skin
    assert hashing.needs_rebuild(shortcuts, [str(output)])


def test_unchanged_build_needs_none(skin: tuple[Path, Path]) -> None:
    """Matching config and includes hashes mean no rebuild."""
    shortcuts, output = skin
    store(shortcuts, output)
    assert not hashing.needs_rebuild(shortcuts, [str(output)])


def test_missing_includes_file_needs_a_rebuild(skin: tuple[Path, Path]) -> None:
    """A deleted includes file is rebuilt even when the config is unchanged."""
    shortcuts, output = skin
    store(shortcuts, output)
    (output / INCLUDES_FILE).unlink()
    assert hashing.needs_rebuild(shortcuts, [str(output)])


def test_edited_includes_file_needs_a_rebuild(skin: tuple[Path, Path]) -> None:
    """An includes file changed since the build is rebuilt."""
    shortcuts, output = skin
    store(shortcuts, output)
    (output / INCLUDES_FILE).write_text("<includes><include /></includes>", encoding="utf-8")
    assert hashing.needs_rebuild(shortcuts, [str(output)])


def test_unreadable_stored_hashes_need_a_rebuild(skin: tuple[Path, Path], tmp_path: Path) -> None:
    """A damaged hashes file reads as nothing stored."""
    shortcuts, output = skin
    store(shortcuts, output)
    (tmp_path / "hashes").write_text("{not json", encoding="utf-8")
    assert hashing.read_stored_hashes() == {}
    assert hashing.needs_rebuild(shortcuts, [str(output)])
