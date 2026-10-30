"""Menu-side includes stay defined, with a child, when their menu has no enabled items."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.models.menu import Menu, MenuItem


def item(name: str, disabled: bool = False, **properties: str) -> MenuItem:
    """Menu item labeled after its name, with optional properties."""
    return MenuItem(name=name, label=name.title(), disabled=disabled, properties=properties)


def include(menus: list[Menu], name: str) -> ET.Element | None:
    """Include of a given name in the built includes, or None."""
    return IncludesBuilder(menus).build().find(f"include[@name='{name}']")


def test_menu_with_enabled_items_has_children() -> None:
    menus = [
        Menu(name="mainmenu", items=[item("movies")]),
        Menu(name="mainmenu/movies", items=[item("recent")], is_submenu=True),
    ]
    found = include(menus, "skinshortcuts-mainmenu-submenu")
    assert found is not None and len(found) == 1


@pytest.mark.xfail(
    strict=True, reason="include missing or empty when its menu has no enabled items"
)
def test_root_menu_with_every_item_disabled() -> None:
    found = include([Menu(name="mainmenu", items=[item("movies", disabled=True)])],
                    "skinshortcuts-mainmenu")
    assert found is not None and len(found) > 0


@pytest.mark.xfail(
    strict=True, reason="include missing or empty when its menu has no enabled items"
)
def test_combined_submenu_with_every_item_disabled() -> None:
    menus = [
        Menu(name="mainmenu", items=[item("movies")]),
        Menu(name="mainmenu/movies", items=[item("recent", disabled=True)], is_submenu=True),
    ]
    found = include(menus, "skinshortcuts-mainmenu-submenu")
    assert found is not None and len(found) > 0


@pytest.mark.xfail(
    strict=True, reason="include missing or empty when its menu has no enabled items"
)
@pytest.mark.parametrize("items", [[], [item("recent", disabled=True)]], ids=["empty", "disabled"])
def test_standalone_submenu_with_no_enabled_items(items: list[MenuItem]) -> None:
    menus = [
        Menu(name="mainmenu", items=[item("pictures")]),
        Menu(name="mainmenu/pictures", items=items, is_submenu=True, template_origin="pictures"),
    ]
    found = include(menus, "skinshortcuts-pictures")
    assert found is not None and len(found) > 0


@pytest.mark.xfail(
    strict=True, reason="include missing or empty when its menu has no enabled items"
)
@pytest.mark.parametrize("custom", [None, []], ids=["missing", "empty"])
def test_custom_widget_with_no_items(custom: list[MenuItem] | None) -> None:
    menus = [Menu(name="mainmenu", items=[item("movies", customWidget="custom-abc")])]
    if custom is not None:
        menus.append(Menu(name="custom-abc", items=custom, is_submenu=True))
    found = include(menus, "skinshortcuts-movies-customwidget")
    assert found is not None and len(found) > 0
