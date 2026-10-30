"""View default resolution: plugin default falls back to library default."""

from __future__ import annotations

from skinshortcuts.builders.views import ViewExpressionBuilder
from skinshortcuts.models.views import ViewConfig, ViewContent
from skinshortcuts.userdata import UserData


def _content(plugin_default: str = "") -> ViewContent:
    """Movies view content with library default 50 and an optional plugin default."""
    return ViewContent(
        name="movies", label="Movies", visible="Container.Content(movies)",
        views=["50", "51", "52"], library_default="50", plugin_default=plugin_default,
    )


def test_get_default_branches():
    assert _content().get_default(is_plugin=False) == "50"
    assert _content().get_default(is_plugin=True) == "50"
    assert _content("51").get_default(is_plugin=True) == "51"
    assert _content("51").get_default(is_plugin=False) == "50"


def test_builder_effective_views():
    content = _content("51")
    builder = ViewExpressionBuilder(ViewConfig(content_rules=[content]), UserData())
    assert builder._get_effective_library_view(content) == "50"
    assert builder._get_effective_generic_plugin_view(content) == "51"
    assert builder._get_effective_generic_plugin_view(_content()) == "50"


def test_builder_user_selection_wins_when_valid():
    content = _content("51")
    userdata = UserData()
    userdata.set_view("library", "movies", "52")
    userdata.set_view("plugins", "movies", "99")
    builder = ViewExpressionBuilder(ViewConfig(content_rules=[content]), userdata)
    assert builder._get_effective_library_view(content) == "52"
    assert builder._get_effective_generic_plugin_view(content) == "51"
