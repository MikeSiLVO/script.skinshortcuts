"""The <contextmenu> element: on/off, enableon focus gating, and custom <button> rows."""

from __future__ import annotations

import types
from pathlib import Path

import xbmc

from skinshortcuts.dialog.base import (
    CONTROL_DELETE,
    CONTROL_EDIT_SUBMENU,
    CONTROL_SET_ACTION,
    CONTROL_SET_ICON,
    CONTROL_SET_LABEL,
    CONTROL_TOGGLE_DISABLED,
    DialogBaseMixin,
)
from skinshortcuts.dialog.items import ItemsMixin
from skinshortcuts.loaders.menu import load_menus
from skinshortcuts.loaders.property import load_properties
from skinshortcuts.models.menu import ContextMenu, ContextMenuButton, MenuItem, SubDialog


def _load(tmp_path: Path, contextmenu_xml: str) -> ContextMenu:
    """Load the context menu from a menus.xml around a contextmenu element."""
    menus = f"""<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>Noop</action></item>
  </menu>
  {contextmenu_xml}
</menus>
"""
    path = tmp_path / "menus.xml"
    path.write_text(menus)
    return load_menus(path).context_menu


def _rows(
    context_menu: ContextMenu,
    item: MenuItem,
    subdialogs: dict[int, SubDialog] | None = None,
    property_schema: object = None,
    property_suffix: str = "",
) -> list[tuple[int, str]]:
    """Bind the row builder to a stub with only what it touches."""
    stub = types.SimpleNamespace(
        manager=None,
        menu_id="mainmenu",
        context_menu=context_menu,
        property_schema=property_schema,
        property_suffix=property_suffix,
        _subdialogs=subdialogs or {},
        _log=lambda _msg: None,
    )
    stub._get_item_properties = DialogBaseMixin._get_item_properties.__get__(stub)
    stub._context_button_routes = ItemsMixin._context_button_routes.__get__(stub)
    return ItemsMixin._context_menu_rows.__get__(stub)(item)


def _allowed(context_menu: ContextMenu, focus_id: int) -> bool:
    """Whether the context menu opens with a control focused."""
    stub = types.SimpleNamespace(context_menu=context_menu, getFocusId=lambda: focus_id)
    return DialogBaseMixin._context_menu_allowed.__get__(stub)()


def _item(**kwargs) -> MenuItem:
    """Movies menu item with extra fields."""
    return MenuItem(name=kwargs.pop("name", "movies"), label="Movies", **kwargs)


def test_absent_element_is_on_everywhere(tmp_path: Path):
    """No <contextmenu>: enabled, no focus gate, built-in rows."""
    context_menu = _load(tmp_path, "")

    assert context_menu.enabled
    assert context_menu.enable_on == []
    assert context_menu.buttons == []


def test_text_true_and_false(tmp_path: Path):
    """The text `false` is the only off switch; anything else is on and logged."""
    assert _load(tmp_path, "<contextmenu>true</contextmenu>").enabled
    assert not _load(tmp_path, "<contextmenu>false</contextmenu>").enabled
    assert _load(tmp_path, "<contextmenu>no</contextmenu>").enabled
    assert _load(tmp_path, "<contextmenu>0</contextmenu>").enabled


def test_empty_element_is_on(tmp_path: Path):
    """An empty element declares nothing and takes the default."""
    assert _load(tmp_path, "<contextmenu></contextmenu>").enabled


def test_enableon_parses_ids(tmp_path: Path):
    """Attribute-only form is on, gated to those controls."""
    context_menu = _load(tmp_path, '<contextmenu enableon="211, 212" />')

    assert context_menu.enabled
    assert context_menu.enable_on == [211, 212]


def test_enableon_drops_junk(tmp_path: Path):
    context_menu = _load(tmp_path, '<contextmenu enableon="211,list,,212" />')

    assert context_menu.enable_on == [211, 212]


def test_buttons_parse(tmp_path: Path):
    """Rows carry id, label, and both condition flavors."""
    context_menu = _load(tmp_path, """<contextmenu>
    <button id="305" label="Rename" />
    <button id="313" label="Enable" visible="Control.HasFocus(211)" condition="disabled=True" />
    <button id="nope" label="Ignored" />
  </contextmenu>""")

    assert context_menu.enabled
    assert [b.button_id for b in context_menu.buttons] == [305, 313]
    assert context_menu.buttons[0].label == "Rename"
    assert context_menu.buttons[1].visible == "Control.HasFocus(211)"
    assert context_menu.buttons[1].condition == "disabled=True"


def test_rejected_rows_fall_back_to_builtins(tmp_path: Path):
    """Every row dropped leaves the menu on with the built-in set, not dead."""
    context_menu = _load(tmp_path, """<contextmenu>
    <button id="delete" label="Delete" />
  </contextmenu>""")

    assert context_menu.enabled
    assert context_menu.buttons == []


