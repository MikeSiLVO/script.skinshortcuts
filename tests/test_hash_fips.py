"""Rebuild hashing works on a Python built for FIPS, where plain md5 is refused."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from skinshortcuts import hashing

REAL_MD5 = hashlib.md5


def fips_md5(*args: object, usedforsecurity: bool = True) -> object:
    """MD5 as a FIPS build offers it: only when declared not for security."""
    if usedforsecurity:
        raise ValueError("[digital envelope routines] unsupported")
    return REAL_MD5(*args, usedforsecurity=False)  # type: ignore[arg-type]


def test_hash_file_on_fips(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "menus.xml"
    path.write_text("<menus />", encoding="utf-8")
    monkeypatch.setattr(hashing.hashlib, "md5", fips_md5)
    assert hashing.hash_file(path) == REAL_MD5(b"<menus />").hexdigest()
