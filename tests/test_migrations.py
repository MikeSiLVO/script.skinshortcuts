"""Retired names in an <overrides> block move or clear the userdata still storing them."""
from __future__ import annotations

import pytest


def _userdata(props, removed=None):
    """Userdata with one mainmenu movies item holding given properties."""
    from skinshortcuts.userdata import MenuItemDiff, MenuDiff, UserData
    item = MenuItemDiff(name="movies", properties=dict(props))
    if removed:
        item.removed_properties = list(removed)
    return UserData(menus={"mainmenu": MenuDiff(items=[item])})


def _item(userdata):
    """First mainmenu item in the userdata."""
    return userdata.menus["mainmenu"].items[0]


def _load(tmp_path, *, widgets="", backgrounds="", properties=""):
    """Write and load properties, widgets and backgrounds files from given XML."""
    from skinshortcuts.loaders.background import load_backgrounds
    from skinshortcuts.loaders.property import load_properties
    from skinshortcuts.loaders.widget import load_widgets

    (tmp_path / "widgets.xml").write_text(f"<widgets>{widgets}</widgets>", encoding="utf-8")
    (tmp_path / "backgrounds.xml").write_text(
        f"<backgrounds>{backgrounds}</backgrounds>", encoding="utf-8"
    )
    (tmp_path / "properties.xml").write_text(
        f"<properties>{properties}</properties>", encoding="utf-8"
    )
    return (
        load_properties(tmp_path / "properties.xml"),
        load_widgets(tmp_path / "widgets.xml"),
        load_backgrounds(tmp_path / "backgrounds.xml"),
    )


def _apply(tmp_path, props, removed=None, **files):
    """Apply overrides to one item and return it with the change count."""
    from skinshortcuts.migrations import apply_overrides
    userdata = _userdata(props, removed)
    count = apply_overrides(userdata, *_load(tmp_path, **files))
    return _item(userdata), count


RENAMED_PROP = (
    '<overrides><property replace="widgetStyle">listStyle</property></overrides>'
    '<property name="listStyle" />'
)
RETIRED_PROP = '<overrides><property replace="oldStyle"></property></overrides>'
RENAMED_WIDGET = (
    '<overrides><widget replace="tmdbrecommended">sisrecommended</widget></overrides>'
    '<widget name="sisrecommended" label="Recommended"><path>plugin://sis/rec</path></widget>'
)
RETIRED_WIDGET = '<overrides><widget replace="tmdbnextaired"></widget></overrides>'
RENAMED_BG = (
    '<overrides><background replace="kodifanart">silvofanart</background></overrides>'
    '<background name="silvofanart" label="Fanart" type="property"><path>x</path></background>'
)


def test_property_rename_carries_numbered_slots(tmp_path):
    item, count = _apply(
        tmp_path, {"widgetStyle": "poster", "widgetStyle.2": "fanart"}, properties=RENAMED_PROP
    )
    assert item.properties == {"listStyle": "poster", "listStyle.2": "fanart"}
    assert count == 2


def test_property_rename_leaves_a_similar_name_alone(tmp_path):
    item, _ = _apply(tmp_path, {"widgetStyleExtra": "keep"}, properties=RENAMED_PROP)
    assert item.properties == {"widgetStyleExtra": "keep"}


def test_property_rename_drops_the_stale_key_when_the_target_is_set(tmp_path):
    item, _ = _apply(tmp_path, {"widgetStyle": "old", "listStyle": "new"}, properties=RENAMED_PROP)
    assert item.properties == {"listStyle": "new"}


def test_property_rename_follows_a_cleared_default(tmp_path):
    item, _ = _apply(tmp_path, {}, removed=["widgetStyle.2"], properties=RENAMED_PROP)
    assert item.removed_properties == ["listStyle.2"]


def test_retired_property_is_dropped(tmp_path):
    item, count = _apply(
        tmp_path,
        {"oldStyle": "x", "oldStyle.2": "y"},
        removed=["oldStyle"],
        properties=RETIRED_PROP,
    )
    assert item.properties == {}
    assert item.removed_properties == []
    assert count == 3