def test_unicode_digits_do_not_raise(tmp_path: Path):
    """The guard has to match int(); isdigit() accepts characters int() rejects."""
    context_menu = _load(tmp_path, """<contextmenu enableon="2¹11">
    <button id="3²05" label="Rename" />
  </contextmenu>""")

    assert context_menu.enable_on == []
    assert context_menu.buttons == []


def test_false_text_wins_over_rows(tmp_path: Path):
    """An explicit off is an off, whatever the element holds."""
    context_menu = _load(tmp_path, """<contextmenu>false<button id="305" label="Rename" />
  </contextmenu>""")

    assert not context_menu.enabled


def test_allowed_everywhere_without_enableon():
    context_menu = ContextMenu()

    assert _allowed(context_menu, 211)
    assert _allowed(context_menu, 401)
    assert _allowed(context_menu, 0)


def test_allowed_only_on_listed_controls():
    context_menu = ContextMenu(enable_on=[211, 212])

    assert _allowed(context_menu, 211)
    assert not _allowed(context_menu, 401)
    assert not _allowed(context_menu, 0)


def test_disabled_menu_never_opens():
    assert not _allowed(ContextMenu(enabled=False), 211)


def test_default_rows_when_no_buttons(monkeypatch):
    """No rows declared: the built-in five, in order."""
    monkeypatch.setattr("skinshortcuts.dialog.items.LANGUAGE", lambda sid: f"#{sid}")
    monkeypatch.setattr(xbmc, "getLocalizedString", lambda sid: f"core#{sid}", raising=False)

    rows = _rows(ContextMenu(), _item())

    assert [button_id for button_id, _ in rows] == [
        CONTROL_SET_LABEL,
        CONTROL_SET_ACTION,
        CONTROL_SET_ICON,
        CONTROL_EDIT_SUBMENU,
        CONTROL_DELETE,
    ]
    assert rows[0][1] == "#32171"
    assert rows[-1][1] == "core#117"


def test_skin_label_overrides_default(monkeypatch):
    monkeypatch.setattr("skinshortcuts.dialog.items.LANGUAGE", lambda sid: f"#{sid}")

    context_menu = ContextMenu(buttons=[
        ContextMenuButton(button_id=CONTROL_SET_LABEL, label="Rename"),
        ContextMenuButton(button_id=CONTROL_SET_ACTION),
    ])
    rows = _rows(context_menu, _item())

    assert rows == [(CONTROL_SET_LABEL, "Rename"), (CONTROL_SET_ACTION, "#32172")]


def test_condition_filters_on_item_properties(monkeypatch):
    monkeypatch.setattr("skinshortcuts.dialog.items.LANGUAGE", lambda sid: f"#{sid}")

    context_menu = ContextMenu(buttons=[
        ContextMenuButton(button_id=CONTROL_SET_LABEL, label="Enabled",
                          condition="disabled=False"),
        ContextMenuButton(button_id=CONTROL_SET_ACTION, label="Disabled",
                          condition="disabled=true"),
        ContextMenuButton(button_id=CONTROL_SET_ICON, label="Custom",
                          condition="widgetType=custom"),
    ])

    rows = _rows(context_menu, _item(properties={"widgetType": "movies"}))
    assert rows == [(CONTROL_SET_LABEL, "Enabled")]

    rows = _rows(context_menu, _item(disabled=True, properties={"widgetType": "custom"}))
    assert rows == [(CONTROL_SET_ACTION, "Disabled"), (CONTROL_SET_ICON, "Custom")]


def test_visible_filters_on_kodi_state(monkeypatch):
    monkeypatch.setattr(xbmc, "getCondVisibility", lambda expr: expr == "Skin.HasSetting(x)")

    context_menu = ContextMenu(buttons=[
        ContextMenuButton(button_id=CONTROL_SET_LABEL, label="Shown",
                          visible="Skin.HasSetting(x)"),
        ContextMenuButton(button_id=CONTROL_SET_ACTION, label="Hidden",
                          visible="Skin.HasSetting(y)"),
    ])

    assert _rows(context_menu, _item()) == [(CONTROL_SET_LABEL, "Shown")]


def test_subdialog_and_property_buttons_route(tmp_path: Path):
    """IDs the skin defines elsewhere are valid rows."""
    schema_path = tmp_path / "properties.xml"
    schema_path.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <property name="widgetStyle" type="options">
    <options><option value="Panel" label="Panel" /></options>
  </property>
  <buttons><button id="350" property="widgetStyle" /></buttons>
