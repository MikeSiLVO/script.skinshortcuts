"""Library field shortcuts open Kodi's own videodb nodes, which are keyed by id, never by name."""

from __future__ import annotations

import re

import pytest

from skinshortcuts.models.menu import Content
from skinshortcuts.providers.content import ContentProvider

ITEM = {
    "cast": [{"name": "Tom Hanks", "thumbnail": ""}],
    "studio": ["20th Century Fox"],
    "tag": ["high school"],
    "director": ["Steven Spielberg"],
}

NODES = {
    "videodb://movies/actors/": ("videodb://movies/actors/455/", "Tom Hanks"),
    "videodb://movies/studios/": ("videodb://movies/studios/5/", "20th Century Fox"),
    "videodb://movies/tags/": ("videodb://movies/tags/1/", "high school"),
    "videodb://movies/directors/": ("videodb://movies/directors/12/", "Steven Spielberg"),
    "videodb://tvshows/actors/": ("videodb://tvshows/actors/455/", "Tom Hanks"),
    "videodb://tvshows/studios/": ("videodb://tvshows/studios/5/", "20th Century Fox"),
    "videodb://tvshows/tags/": ("videodb://tvshows/tags/1/", "high school"),
}


def library_rpc(method: str, params: dict | None = None) -> dict:
    """Answer the library queries the way live Kodi does, one entry per kind."""
    if method == "Files.GetDirectory":
        node = NODES.get((params or {}).get("directory", ""))
        if not node:
            return {"files": None}
        file, label = node
        return {"files": [{"file": file, "label": label, "filetype": "directory"}]}
    if method == "VideoLibrary.GetGenres":
        return {"genres": [{"genreid": 3, "label": "Drama", "thumbnail": ""}]}
    key = {
        "VideoLibrary.GetMovies": "movies",
        "VideoLibrary.GetTVShows": "tvshows",
        "VideoLibrary.GetEpisodes": "episodes",
    }.get(method)
    return {key: [dict(ITEM)]} if key else {}


def resolve(monkeypatch: pytest.MonkeyPatch, target: str) -> list[str]:
    """Actions the library source resolves."""
    provider = ContentProvider()
    monkeypatch.setattr(provider, "_jsonrpc", library_rpc)
    return [s.action for s in provider.resolve(Content(source="library", target=target))]


def test_genres_open_by_id(monkeypatch: pytest.MonkeyPatch) -> None:
    assert resolve(monkeypatch, "genres") == [
        "ActivateWindow(videos,videodb://movies/genres/3/,return)"
    ]


@pytest.mark.parametrize(
    ("target", "node"),
    [
        ("actors", "movies/actors"),
        ("studios", "movies/studios"),
        ("tags", "movies/tags"),
        ("directors", "movies/directors"),
        ("tvactors", "tvshows/actors"),
        ("tvstudios", "tvshows/studios"),
        ("tvtags", "tvshows/tags"),
    ],
)
def test_field_values_open_by_id(monkeypatch: pytest.MonkeyPatch, target: str, node: str) -> None:
    actions = resolve(monkeypatch, target)
    pattern = rf'ActivateWindow\(Videos,"?videodb://{node}/\d+/"?,return\)'
    assert actions
    assert all(re.fullmatch(pattern, action) for action in actions), actions


def test_tv_directors_target_is_gone(monkeypatch: pytest.MonkeyPatch) -> None:
    assert resolve(monkeypatch, "tvdirectors") == []
