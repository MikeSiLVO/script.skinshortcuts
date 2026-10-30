"""Content source="addons" must query both plugin and script types."""

from __future__ import annotations

import pytest

from skinshortcuts.models.menu import Content
from skinshortcuts.providers.content import ContentProvider

PLUGINSOURCE = "xbmc.python.pluginsource"
SCRIPT = "xbmc.python.script"


def _provider(responses: dict[str, list[dict]]):
    """ContentProvider whose JSON-RPC answers from a {addon_type: addons} map, plus its call log."""
    provider = ContentProvider()
    calls: list[dict] = []

    def fake(method: str, params: dict | None = None):
        assert method == "Addons.GetAddons"
        params = params or {}
        calls.append(params)
        return {"addons": responses.get(params.get("type", ""), [])}

    provider._jsonrpc = fake  # type: ignore[method-assign]
    return provider, calls


def test_queries_both_types_with_content():
    provider, calls = _provider({})

    provider.resolve(Content(source="addons", target="videos"))

    assert [(c["type"], c["content"]) for c in calls] == [
        (PLUGINSOURCE, "video"),
        (SCRIPT, "video"),
    ]


def test_script_first_addon_is_found():
    provider, _ = _provider(
        {PLUGINSOURCE: [
            {"addonid": "script.texturemaker", "name": "Texture Maker", "type": PLUGINSOURCE}
        ]}
    )

    result = provider.resolve(Content(source="addons", target="pictures"))

    assert [s.label for s in result] == ["Texture Maker"]


def test_both_types_merge_and_dedupe():
    shared = {"addonid": "plugin.video.themoviedb.helper", "name": "TMDb Helper"}
    provider, _ = _provider(
        {
            PLUGINSOURCE: [{**shared, "type": PLUGINSOURCE}],
            SCRIPT: [
                {**shared, "type": SCRIPT},
                {"addonid": "script.globalsearch", "name": "Global Search", "type": SCRIPT},
            ],
        }
    )

    result = provider.resolve(Content(source="addons", target="videos"))

    assert [s.label for s in result] == ["TMDb Helper", "Global Search"]
    # first query wins the duplicate; it stays browsable, not a launcher
    assert result[0].browse_path == "plugin://plugin.video.themoviedb.helper/"
    assert result[0].action == ""


def test_type_drives_browse_vs_runaddon():
    provider, _ = _provider(
        {
            PLUGINSOURCE: [{"addonid": "plugin.video.x", "name": "Plugin X", "type": PLUGINSOURCE}],
            SCRIPT: [{"addonid": "script.y", "name": "Script Y", "type": SCRIPT}],
        }
    )

    result = provider.resolve(Content(source="addons", target="videos"))
    by_label = {s.label: s for s in result}

    assert by_label["Plugin X"].browse_path == "plugin://plugin.video.x/"
    assert by_label["Plugin X"].browse_window == "videos"
    assert by_label["Script Y"].action == "RunAddon(script.y)"
    assert by_label["Script Y"].browse_path == ""


@pytest.mark.parametrize(
    ("target", "content"),
    [("videos", "video"), ("music", "audio"), ("pictures", "image"), ("programs", "executable")],
)
def test_target_aliases_map_to_content(target: str, content: str):
    provider, calls = _provider({})

    provider.resolve(Content(source="addons", target=target))

    assert {c["content"] for c in calls} == {content}
