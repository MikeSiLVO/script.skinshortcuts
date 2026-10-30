"""Flat groups inline their children at parent level in the picker."""

from __future__ import annotations

from skinshortcuts.dialog.pickers import PickersMixin
from skinshortcuts.models.widget import Widget, WidgetGroup


class _Picker(PickersMixin):
    """Minimal adapter for filter testing."""

    def __init__(self) -> None:
        self.shortcuts_path = ""
        self.manager = None  # type: ignore[assignment]
        self.menu_id = ""
        self.items: list = []

    def _get_selected_item(self):
        return None

    def _get_item_properties(self, _item):
        return {}

    def _refresh_selected_item(self) -> None:
        pass

    def _log(self, _msg: str) -> None:
        pass


def _widget(name: str) -> Widget:
    """Plugin widget named and labeled the same."""
    return Widget(name=name, label=name, path=f"plugin://{name}")


def test_flat_group_children_inline_when_condition_passes():
    picker = _Picker()
    flat_group = WidgetGroup(
        name="home-bundle",
        label="",
        condition="slot=home",
        items=[_widget("a"), _widget("b")],
        flat=True,
    )
    items = [_widget("top"), flat_group]

    result = picker._filter_picker_items(
        items, {"slot": "home"}, leaf_types=(Widget,), group_types=(WidgetGroup,)
    )

    assert [getattr(i, "name", None) for i in result] == ["top", "a", "b"]


def test_flat_group_hidden_when_condition_fails():
    picker = _Picker()
    flat_group = WidgetGroup(
        name="home-bundle",
        label="",
        condition="slot=home",
        items=[_widget("a"), _widget("b")],
        flat=True,
    )
    items = [_widget("top"), flat_group]

    result = picker._filter_picker_items(
        items, {"slot": "other"}, leaf_types=(Widget,), group_types=(WidgetGroup,)
    )

    assert [getattr(i, "name", None) for i in result] == ["top"]


def test_folder_group_not_inlined():
    picker = _Picker()
    folder = WidgetGroup(
        name="movies",
        label="Movies",
        items=[_widget("a")],
        flat=False,
    )
    items = [folder, _widget("top")]

    result = picker._filter_picker_items(
        items, {}, leaf_types=(Widget,), group_types=(WidgetGroup,)
    )

    assert [type(i).__name__ for i in result] == ["WidgetGroup", "Widget"]


def test_nested_flat_groups_expand_recursively():
    picker = _Picker()
    inner = WidgetGroup(
        name="inner",
        label="",
        items=[_widget("c"), _widget("d")],
        flat=True,
    )
    outer = WidgetGroup(
        name="outer",
        label="",
        items=[_widget("b"), inner],
        flat=True,
    )
    items = [_widget("a"), outer]

    result = picker._filter_picker_items(
        items, {}, leaf_types=(Widget,), group_types=(WidgetGroup,)
    )

    assert [getattr(i, "name", None) for i in result] == ["a", "b", "c", "d"]


def test_child_conditions_still_apply_when_inlined():
    picker = _Picker()
    flat_group = WidgetGroup(
        name="bundle",
        label="",
        items=[
            Widget(name="visible", label="V", path="x", condition="show=true"),
            Widget(name="hidden", label="H", path="y", condition="show=false"),
        ],
        flat=True,
    )

    result = picker._filter_picker_items(
        [flat_group], {"show": "true"}, leaf_types=(Widget,), group_types=(WidgetGroup,)
    )

    assert [getattr(i, "name", None) for i in result] == ["visible"]


def test_slot_filter_preserves_flat_attribute():
    """The slot filter rebuilds WidgetGroup; it must carry flat through."""
    picker = _Picker()
    flat_group = WidgetGroup(
        name="bundle",
        label="",
        items=[Widget(name="a", label="A", path="x"), Widget(name="b", label="B", path="y")],
        flat=True,
    )

    filtered = picker._filter_widgets_by_slot([flat_group], slot="")

    assert len(filtered) == 1
    assert isinstance(filtered[0], WidgetGroup)
    assert filtered[0].flat is True
