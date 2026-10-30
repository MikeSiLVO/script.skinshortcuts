"""Submenu templates: what they honor, what they ignore, and the warning for what they ignore."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import Menu, MenuItem

TEMPLATES = ("""<templates>
  <expressions>
    <expression name="isMovies">name=movies</expression>
  </expressions>
  <propertyGroups>
    <propertyGroup name="Extra"><property name="grouped">from-group</property></propertyGroup>
  </propertyGroups>
  <template items="rows" filter="kind=keep">
    <controls><control type="button"><label>$PROPERTY[name]</label></control></controls>
  </template>
  <submenu include="Sub" level="1">
    <property name="plain">kept</property>
    <property name="gated" condition="name=music">SHOULD-NOT-APPEAR</property>
    <propertyGroup content="Extra" />
    <var name="viaExp"><value condition="$EXP[isMovies]">yes</value></var>
    <controls>
      <control type="list">
        <description>$PROPERTY[plain]|$PROPERTY[gated]|"""
    """$PROPERTY[grouped]|$PROPERTY[viaExp]</description>
        <label>$IF[name=movies THEN yes ELSE no]</label>
        <label2>$PARENT[name]</label2>
        <skinshortcuts insert="rows" />
      </control>
    </controls>
  </submenu>
</templates>""")


@pytest.fixture
def built(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[ET.Element, list[str]]:
    """The Sub include built over mainmenu/movies, and the notifications fired."""
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES, encoding="utf-8")
    notified: list[str] = []
    for module in ("builders", "loaders"):
        monkeypatch.setattr(
            f"skinshortcuts.{module}.template.notify",
            lambda h, m, *_: notified.append(f"{h}: {m}"),
        )
    main = Menu(name="mainmenu", items=[MenuItem(name="movies", label="Movies")])
    sub_items = [
        MenuItem(name="keep", label="Keep", properties={"kind": "keep"}),
        MenuItem(name="drop", label="Drop", properties={"kind": "drop"}),
    ]
    sub = Menu(name="mainmenu/movies", items=sub_items, is_submenu=True)
    root = TemplateBuilder(load_templates(path), [main, sub]).build()
    include = root.find("include[@name='skinshortcuts-Sub']")
    assert include is not None
    return include, notified


def values(include: ET.Element) -> list[str]:
    """The four property values the description joins."""
    return (include.findtext("control/description") or "").split("|")


def test_literal_property_applies(built: tuple[ET.Element, list[str]]) -> None:
    assert values(built[0])[0] == "kept"


def test_property_condition_is_honored(built: tuple[ET.Element, list[str]]) -> None:
    assert values(built[0])[1] == ""


@pytest.mark.parametrize("feature", ["<propertyGroup>", "$IF", "$PARENT"])
def test_unsupported_feature_is_reported(built: tuple[ET.Element, list[str]], feature: str) -> None:
    assert f"Submenu Template Error: 'Sub' uses {feature}" in built[1]


def test_include_marker_and_items_variable_groups_are_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "templates.xml"
    path.write_text("""<templates>
  <includes><include name="Shared"><control type="image" /></include></includes>
  <variables>
    <variable name="v"><value>x</value></variable>
    <variableGroup name="g"><variable content="v" /></variableGroup>
  </variables>
  <template items="rows">
    <variableGroup content="g" />
    <controls><control type="button"><label>$PROPERTY[name]</label></control></controls>
  </template>
  <submenu include="Sub" level="1">
    <controls>
      <control type="group"><skinshortcuts include="Shared" />"""
      """<skinshortcuts insert="rows" /></control>
    </controls>
  </submenu>
