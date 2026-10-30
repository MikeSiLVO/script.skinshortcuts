"""Per-add-on view overrides: the helper expressions and the view each source lands on."""

from __future__ import annotations

from skinshortcuts.builders.views import ViewExpressionBuilder
from skinshortcuts.models.views import View, ViewConfig, ViewContent
from skinshortcuts.userdata import UserData

MOVIES = "Container.Content(movies)"
NO_PLUGIN = "String.IsEmpty(Container.PluginName)"


def build(userdata: UserData, plugin_default: str = "") -> dict[str, str]:
    """Expression text by name, for a movies rule offering views 50, 51 and 52."""
    content = ViewContent(
        name="movies", label="Movies", visible=MOVIES,
        views=["50", "51", "52"], library_default="50", plugin_default=plugin_default,
    )
    views = [View(id=view_id, label=view_id) for view_id in content.views]
    config = ViewConfig(views=views, content_rules=[content])
    return {
        elem.get("name") or "": elem.text or ""
        for elem in ViewExpressionBuilder(config, userdata).build()
    }


def test_override_sends_its_addon_to_its_view() -> None:
    """An add-on's own view wins for that add-on; other add-ons get the generic plugin view."""
    userdata = UserData()
    userdata.set_view("plugin.video.example", "movies", "52")
    expressions = build(userdata, plugin_default="51")

    assert expressions["ShortcutView_Movies_HasPluginOverride"] == (
        "String.IsEqual(Container.PluginName,plugin.video.example)"
    )
    assert expressions["ShortcutView_Movies_IsGenericPlugin"] == (
        "!String.IsEmpty(Container.PluginName) + !$EXP[ShortcutView_Movies_HasPluginOverride]"
    )
    assert expressions["ShortcutView_50"] == f"[{MOVIES} + {NO_PLUGIN}]"
    assert expressions["ShortcutView_51"] == (
        f"[{MOVIES} + $EXP[ShortcutView_Movies_IsGenericPlugin]]"
    )
    assert expressions["ShortcutView_52"] == (
        f"[{MOVIES} + String.IsEqual(Container.PluginName,plugin.video.example)]"
    )
    assert expressions["ShortcutView_52_Include"] == "True"


def test_overrides_in_id_order_and_unknown_views_ignored() -> None:
    """Overriding add-ons are listed in id order; one picking a view the rule lacks is left out."""
    userdata = UserData()
    userdata.set_view("plugin.b", "movies", "52")
    userdata.set_view("plugin.a", "movies", "51")
    userdata.set_view("plugin.c", "movies", "99")
    expressions = build(userdata)

    assert expressions["ShortcutView_Movies_HasPluginOverride"] == (
        "String.IsEqual(Container.PluginName,plugin.a)"
        " | String.IsEqual(Container.PluginName,plugin.b)"
    )


def test_split_defaults_without_overrides() -> None:
    """Different library and plugin defaults split on whether an add-on is listing."""
    expressions = build(UserData(), plugin_default="51")

    assert "ShortcutView_Movies_HasPluginOverride" not in expressions
    assert expressions["ShortcutView_50"] == f"[{MOVIES} + {NO_PLUGIN}]"
    assert expressions["ShortcutView_51"] == f"[{MOVIES} + !{NO_PLUGIN}]"
    assert expressions["ShortcutView_52"] == "False"
    assert expressions["ShortcutView_52_Include"] == "False"


def test_generic_plugin_selection_replaces_plugin_default() -> None:
    """A user's generic plugin view replaces the rule's plugin default."""
    userdata = UserData()
    userdata.set_view("plugins", "movies", "52")
    expressions = build(userdata, plugin_default="51")

    assert expressions["ShortcutView_51"] == "False"
    assert expressions["ShortcutView_52"] == f"[{MOVIES} + !{NO_PLUGIN}]"


def test_no_content_rules_builds_nothing() -> None:
    """Without content rules there are no view expressions."""
    assert ViewExpressionBuilder(ViewConfig(), UserData()).build() == []
