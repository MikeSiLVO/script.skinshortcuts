"""Built-in names and nosuffix expressions stay unsuffixed whatever their case or nesting."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.conditions import suffix_condition, suffix_property
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import MenuItem

TEMPLATES = """<templates>
  <expressions>
    <expression name="global" nosuffix="true">homeToggle</expression>
    <expression name="globalMovies" nosuffix="true">$EXP[global] + widgetType=movies</expression>
  </expressions>
</templates>"""


@pytest.fixture
def builder(tmp_path: Path) -> TemplateBuilder:
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES, encoding="utf-8")
    return TemplateBuilder(load_templates(path), [])


def test_lowercase_builtins_escape_the_suffix() -> None:
    assert suffix_condition("name=movies", ".2") == "name=movies"
    assert suffix_property("index", ".2") == "index"


def test_builtin_condition_escapes_the_suffix_in_any_case() -> None:
    assert suffix_condition("Name=movies", ".2") == "Name=movies"


def test_builtin_from_escapes_the_suffix_in_any_case() -> None:
    assert suffix_property("Index", ".2") == "Index"


def test_builtin_iterate_ref_escapes_the_suffix_in_any_case() -> None:
    text = TemplateBuilder._apply_iterate_to_text("$PROPERTY[ID]", ".2", 2, "slot")
    assert text == "$PROPERTY[ID]"


@pytest.mark.parametrize("suffix", ["", ".2"])
def test_single_nosuffix_expression(builder: TemplateBuilder, suffix: str) -> None:
    item = MenuItem(name="movies", label="Movies", properties={"homeToggle": "1"})
    assert builder._check_conditions(["$EXP[global]"], item, suffix) is True


@pytest.mark.parametrize("suffix", ["", ".2"])
def test_nested_nosuffix_expression(builder: TemplateBuilder, suffix: str) -> None:
    properties = {"homeToggle": "1", "widgetType": "movies"}
    item = MenuItem(name="movies", label="Movies", properties=properties)
    assert builder._check_conditions(["$EXP[globalMovies]"], item, suffix) is True