def test_widget_rename_moves_the_stored_name(tmp_path):
    item, count = _apply(
        tmp_path, {"widget": "tmdbrecommended", "widget.2": "other"}, widgets=RENAMED_WIDGET
    )
    assert item.properties == {"widget": "sisrecommended", "widget.2": "other"}
    assert count == 1


def test_retired_widget_clears_the_slot(tmp_path):
    item, count = _apply(
        tmp_path, {"widget": "tmdbnextaired", "widget.2": "keep"}, widgets=RETIRED_WIDGET
    )
    assert item.properties == {"widget.2": "keep"}
    assert count == 1


def test_background_rename_moves_the_stored_name(tmp_path):
    item, _ = _apply(tmp_path, {"background": "kodifanart"}, backgrounds=RENAMED_BG)
    assert item.properties == {"background": "silvofanart"}


def test_overrides_are_idempotent(tmp_path):
    from skinshortcuts.migrations import apply_overrides
    loaded = _load(tmp_path, properties=RENAMED_PROP, widgets=RENAMED_WIDGET)
    userdata = _userdata({"widgetStyle": "poster", "widget": "tmdbrecommended"})
    first = apply_overrides(userdata, *loaded)
    settled = dict(_item(userdata).properties)
    second = apply_overrides(userdata, *loaded)
    assert first == 2
    assert second == 0
    assert dict(_item(userdata).properties) == settled


def test_no_overrides_section_is_a_no_op(tmp_path):
    item, count = _apply(tmp_path, {"widget": "movies"})
    assert count == 0
    assert item.properties == {"widget": "movies"}


@pytest.mark.parametrize(
    "section", ["<overrides></overrides>", '<overrides><widget>x</widget></overrides>']
)
def test_incomplete_entries_are_ignored(tmp_path, section):
    item, count = _apply(tmp_path, {"widget": "movies"}, widgets=section)
    assert count == 0
    assert item.properties == {"widget": "movies"}


UNDEFINED_TARGET = '<overrides><widget replace="old">nosuchwidget</widget></overrides>'
SELF_RENAME = (
    '<overrides><property replace="listStyle">listStyle</property></overrides>'
    '<property name="listStyle" />'
)
SCRIPT_OWNED = '<overrides><property replace="widgetPath">myPath</property></overrides>'
SKIN_OWNED = (
    '<overrides><property replace="widgetStyle">widgetArt</property></overrides>'
    '<property name="widgetArt" />'
)


def test_a_rename_to_an_undefined_name_is_refused(tmp_path):
    item, count = _apply(tmp_path, {"widget": "old"}, widgets=UNDEFINED_TARGET)
    assert count == 0
    assert item.properties == {"widget": "old"}


def test_a_self_rename_does_not_delete_the_property(tmp_path):
    item, count = _apply(tmp_path, {"listStyle": "poster"}, properties=SELF_RENAME)
    assert count == 0
    assert item.properties == {"listStyle": "poster"}


def test_script_owned_keys_are_refused(tmp_path):
    item, count = _apply(tmp_path, {"widgetPath": "plugin://user/"}, properties=SCRIPT_OWNED)
    assert count == 0
    assert item.properties == {"widgetPath": "plugin://user/"}


def test_a_skin_owned_widget_property_still_renames(tmp_path):
    item, _ = _apply(tmp_path, {"widgetStyle": "Panel"}, properties=SKIN_OWNED)
    assert item.properties == {"widgetArt": "Panel"}


def test_a_rename_keeps_the_users_label_and_drops_the_stale_bake(tmp_path):
    item, _ = _apply(
        tmp_path,
        {"widget": "tmdbrecommended", "widgetLabel": "MY NAME", "widgetPath": "plugin://old/"},
        widgets=RENAMED_WIDGET,
    )
    assert item.properties == {"widget": "sisrecommended", "widgetLabel": "MY NAME"}


