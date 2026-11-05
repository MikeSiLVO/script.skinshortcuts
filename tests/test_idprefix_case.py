"""The idprefix built-in reads in any case, and an output suffix never applies to it."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.conditions import suffix_condition, suffix_property
from skinshortcuts.loaders.menu import load_menus
from skinshortcuts.loaders.template import load_templates

SPELLINGS = ["idprefix", "idPrefix", "IDPREFIX"]

MENUS = """<menus>
<menu name="mainmenu" container="9000">
  <item name="movies"><label>Movies</label><action>Noop</action></item>
</menu>
<submenu name="movies.1" type="widgets">
  <item name="recent"><label>Recent</label><action>Noop</action></item>
</submenu>
</menus>"""

TEMPLATES = """<templates>
<expressions><expression name="secondSlot">{name}=82</expression></expressions>
<includes><include name="secondOnly"><marker>yes</marker></include></includes>
<propertyGroups><propertyGroup name="group">
  <property name="groupFrom" from="{name}" />
  <property name="groupCondition" condition="{name}=82">two</property>
  <property name="groupCondition">one</property>
</propertyGroup></propertyGroups>
<template menu="mainmenu">
  <output include="first" idPrefix="81" />
  <output include="second" idPrefix="82" suffix=".2" />
  <property name="fromSource" from="{name}" />
  <property name="literal">id$PROPERTY[{name}]</property>
  <property name="byCondition" condition="{name}=82">two</property>
  <property name="byCondition">one</property>
  <property name="byExpression" condition="$EXP[secondSlot]">two</property>
  <property name="byExpression">one</property>
  <var name="byVar">
    <value condition="{name}=82">two</value>
    <value>one</value>
  </var>
  <propertyGroup content="group" />
  <controls>
    <control type="group" id="$PROPERTY[{name}]">
      <body>$PROPERTY[{name}]</body>
      <math>$MATH[{name} + 1]</math>
      <if>$IF[{name}=82 THEN two ELSE one]</if>
      <fromSource>$PROPERTY[fromSource]</fromSource>
      <literal>$PROPERTY[literal]</literal>
      <byCondition>$PROPERTY[byCondition]</byCondition>
      <byExpression>$PROPERTY[byExpression]</byExpression>
      <byVar>$PROPERTY[byVar]</byVar>
      <groupFrom>$PROPERTY[groupFrom]</groupFrom>
      <groupCondition>$PROPERTY[groupCondition]</groupCondition>
      <skinshortcuts include="secondOnly" condition="{name}=82" />
      <skinshortcuts insert="widget" />
    </control>
  </controls>
</template>
<template items="widget" source="1">
  <controls><control type="button"><parent>$PARENT[{name}]</parent></control></controls>
</template>
<template include="raw" build="true" idPrefix="90" menu="mainmenu">
  <property name="rawFrom" from="{name}" />
  <controls>
    <control type="group"><rawFrom>$PROPERTY[rawFrom]</rawFrom><rawBody>$PROPERTY[{name}]</rawBody>
    </control>
  </controls>
</template>
</templates>"""

EXPECTED = {
    "first": {
        "id": "81", "body": "81", "math": "82", "if": "one", "fromSource": "81",
        "literal": "id81", "byCondition": "one", "byExpression": "one", "byVar": "one",
        "groupFrom": "81", "groupCondition": "one", "parent": "81",
    },
    "second": {
        "id": "82", "body": "82", "math": "83", "if": "two", "fromSource": "82",
        "literal": "id82", "byCondition": "two", "byExpression": "two", "byVar": "two",
        "groupFrom": "82", "groupCondition": "two", "marker": "yes", "parent": "82",
    },
    "raw": {"rawFrom": "90", "rawBody": "90"},
}


def build(tmp_path: Path, name: str) -> ET.Element:
    """Build the test templates with the built-in written as the given spelling."""
    menus_path = tmp_path / "menus.xml"
    menus_path.write_text(MENUS, encoding="utf-8")
    templates_path = tmp_path / "templates.xml"
    templates_path.write_text(TEMPLATES.format(name=name), encoding="utf-8")
    menus = load_menus(str(menus_path))
    return TemplateBuilder(load_templates(str(templates_path)), menus.menus, None).build()


def resolved(root: ET.Element) -> dict[str, dict[str, str]]:
    """Each include's leaf texts by tag, plus the first control's id."""
    found: dict[str, dict[str, str]] = {}
    for include in root.iter("include"):
        name = include.get("name", "").removeprefix("skinshortcuts-template-")
        values = found.setdefault(name, {})
        control = include.find("control")
        if control is not None and control.get("id"):
            values["id"] = control.get("id", "")
        for elem in include.iter():
            if len(elem) == 0 and elem.text and elem.text.strip():
                values[elem.tag] = elem.text.strip()
    return found


@pytest.mark.parametrize("name", SPELLINGS)
def test_each_reference_resolves(tmp_path: Path, name: str) -> None:
    """Each place a template reads the built-in resolves to the output's prefix, suffixed or not."""
    assert resolved(build(tmp_path, name)) == EXPECTED


@pytest.mark.parametrize("name", SPELLINGS[1:])
def test_build_matches_lowercase(tmp_path: Path, name: str) -> None:
    """Any spelling builds the same includes as the lowercase one."""
    lower = ET.tostring(build(tmp_path, "idprefix"), encoding="unicode")
    other = ET.tostring(build(tmp_path, name), encoding="unicode")
    assert other == lower


@pytest.mark.parametrize("name", SPELLINGS)
@pytest.mark.parametrize("form", ["{}=82", "!{}", "{}", "{} EMPTY", "{} IN 81,82", "{}~8"])
def test_suffix_leaves_the_built_in(name: str, form: str) -> None:
    """A suffix leaves the built-in's name in each condition form and in a from= read."""
    condition = form.format(name)
    assert suffix_condition(condition, ".2") == condition
    assert suffix_property(name, ".2") == name
