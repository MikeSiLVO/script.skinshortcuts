"""A template var value follows the widget suffix only through a from property."""

from __future__ import annotations

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.models.menu import MenuItem
from skinshortcuts.models.template import (
    PropertyGroup,
    TemplateProperty,
    TemplateVar,
)


@pytest.fixture
def builder() -> TemplateBuilder:
    tb = TemplateBuilder.__new__(TemplateBuilder)
    tb.schema = None
    tb.menus = []
    tb._menu_map = {}
    tb._assigned_templates = set()
    return tb


@pytest.fixture
def item() -> MenuItem:
    return MenuItem(name="home", label="Home", properties={
        "widget": "movies-recent",
        "widget.2": "tvshows-recent",
        "widgetLabel": "Recent Movies",
        "widgetLabel.2": "Recent TV",
    })


def _resolve_label(builder: TemplateBuilder, group: PropertyGroup,
                   item: MenuItem, suffix: str) -> str | None:
    """Label var a property group resolves to for an item under a suffix."""
    ctx = {"suffix": suffix}
    builder._apply_property_group(group, item, ctx, suffix)
    return ctx.get("label")


def test_var_value_raw_property_is_not_suffix_aware(builder, item):
    group = PropertyGroup(name="g", vars=[
        TemplateVar(name="label", values=[
            TemplateProperty(name="", value="$PROPERTY[widgetLabel]"),
        ]),
    ])
    assert _resolve_label(builder, group, item, "") == "Recent Movies"
    assert _resolve_label(builder, group, item, ".2") == "Recent Movies"


def test_var_value_via_from_property_is_suffix_aware(builder, item):
    """A `from` property feeding the var gives each widget its own label."""
    group = PropertyGroup(
        name="g",
        properties=[TemplateProperty(name="itemlabel", from_source="widgetLabel")],
        vars=[
            TemplateVar(name="label", values=[
                TemplateProperty(name="", value="$INFO[...BasedOnLabel]",
                                 condition="widget~recommended-"),
                TemplateProperty(name="", value="$PROPERTY[itemlabel]"),
            ]),
        ],
    )
    assert _resolve_label(builder, group, item, "") == "Recent Movies"
    assert _resolve_label(builder, group, item, ".2") == "Recent TV"
