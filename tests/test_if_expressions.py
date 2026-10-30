"""$IF clauses: bracketed text inside them, and THEN/ELIF/ELSE inside user values."""

from __future__ import annotations

from pathlib import Path

import pytest

import skinshortcuts.expressions as expressions
from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.expressions import evaluate_if
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import MenuItem

TEMPLATES = """<templates>
  <expressions>
    <expression name="isMovies">widgetType=movies</expression>
  </expressions>
</templates>"""

PLAYLIST = "special://profile/playlists/video/Something Else.xsp"


@pytest.fixture
def builder(tmp_path: Path) -> TemplateBuilder:
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES, encoding="utf-8")
    return TemplateBuilder(load_templates(path), [])


def substitute(builder: TemplateBuilder, text: str, **properties: str) -> str:
    """Substitute template text for a movies item holding given properties."""
    item = MenuItem(name="movies", label="Movies", properties=properties)
    return builder._substitute_text(text, dict(properties), item)


def test_documented_nesting_resolves(builder: TemplateBuilder) -> None:
    text = "$IF[useCustom THEN $PROPERTY[customPath] ELSE $PROPERTY[defaultPath]]"
    assert substitute(builder, text, useCustom="true", customPath="a", defaultPath="b") == "a"


@pytest.mark.xfail(strict=True, reason="won't fix: $IF ends at the first ] in its text")
@pytest.mark.parametrize(
    ("text", "want"),
    [
        ("$IF[widgetType=movies THEN $PROPERTY[lbl] ELSE x]", "$LOCALIZE[342]"),
        ("$IF[widgetType=movies THEN $INFO[ListItem.Label] ELSE x]", "$INFO[ListItem.Label]"),
        ("$IF[$EXP[isMovies] THEN a ELSE b]", "a"),
        ("$IF[[widgetType=movies | widgetType=tvshows] + widgetArt=Poster THEN a ELSE b]", "a"),
    ],
)
def test_brackets_inside_if(builder: TemplateBuilder, text: str, want: str) -> None:
    properties = {"widgetType": "movies", "widgetArt": "Poster", "lbl": "$LOCALIZE[342]"}
    assert substitute(builder, text, **properties) == want


def test_uppercase_keywords_still_split() -> None:
    expr = "a=1 THEN x ELIF a=2 THEN y ELSE z"
    assert [evaluate_if(expr, {"a": a}) for a in ("1", "2", "3")] == ["x", "y", "z"]


@pytest.mark.parametrize(
    ("expr", "properties", "want"),
    [
        ("a=1 THEN Something Else here ELSE z", {"a": "1"}, "Something Else here"),
        ("label=Then and Now THEN x ELSE y", {"label": "Then and Now"}, "x"),
        ("a=1 THEN Pick elif skip ELSE z", {"a": "1"}, "Pick elif skip"),
    ],
)
def test_lowercase_words_in_values_are_not_keywords(
    expr: str, properties: dict[str, str], want: str
) -> None:
    assert evaluate_if(expr, properties) == want


def test_property_value_with_else_survives(builder: TemplateBuilder) -> None:
    text = "$IF[widgetPath THEN $PROPERTY[widgetPath] ELSE none]"
    assert substitute(builder, text, widgetPath=PLAYLIST) == PLAYLIST


@pytest.mark.parametrize("expr", ["a", "a=1 THNE x ELSE y", "a=1 THEN x ELIF b"])
def test_clause_without_then_is_reported(monkeypatch: pytest.MonkeyPatch, expr: str) -> None:
    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(expressions, "notify", lambda *args: calls.append(args))
    evaluate_if(expr, {"a": "1"})
    assert calls