</properties>""")
    property_schema = load_properties(schema_path)

    context_menu = ContextMenu(buttons=[
        ContextMenuButton(button_id=800, label="Widget 1"),
        ContextMenuButton(button_id=350, label="Style"),
        ContextMenuButton(button_id=999, label="Nothing"),
    ])
    rows = _rows(
        context_menu,
        _item(),
        subdialogs={800: SubDialog(button_id=800, mode="widget1")},
        property_schema=property_schema,
    )

    assert (800, "Widget 1") in rows
    assert (999, "Nothing") not in rows


def test_condition_follows_the_subdialog_suffix(monkeypatch):
    """A row condition is written once and works in every widget slot."""
    monkeypatch.setattr("skinshortcuts.dialog.items.LANGUAGE", lambda sid: f"#{sid}")

    context_menu = ContextMenu(buttons=[
        ContextMenuButton(button_id=CONTROL_SET_LABEL, label="Custom",
                          condition="widgetType=custom")
    ])
    item = _item(properties={"widgetType": "movies", "widgetType.2": "custom"})

    assert _rows(context_menu, item) == []
    assert _rows(context_menu, item, property_suffix=".2") == [(CONTROL_SET_LABEL, "Custom")]


def test_toggle_label_follows_item_state(monkeypatch):
    """Button 313 offers Enable on a disabled item, Disable on a live one."""
    monkeypatch.setattr("skinshortcuts.dialog.items.LANGUAGE", lambda sid: f"#{sid}")

    context_menu = ContextMenu(buttons=[ContextMenuButton(button_id=CONTROL_TOGGLE_DISABLED)])

    assert _rows(context_menu, _item()) == [(CONTROL_TOGGLE_DISABLED, "#32117")]
    assert _rows(context_menu, _item(disabled=True)) == [(CONTROL_TOGGLE_DISABLED, "#32207")]


def test_button_mapped_to_missing_property_is_dropped(tmp_path: Path):
    """A mapping whose <property> does not exist would crash the click path."""
    schema_path = tmp_path / "properties.xml"
    schema_path.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <buttons><button id="350" property="widgetStlye" /></buttons>
</properties>""")

    context_menu = ContextMenu(buttons=[ContextMenuButton(button_id=350, label="Style")])
    rows = _rows(context_menu, _item(), property_schema=load_properties(schema_path))

    assert rows == []


def test_unlabelled_skin_button_is_dropped():
    """No label and no built-in default: nothing to show."""
    context_menu = ContextMenu(buttons=[ContextMenuButton(button_id=800)])
    rows = _rows(context_menu, _item(), subdialogs={800: SubDialog(button_id=800, mode="widget1")})

    assert rows == []


def test_boolean_conditions_ignore_case(monkeypatch):
    """The `disabled` property reads True/False, but the skinner's casing does not matter."""
    monkeypatch.setattr("skinshortcuts.dialog.items.LANGUAGE", lambda sid: f"#{sid}")

    for written in ("disabled=True", "disabled=true", "disabled=TRUE"):
        context_menu = ContextMenu(buttons=[
            ContextMenuButton(button_id=CONTROL_SET_LABEL, label="Row", condition=written)
        ])
        assert _rows(context_menu, _item(disabled=True)) == [(CONTROL_SET_LABEL, "Row")]
        assert _rows(context_menu, _item()) == []


def test_condition_sees_stored_values_not_fallbacks(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("skinshortcuts.dialog.items.LANGUAGE", lambda sid: f"#{sid}")

    schema_path = tmp_path / "properties.xml"
    schema_path.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <property name="widgetStyle" type="options">
    <options><option value="Panel" label="Panel" /></options>
  </property>
  <fallbacks>
    <fallback property="widgetStyle"><default>Panel</default></fallback>
  </fallbacks>
</properties>""")

    context_menu = ContextMenu(buttons=[
        ContextMenuButton(button_id=CONTROL_SET_LABEL, label="Unset", condition="widgetStyle EMPTY")
    ])
    rows = _rows(context_menu, _item(), property_schema=load_properties(schema_path))

    assert rows == [(CONTROL_SET_LABEL, "Unset")]


def test_typed_button_without_a_property_still_routes(tmp_path: Path):
    """A widget button needs no <property>; an options button does."""
    schema_path = tmp_path / "properties.xml"
    schema_path.write_text("""<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <buttons>
    <button id="309" property="widget" type="widget" />
    <button id="350" property="widgtStyle" type="select" />
  </buttons>
</properties>""")
    schema = load_properties(schema_path)

    context_menu = ContextMenu(buttons=[
        ContextMenuButton(button_id=309, label="Widget"),
        ContextMenuButton(button_id=350, label="Typo"),
    ])

    assert _rows(context_menu, _item(), property_schema=schema) == [(309, "Widget")]
