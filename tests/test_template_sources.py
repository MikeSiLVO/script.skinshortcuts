"""Names that resolve as template $PROPERTY sources."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.menu import load_menus
from skinshortcuts.loaders.template import load_templates

RESOLVES = {
    "label": "Movies",
    "label2": "Second",
    "icon": "i.png",
    "visible": "Library.HasContent(movies)",
    "action": "ActivateWindow(Videos,videodb://movies/)",
    "path": "videodb://movies/",
    "name": "movies",
    "menu": "mainmenu",
    "index": "1",
    "idprefix": "80",
    "id": "801",
    "submenuVisibility": "movies",
}

MENUS = """<menus><menu name="mainmenu" container="9000">
<item name="movies"><label>Movies</label><label2>Second</label2>
<icon>i.png</icon><thumb>t.png</thumb><visible>Library.HasContent(movies)</visible>
<action>ActivateWindow(Videos,videodb://movies/)</action></item></menu></menus>"""


def build(tmp_path: Path, sources: list[str]) -> dict[str, str]:
    """Build a template referencing each source, returning tag -> resolved text."""
    rows = "\n".join(f"<{s}>$PROPERTY[{s}]</{s}>" for s in sources)
    tpl = (
        f'<templates><template include="T" idprefix="80">'
        f'<controls><control type="group">{rows}</control></controls>'
        f"</template></templates>"
    )
    menus_path = tmp_path / "menus.xml"
    menus_path.write_text(MENUS, encoding="utf-8")
    tpl_path = tmp_path / "templates.xml"
    tpl_path.write_text(tpl, encoding="utf-8")

    menus = load_menus(str(menus_path))
    schema = load_templates(str(tpl_path))
    out = TemplateBuilder(schema, menus.menus, None).build()
    found: dict[str, str] = {}
    for control in out.iter("control"):
        for child in control:
            found[child.tag] = child.text or ""
    return found


@pytest.mark.parametrize(("source", "expected"), sorted(RESOLVES.items()))
def test_documented_source_resolves(tmp_path: Path, source: str, expected: str) -> None:
    assert build(tmp_path, [source]).get(source) == expected


def test_thumb_is_not_a_template_source(tmp_path: Path) -> None:
    # empty leaf elements are stripped; an unresolved source leaves no tag at all
    assert "thumb" not in build(tmp_path, ["thumb"])


def test_item_thumb_still_reaches_the_includes(tmp_path: Path) -> None:
    """An item's thumb reaches its menu include, though templates have no thumb source."""
    from skinshortcuts.builders.includes import IncludesBuilder

    menus_path = tmp_path / "menus.xml"
    menus_path.write_text(MENUS, encoding="utf-8")
    menus = load_menus(str(menus_path))
    root = IncludesBuilder(menus.menus).build()
    thumbs = [el.text for el in root.iter("thumb")]
    assert thumbs == ["t.png"]


def test_documented_sources_come_from_build_context() -> None:
    """Each documented source is assigned in _build_context."""
    root = Path(__file__).resolve().parents[1]
    source = root / "resources/lib/skinshortcuts/builders/template.py"
    body = source.read_text(encoding="utf-8").split("def _build_context")[1]
    body = body.split("def _build_variable")[0]
    missing = [key for key in RESOLVES if f'context["{key}"]' not in body]
    assert not missing, f"no longer set in _build_context: {missing}"
