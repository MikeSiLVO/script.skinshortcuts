"""Menus with a controltype emit <control>, and the auto-stamped <icon> is suppressed there."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.models.menu import Menu, MenuItem


def _build(controltype: str) -> ET.Element:
    """Build the movies item in a menu of a given controltype."""
    item = MenuItem(name="movies", label="Movies", actions=[])
    menu = Menu(name="m", items=[item], controltype=controltype)
    builder = IncludesBuilder(
        menus=[menu], templates=[], property_schema=None, view_config=None, userdata={}
    )
    return builder._build_item(item, 1, menu)


def test_listitem_keeps_icon():
    elem = _build("")
    assert elem.tag == "item"
    assert elem.find("icon") is not None


def test_button_control_drops_auto_icon():
    elem = _build("button")
    assert elem.tag == "control"
    assert elem.get("type") == "button"
    assert elem.find("icon") is None
