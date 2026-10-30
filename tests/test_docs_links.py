"""Docs links resolve, and every skinner-facing doc is reachable from the index."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX = DOCS / "skinning" / "index.md"

# internal notes, not part of the skinner-facing set the index covers
EXCLUDED = {"codebase"}

PAGES = sorted(
    md for md in DOCS.rglob("*.md")
    if not EXCLUDED & set(md.relative_to(DOCS).parts)
)
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def anchors(doc: Path) -> set[str]:
    """GitHub-style heading slugs for a doc."""
    return {
        re.sub(r"[^a-z0-9\s-]", "", heading.lower()).strip().replace(" ", "-")
        for heading in re.findall(r"^#+\s+(.+)$", doc.read_text(encoding="utf-8"), re.M)
    }


@pytest.mark.parametrize("doc", PAGES, ids=lambda p: p.name)
def test_links_resolve(doc: Path) -> None:
    for label, target in LINK.findall(doc.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        path_part, _, anchor = target.partition("#")
        dest = (doc.parent / path_part).resolve() if path_part else doc
        assert dest.exists(), f"{doc.name}: {target} ({label}) points at nothing"
        if anchor:
            assert anchor in anchors(dest), f"{doc.name}: {target} ({label}) has no such heading"


def test_every_page_is_reachable_from_the_index() -> None:
    linked = {
        (INDEX.parent / target.partition("#")[0]).resolve()
        for _, target in LINK.findall(INDEX.read_text(encoding="utf-8"))
        if not target.startswith(("http://", "https://", "mailto:")) and target.partition("#")[0]
    }
    orphans = [p.relative_to(ROOT).as_posix() for p in PAGES
               if p.resolve() != INDEX.resolve() and p.resolve() not in linked]
    assert not orphans, f"not linked from skinning/index.md: {orphans}"