</templates>""", encoding="utf-8")
    notified: list[str] = []
    for module in ("builders", "loaders"):
        monkeypatch.setattr(
            f"skinshortcuts.{module}.template.notify",
            lambda h, m, *_: notified.append(f"{h}: {m}"),
        )
    main = Menu(name="mainmenu", items=[MenuItem(name="movies", label="Movies")])
    sub = Menu(name="mainmenu/movies", items=[MenuItem(name="a", label="A")], is_submenu=True)
    root = TemplateBuilder(load_templates(path), [main, sub]).build()
    include = root.find("include[@name='skinshortcuts-Sub']")
    assert include is not None and include.find(".//skinshortcuts") is None
    assert "Submenu Template Error: 'Sub' uses <skinshortcuts include>" in notified
    assert "Submenu Template Error: 'rows' variableGroups are not built" in notified


def test_var_condition_expands_expressions(built: tuple[ET.Element, list[str]]) -> None:
    assert values(built[0])[3] == "yes"


def test_first_matching_property_wins(tmp_path: Path) -> None:
    path = tmp_path / "templates.xml"
    path.write_text("""<templates>
  <submenu include="Sub" level="1">
    <property name="pick" condition="name=movies">first</property>
    <property name="pick">second</property>
    <controls><control type="label"><label>$PROPERTY[pick]</label></control></controls>
  </submenu>
</templates>""", encoding="utf-8")
    main = Menu(name="mainmenu", items=[MenuItem(name="movies", label="Movies")])
    sub = Menu(name="mainmenu/movies", items=[MenuItem(name="movies", label="M")], is_submenu=True)
    root = TemplateBuilder(load_templates(path), [main, sub]).build()
    assert root.findtext("include[@name='skinshortcuts-Sub']/control/label") == "first"


def test_unsupported_features_are_ignored(built: tuple[ET.Element, list[str]]) -> None:
    include = built[0]
    assert values(include)[2] == ""
    assert include.findtext("control/label") == "$IF[name=movies THEN yes ELSE no]"
    assert include.findtext("control/label2") == "$PARENT[name]"


def test_items_filter_is_honored(built: tuple[ET.Element, list[str]]) -> None:
    labels = [b.findtext("label") for b in built[0].iter("control") if b.get("type") == "button"]
    assert labels == ["keep"]


CONDITIONED = """<templates>
  <template items="rows">
    <condition>name=%s</condition>
    <controls><control type="button"><label>$PROPERTY[name]</label></control></controls>
  </template>
  <submenu include="Level" level="1">
    <controls><control type="group"><skinshortcuts insert="rows" /></control></controls>
  </submenu>
  <submenu include="Named" name="mainmenu/movies">
    <controls><control type="group"><skinshortcuts insert="rows" /></control></controls>
  </submenu>
</templates>"""


def build_conditioned(tmp_path: Path, parent: str, monkeypatch: pytest.MonkeyPatch):
    """Build Level and Named includes for a parent-gated items template, plus notifications."""
    path = tmp_path / "templates.xml"
    path.write_text(CONDITIONED % parent, encoding="utf-8")
    notified: list[str] = []
    monkeypatch.setattr(
        "skinshortcuts.builders.template.notify", lambda h, m, *_: notified.append(f"{h}: {m}")
    )
    main = Menu(name="mainmenu", items=[MenuItem(name="movies", label="Movies")])
    sub = Menu(name="mainmenu/movies", items=[MenuItem(name="a", label="A")], is_submenu=True)
    root = TemplateBuilder(load_templates(path), [main, sub]).build()
    level = root.find("include[@name='skinshortcuts-Level']")
    named = root.find("include[@name='skinshortcuts-Named']")
    assert level is not None and named is not None
    return level, named, notified


@pytest.mark.parametrize(("parent", "rows"), [("movies", 1), ("music", 0)])
def test_items_condition_tests_the_parent_item(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, parent: str, rows: int
) -> None:
    level, _, _ = build_conditioned(tmp_path, parent, monkeypatch)
    assert len(level.findall(".//control[@type='button']")) == rows


def test_items_condition_in_a_named_submenu_is_reported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, named, notified = build_conditioned(tmp_path, "music", monkeypatch)
    assert len(named.findall(".//control[@type='button']")) == 1
    assert "Submenu Template Error: 'rows' condition has no item to test" in notified
