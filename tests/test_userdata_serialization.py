"""Userdata serialization stays minimal: no empty/default fields written."""

from __future__ import annotations

from skinshortcuts.models.menu import Action
from skinshortcuts.userdata import (
    MenuItemDiff,
    MenuDiff,
    UserData,
    _action_to_dict,
)


def test_empty_condition_omitted():
    assert _action_to_dict(Action(action="Foo")) == {"action": "Foo"}


def test_condition_preserved_when_set():
    assert _action_to_dict(Action(action="Bar", condition="X")) == {
        "action": "Bar",
        "condition": "X",
    }


def test_item_dict_omits_unset_fields():
    item = MenuItemDiff(name="movies", position=0)
    result = UserData(menus={"mainmenu": MenuDiff(items=[item])}).to_dict()
    serialized = result["menus"]["mainmenu"]["items"][0]
    assert serialized == {"name": "movies", "position": 0}


def test_actions_round_trip_without_condition():
    ud = UserData(
        menus={
            "mainmenu": MenuDiff(
                items=[
                    MenuItemDiff(name="a", actions=[Action(action="Foo")]),
                    MenuItemDiff(
                        name="b", actions=[Action(action="Bar", condition="X")]
                    ),
                ]
            )
        }
    )
    back = UserData.from_dict(ud.to_dict())
    items = back.menus["mainmenu"].items
    assert items[0].actions[0].condition == ""
    assert items[1].actions[0].condition == "X"
