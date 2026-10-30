"""A template condition reads item properties only; property conditions also see the built-ins."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import Menu, MenuItem

TEMPLATES = """<templates>
  <template include="ByCondition">
    <condition>name=movies</condition>
    <controls><control type="button"><label>$PROPERTY[name]</label></control></controls>
  </template>
  <template include="ByProperty">
    <property name="tag" condition="name=movies">hit</property>
    <controls><control type="button"><label>$PROPERTY[tag]</label></control></controls>
  </template>
</templates>"""


@pytest.fixture
def builder(tmp_path: Path) -> TemplateBuilder:
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES, encoding="utf-8")
    menu = Menu(name="mainmenu", items=[MenuItem(name="movies", label="Movies")])
    return TemplateBuilder(load_templates(path), [menu])


def labels(builder: TemplateBuilder, include: str) -> list[str]:
    """Button labels built by the template include of a given name."""
    found = builder.build().find(f"include[@name='skinshortcuts-template-{include}']")
    assert found is not None
    return [b.findtext("label") or "" for b in found.iter("control")]


def test_property_condition_sees_builtins(builder: TemplateBuilder) -> None:
    assert labels(builder, "ByProperty") == ["hit"]


@pytest.mark.xfail(strict=True, reason="not a bug: built-ins are not condition targets")
def test_template_condition_sees_builtins(builder: TemplateBuilder) -> None:
    assert labels(builder, "ByCondition") == ["movies"]