def test_a_rename_drops_a_stale_bake_in_a_numbered_slot(tmp_path):
    item, _ = _apply(
        tmp_path,
        {"widget.2": "tmdbrecommended", "widgetPath.2": "plugin://old/", "widgetType.2": "movies"},
        widgets=RENAMED_WIDGET,
    )
    assert item.properties == {"widget.2": "sisrecommended"}


def test_a_rename_keeps_a_playlist_background_path(tmp_path):
    playlist = (
        '<overrides><background replace="playlist">live-playlist</background></overrides>'
        '<background name="live-playlist" label="Playlist" type="live-playlist" />'
    )
    item, _ = _apply(
        tmp_path,
        {"background": "playlist", "backgroundPath": "special://profile/playlists/mine.xsp"},
        backgrounds=playlist,
    )
    assert item.properties["backgroundPath"] == "special://profile/playlists/mine.xsp"


def test_retiring_clears_the_whole_cluster(tmp_path):
    item, _ = _apply(
        tmp_path,
        {"widget": "tmdbnextaired", "widgetLabel": "x", "widgetPath": "y", "widgetType": "z"},
        widgets=RETIRED_WIDGET,
    )
    assert item.properties == {}


def test_successive_renames_point_at_the_current_name(tmp_path):
    successive = (
        '<overrides>'
        '<widget replace="a">c</widget>'
        '<widget replace="b">c</widget>'
        '</overrides>'
        '<widget name="c" label="C"><path>p</path></widget>'
    )
    item, _ = _apply(tmp_path, {"widget": "a", "widget.2": "b"}, widgets=successive)
    assert item.properties == {"widget": "c", "widget.2": "c"}


def test_an_override_for_something_still_shipped_is_refused(tmp_path):
    still_shipped = (
        '<overrides><widget replace="keeper"></widget></overrides>'
        '<widget name="keeper" label="Keeper"><path>p</path></widget>'
    )
    item, count = _apply(tmp_path, {"widget": "keeper"}, widgets=still_shipped)
    assert count == 0
    assert item.properties == {"widget": "keeper"}


def test_a_background_sub_key_is_not_treated_as_a_slot(tmp_path):
    # a skin background named after a type word must not match background.2Type's value
    named_browse = (
        '<overrides><background replace="browse">hero</background></overrides>'
        '<background name="hero" label="Hero" type="property"><path>x</path></background>'
    )
    item, _ = _apply(
        tmp_path,
        {"background.2": "/home/user/my.jpg", "background.2Type": "browse"},
        backgrounds=named_browse,
    )
    assert item.properties == {"background.2": "/home/user/my.jpg", "background.2Type": "browse"}


def test_a_rename_onto_a_script_owned_key_is_refused(tmp_path):
    onto_widget = '<overrides><property replace="oldStyle">widget</property></overrides>'
    item, count = _apply(tmp_path, {"oldStyle": "poster"}, properties=onto_widget)
    assert count == 0
    assert item.properties == {"oldStyle": "poster"}


@pytest.mark.parametrize("name", ["widgetLimit", "widgetSortBy", "widgetSortOrder"])
def test_a_baked_sort_key_cannot_be_retired(tmp_path, name):
    """The picker bakes these; a skin naming one must not strip the user's value."""
    item, count = _apply(
        tmp_path,
        {name: "5"},
        properties=f'<overrides><property replace="{name}"></property></overrides>',
    )
    assert count == 0
    assert item.properties == {name: "5"}


def test_retiring_a_widget_leaves_the_sort_the_user_set(tmp_path):
    """Nothing derives limit/sort back; clearing the name must not take them too."""
    item, _ = _apply(
        tmp_path,
        {"widget": "tmdbnextaired", "widgetPath": "plugin://old/", "widgetLimit": "5"},
        widgets=RETIRED_WIDGET,
    )
    assert item.properties == {"widgetLimit": "5"}
