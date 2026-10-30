"""Widget and background sub-properties derive per slot."""
from __future__ import annotations

import pytest


@pytest.fixture
def config():
    from skinshortcuts.config import SkinConfig
    from skinshortcuts.models.background import Background, BackgroundConfig, BackgroundType
    from skinshortcuts.models.widget import Widget, WidgetConfig

    return SkinConfig(
        _widget_config=WidgetConfig(widgets=[
            Widget(name="recent", label="Recent", path="videodb://recent/", type="movies",
                   target="videos"),
            Widget(name="peritem", label="Per Item", path="videodb://{menuitem}/"),
        ]),
        _background_config=BackgroundConfig(backgrounds=[
            Background(name="fanart", label="Fanart", path="special://fanart/",
                       type=BackgroundType.PROPERTY),
        ]),
    )


def _item(**properties):
    """Movies menu item holding given properties."""
    from skinshortcuts.models.menu import MenuItem
    return MenuItem(name="movies", label="Movies", properties=properties)


def test_a_numbered_widget_slot_derives(config):
    derived = config.derived_item_properties(_item(**{"widget.2": "recent"}))
    assert derived["widgetPath.2"] == "videodb://recent/"
    assert derived["widgetLabel.2"] == "Recent"
    assert derived["widgetType.2"] == "movies"


def test_a_numbered_background_slot_derives(config):
    derived = config.derived_item_properties(_item(**{"background.2": "fanart"}))
    assert derived["backgroundPath.2"] == "special://fanart/"
    assert derived["backgroundLabel.2"] == "Fanart"


def test_a_sub_key_is_not_mistaken_for_a_slot(config):
    # backgroundType.2 holds a type word, not a background name
    derived = config.derived_item_properties(
        _item(**{"background.2": "/home/user/pic.jpg", "backgroundType.2": "browse"})
    )
    assert not any("browse" in k for k in derived)


def test_a_skin_property_named_after_a_slot_is_left_alone(config):
    derived = config.derived_item_properties(_item(widgetStyle="Panel", widgetArt="Poster"))
    assert derived == {}


def test_the_menuitem_placeholder_resolves_per_slot(config):
    derived = config.derived_item_properties(_item(**{"widget.3": "peritem"}))
    assert derived["widgetPath.3"] == "videodb://movies/"


def test_derived_values_are_stripped_at_save_and_user_values_kept(config):
    from skinshortcuts.manager import _is_derived

    item = _item(**{"widget.2": "recent", "widgetLabel.2": "MY NAME"})
    derived = config.derived_item_properties(item)
    assert _is_derived(derived, "widgetPath.2", "videodb://recent/")
    assert not _is_derived(derived, "widgetLabel.2", "MY NAME")
