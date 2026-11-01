"""Shortcut groupings: menu-specific sets, nested and flat groups, inputs and content."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.loaders.menu import load_groupings
from skinshortcuts.models.menu import Content, Input, Shortcut, ShortcutGroup

DEFAULT = (
    '<groupings><shortcut name="default" label="Default"><action>noop</action></shortcut>'
    "</groupings>"
)
POWER = (
    '<groupings menu="powermenu">'
    '<shortcut name="power" label="Power"><action>noop</action></shortcut></groupings>'
)


def load(tmp_path: Path, groupings: str, menu_id: str = "") -> list:
    """Load the groupings a menus.xml holding the given XML offers a menu."""
    path = tmp_path / "menus.xml"
    path.write_text(f'<menus><menu name="mainmenu"/>{groupings}</menus>', encoding="utf-8")
    return load_groupings(path, menu_id)


def names(items: list) -> list[str]:
    """Names of the shortcuts and groups in a groupings list, in order."""
    return [item.name for item in items]


def test_menu_groupings_replace_the_default(tmp_path: Path) -> None:
    """A menu with its own groupings gets only those; other menus get the default."""
    assert names(load(tmp_path, DEFAULT + POWER, "powermenu")) == ["power"]
    assert names(load(tmp_path, POWER + DEFAULT, "powermenu")) == ["power"]
    assert names(load(tmp_path, DEFAULT + POWER, "mainmenu")) == ["default"]


def test_empty_menu_groupings_offer_nothing(tmp_path: Path) -> None:
    """An empty groupings for a menu replaces the default with nothing."""
    assert load(tmp_path, DEFAULT + '<groupings menu="powermenu" />', "powermenu") == []


def test_groups_nest_and_a_flat_group_needs_no_label(tmp_path: Path) -> None:
    """Nested groups keep their tree, and a flat group without a label is kept."""
    items = load(tmp_path, """<groupings>
        <group name="outer" label="Outer">
            <group name="inner" label="Inner">
                <shortcut name="deep" label="Deep"><action>noop</action></shortcut>
            </group>
        </group>
        <group name="loose" flat="true">
            <shortcut name="flat-one" label="Flat"><action>noop</action></shortcut>
        </group>
    </groupings>""")

    outer, loose = items
    assert isinstance(outer, ShortcutGroup) and isinstance(loose, ShortcutGroup)
    inner = outer.items[0]
    assert isinstance(inner, ShortcutGroup)
    assert names(inner.items) == ["deep"]
    assert loose.flat and not loose.label
    assert names(loose.items) == ["flat-one"]


def test_groups_without_name_or_label_are_skipped(tmp_path: Path) -> None:
    """A group with no name, or no label while not flat, is left out; its siblings stay."""
    items = load(tmp_path, """<groupings>
        <group label="No name"><shortcut name="a" label="A"><action>noop</action></shortcut></group>
        <group name="nolabel"><shortcut name="b" label="B"><action>noop</action></shortcut></group>
        <shortcut name="kept" label="Kept"><action>noop</action></shortcut>
    </groupings>""")

    assert names(items) == ["kept"]


def test_inputs_take_defaults_and_need_a_label(tmp_path: Path) -> None:
    """An input defaults to a text prompt for the action; one with no label is left out."""
    items = load(tmp_path, """<groupings><group name="g" label="G">
        <input label="Custom" />
        <input label="Address" type="ipaddress" for="path" icon="ip.png" />
        <input />
    </group></groupings>""")

    plain, address = items[0].items
    assert isinstance(plain, Input) and isinstance(address, Input)
    assert (plain.type, plain.for_, plain.icon) == ("text", "action", "DefaultFile.png")
    assert (address.type, address.for_, address.icon) == ("ipaddress", "path", "ip.png")


def test_content_needs_a_source(tmp_path: Path) -> None:
    """A content entry carries its attributes; one with no source is left out."""
    items = load(tmp_path, """<groupings><group name="g" label="G">
        <content source="playlists" target="videos" folder="Playlists" />
        <content target="videos" />
    </group></groupings>""")

    (content,) = items[0].items
    assert isinstance(content, Content)
    assert (content.source, content.target, content.folder) == ("playlists", "videos", "Playlists")


def test_shortcut_needs_a_name_and_an_action_or_browse_path(tmp_path: Path) -> None:
    """A shortcut needs a name and actions or a browse path; primary picks the main action."""
    items = load(tmp_path, """<groupings>
        <shortcut name="empty" label="Empty"><action> </action></shortcut>
        <shortcut name="no-path" label="No path" browse="videos" />
        <shortcut name="browse" label="Browse" browse="videos">
            <path>videodb://movies/</path>
        </shortcut>
        <shortcut name="two" label="Two">
            <action>First</action><action primary="true">Second</action>
        </shortcut>
        <shortcut label="Nameless"><action>noop</action></shortcut>
    </groupings>""")

    assert names(items) == ["browse", "two"]
    two = items[1]
    assert isinstance(two, Shortcut)
    assert [action.action for action in two.actions] == ["First", "Second"]
    assert two.primary_action == "Second"
