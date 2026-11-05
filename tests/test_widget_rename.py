"""Widget rename opt-in: button parsing, and the blank-label round trip."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.loaders.property import load_properties
from skinshortcuts.models.menu import Menu, MenuItem
from skinshortcuts.userdata import (
    MenuDiff,
    MenuItemDiff,
    UserData,
    load_userdata,
    save_userdata,
)

BLANK = " "


def _write_properties(tmp: Path, body: str) -> Path:
    """Write a properties.xml around given XML and return its path."""
    path = tmp / "properties.xml"
    path.write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<properties>\n{body}\n</properties>\n'
    )
    return path


def test_rename_attribute_parsed(tmp_path: Path):
    path = _write_properties(
        tmp_path,
        """
        <property name="widget" type="widget" />
        <buttons>
          <button id="309" property="widget" rename="true" />
        </buttons>
        """,
    )

    schema = load_properties(path)

    assert schema.buttons[309].rename is True


def test_rename_defaults_off(tmp_path: Path):
    path = _write_properties(
        tmp_path,
        """
        <property name="widget" type="widget" />
        <buttons>
          <button id="309" property="widget" />
        </buttons>
        """,
    )

    schema = load_properties(path)

    assert schema.buttons[309].rename is False


def test_rename_on_non_widget_button_still_parses(tmp_path: Path):
    """No-op renames are logged, not dropped."""
    path = _write_properties(
        tmp_path,
        """
        <property name="colour" />
        <buttons>
          <button id="401" property="colour" rename="true" />
        </buttons>
        """,
    )

    schema = load_properties(path)

    assert schema.buttons[401].property_name == "colour"


def test_blank_label_survives_userdata_round_trip(tmp_path: Path):
    path = tmp_path / "userdata.json"
    userdata = UserData(
        menus={
            "mainmenu": MenuDiff(
                items=[
                    MenuItemDiff(
                        name="movies",
                        properties={"widget": "recent", "widgetLabel": BLANK},
                    )
                ]
            )
        }
    )

    assert save_userdata(userdata, str(path))
    back = load_userdata(str(path))

    assert back.menus["mainmenu"].items[0].properties["widgetLabel"] == BLANK


def test_blank_label_emitted_into_includes(tmp_path: Path):
    menu = Menu(name="mainmenu")
    menu.items.append(
        MenuItem(
            name="movies",
            label="Movies",
            properties={"widget": "recent", "widgetLabel": BLANK},
        )
    )

    out = tmp_path / "includes.xml"
    IncludesBuilder(menus=[menu]).write(out)
    written = out.read_text()

    assert '<property name="widgetLabel"> </property>' in written


def test_empty_label_not_emitted(tmp_path: Path):
    """Contrast with blank: a truly empty value is dropped, not written."""
    menu = Menu(name="mainmenu")
    menu.items.append(
        MenuItem(
            name="movies",
            label="Movies",
            properties={"widget": "recent", "widgetLabel": ""},
        )
    )

    out = tmp_path / "includes.xml"
    IncludesBuilder(menus=[menu]).write(out)

    assert 'name="widgetLabel"' not in out.read_text()


def test_includes_file_uses_unix_line_endings(tmp_path):
    menu = Menu(name="mainmenu", items=[MenuItem(name="a", label="A")])
    out = tmp_path / "includes.xml"
    IncludesBuilder(menus=[menu]).write(out)

    assert b"\r\n" not in out.read_bytes()
