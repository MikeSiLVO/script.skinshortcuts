"""Precedence of same-named declarations: first match wins within a list, across lists it varies."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import Menu, MenuItem

TEMPLATES = """<templates>
  <presets>
    <preset name="sizes"><values aspect="preset" /></preset>
  </presets>
  <propertyGroups>
    <propertyGroup name="twoFroms">
      <property name="aspect" from="first" />
      <property name="aspect" from="second" />
    </propertyGroup>
    <propertyGroup name="literalThenFrom">
      <property name="aspect">literal</property>
      <property name="aspect" from="second" />
    </propertyGroup>
    <propertyGroup name="fromThenLiteral">
      <property name="aspect" from="first" />
      <property name="aspect">literal</property>
    </propertyGroup>
    <propertyGroup name="fromOnly"><property name="aspect" from="first" /></propertyGroup>
    <propertyGroup name="literalOnly"><property name="aspect">literal</property></propertyGroup>
    <propertyGroup name="twoVars">
      <var name="aspect"><value>first var</value></var>
      <var name="aspect"><value>second var</value></var>
    </propertyGroup>
  </propertyGroups>
  <template include="twoProperties">
    <property name="aspect" from="first" />
    <property name="aspect" from="second" />
  </template>
  <template include="templateLiteral"><property name="aspect">literal</property></template>
  <template include="twoVars">
    <var name="aspect"><value>first var</value></var>
    <var name="aspect"><value>second var</value></var>
  </template>
  <template include="preset"><preset content="sizes" /></template>
  <template include="twoFroms"><propertyGroup content="twoFroms" /></template>
  <template include="literalThenFrom"><propertyGroup content="literalThenFrom" /></template>
  <template include="fromThenLiteral"><propertyGroup content="fromThenLiteral" /></template>
  <template include="fromOnly"><propertyGroup content="fromOnly" /></template>
  <template include="literalOnly"><propertyGroup content="literalOnly" /></template>
  <template include="groupVars"><propertyGroup content="twoVars" /></template>
  <template include="propertyThenVar">
    <property name="aspect" condition="kind=a">branch a</property>
    <property name="aspect">branch b</property>
    <var name="aspect"><value>var</value></var>
  </template>
  <template include="varThenProperty">
    <var name="aspect"><value>var</value></var>
    <property name="aspect">property</property>
  </template>
</templates>"""


@pytest.fixture
def notified(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Headings and messages the loader notifies."""
    seen: list[str] = []
    monkeypatch.setattr(
        "skinshortcuts.loaders.template.notify", lambda h, m, *_: seen.append(f"{h}: {m}")
    )
    return seen


@pytest.fixture
def builder(tmp_path: Path, notified: list[str]) -> TemplateBuilder:
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES, encoding="utf-8")
    return TemplateBuilder(load_templates(path), [])


def aspect(builder: TemplateBuilder, include: str, **properties: str) -> str:
    """Aspect a template resolves for a movies item holding given values."""
    template = next(t for t in builder.schema.templates if t.include == include)
    item = MenuItem(name="movies", label="Movies", properties=properties)
    menu = Menu(name="mainmenu", items=[item])
    context = builder._build_context(template, template.get_outputs()[0], item, 1, menu)
    return context.get("aspect", "")


SOURCES = {"first": "from first", "second": "from second"}


def test_template_properties_first_match_wins(builder: TemplateBuilder) -> None:
    assert aspect(builder, "twoProperties", **SOURCES) == "from first"


def test_template_literal_overwrites_the_item(builder: TemplateBuilder) -> None:
    assert aspect(builder, "templateLiteral", aspect="item") == "literal"


def test_group_from_overwrites_the_item(builder: TemplateBuilder) -> None:
    assert aspect(builder, "fromOnly", aspect="item", first="from first") == "from first"


def test_group_literal_only_fills_an_unset_name(builder: TemplateBuilder) -> None:
    assert aspect(builder, "literalOnly", aspect="item") == "item"
    assert aspect(builder, "literalOnly") == "literal"


def test_preset_only_fills_an_unset_name(builder: TemplateBuilder) -> None:
    assert aspect(builder, "preset", aspect="item") == "item"
    assert aspect(builder, "preset") == "preset"


def test_group_literal_before_a_from_keeps_first_place(builder: TemplateBuilder) -> None:
    assert aspect(builder, "fromThenLiteral", **SOURCES) == "from first"


@pytest.mark.parametrize(
    ("include", "want"),
    [("twoFroms", "from first"), ("literalThenFrom", "literal")],
)
def test_group_first_match_wins(builder: TemplateBuilder, include: str, want: str) -> None:
    assert aspect(builder, include, **SOURCES) == want


@pytest.mark.parametrize("include", ["twoVars", "groupVars"])
def test_same_named_vars_first_match_wins(builder: TemplateBuilder, include: str) -> None:
    assert aspect(builder, include) == "first var"


def test_group_literal_that_keeps_the_item_still_wins_first_place(builder: TemplateBuilder) -> None:
    assert aspect(builder, "literalThenFrom", aspect="item", second="from second") == "item"


@pytest.mark.parametrize(
    ("include", "want"),
    [("propertyThenVar", "branch b"), ("varThenProperty", "var")],
)
def test_first_definition_wins_a_clash(builder: TemplateBuilder, include: str, want: str) -> None:
    assert aspect(builder, include) == want


def test_every_clash_is_reported(builder: TemplateBuilder, notified: list[str]) -> None:
    """Two vars in a group, two in a template, then property-var and var-property."""
    assert notified == ["Template Error: 'aspect' defined twice"] * 4
