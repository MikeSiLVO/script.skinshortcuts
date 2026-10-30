"""A named expression expands as one bracketed term."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import MenuItem

TEMPLATES = """<templates>
  <expressions>
    <expression name="landscape">widgetArt=FanArt | Landscape | ClearArt</expression>
    <expression name="hasWidget">widgetPath</expression>
    <expression name="global" nosuffix="true">homeToggle</expression>
    <expression name="blank"></expression>
  </expressions>
  <presets>
    <preset name="dimensions">
      <values condition="suffix=.2 + $EXP[landscape]" top="117" />
      <values condition="suffix=.2" top="112" />
      <values condition="$EXP[landscape]" top="429" />
      <values top="424" />
    </preset>
  </presets>
</templates>"""


@pytest.fixture
def builder(tmp_path: Path) -> TemplateBuilder:
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES, encoding="utf-8")
    return TemplateBuilder(load_templates(path), [])


def item(**properties: str) -> MenuItem:
    """Movies menu item holding given properties."""
    return MenuItem(name="movies", label="Movies", properties=properties)


def top(builder: TemplateBuilder, menu_item: MenuItem, suffix: str) -> str:
    """Top value of the dimensions preset row that wins, picked as the build does."""
    preset = builder.schema.get_preset("dimensions")
    values = builder._get_preset_values(preset, menu_item, {"suffix": suffix}, suffix)
    return (values or {}).get("top", "")


def test_expression_is_stored_bracketed(builder: TemplateBuilder) -> None:
    expr = builder.schema.get_expression("landscape")
    assert expr is not None
    assert expr.value == "[widgetArt=FanArt | Landscape | ClearArt]"


def test_empty_expression_stays_empty(builder: TemplateBuilder) -> None:
    expr = builder.schema.get_expression("blank")
    assert expr is not None
    assert expr.value == ""


def test_suffixed_row_does_not_match_the_unsuffixed_widget(builder: TemplateBuilder) -> None:
    assert top(builder, item(widgetArt="ClearArt"), "") == "429"


def test_suffixed_row_matches_its_own_widget(builder: TemplateBuilder) -> None:
    assert top(builder, item(**{"widgetArt.2": "ClearArt"}), ".2") == "117"


def test_suffixed_widget_falls_through_on_a_miss(builder: TemplateBuilder) -> None:
    assert top(builder, item(**{"widgetArt.2": "Poster"}), ".2") == "112"


@pytest.mark.parametrize("art", ["FanArt", "Landscape", "ClearArt"])
def test_compact_values_still_cascade_inside_the_bracket(
    builder: TemplateBuilder, art: str
) -> None:
    assert builder._eval_condition("$EXP[landscape]", item(widgetArt=art), {}) is True


def test_unlisted_value_does_not_match(builder: TemplateBuilder) -> None:
    assert builder._eval_condition("$EXP[landscape]", item(widgetArt="Poster"), {}) is False


@pytest.mark.parametrize(
    ("art", "want"),
    [("ClearArt", False), ("Poster", True)],
)
def test_negation_applies_to_the_whole_expression(
    builder: TemplateBuilder, art: str, want: bool
) -> None:
    assert builder._eval_condition("!$EXP[landscape]", item(widgetArt=art), {}) is want


def test_single_term_expression_still_resolves(builder: TemplateBuilder) -> None:
    assert builder._check_conditions(["$EXP[hasWidget]"], item(widgetPath="plugin://x")) is True
    assert builder._check_conditions(["$EXP[hasWidget]"], item()) is False


def test_nosuffix_survives_the_bracket(builder: TemplateBuilder) -> None:
    assert builder._check_conditions(["$EXP[global]"], item(homeToggle="1"), ".2") is True
