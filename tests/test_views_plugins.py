"""The plugin view picker's add-on list survives a bad or empty JSON-RPC reply."""

from __future__ import annotations

import json

import pytest
import xbmc

from skinshortcuts.dialog import views


def _reply(payload):
    """Stand-in executeJSONRPC returning a payload, JSON-encoded unless already text."""
    return lambda _request: payload if isinstance(payload, str) else json.dumps(payload)


@pytest.mark.parametrize("payload", [
    "not json",
    {"error": {"code": -32602}},
    {"result": {"addons": None}},
    {"result": {}},
    {"result": None},
])
def test_bad_replies_give_empty_list(monkeypatch, payload):
    monkeypatch.setattr(xbmc, "executeJSONRPC", _reply(payload), raising=False)
    assert views._get_video_plugins() == []


def test_addons_sorted_by_name(monkeypatch):
    addons = [
        {"addonid": "plugin.b", "name": "beta"},
        {"addonid": "plugin.a", "name": "Alpha"},
    ]
    monkeypatch.setattr(
        xbmc, "executeJSONRPC", _reply({"result": {"addons": addons}}), raising=False
    )
    assert views._get_video_plugins() == [("plugin.a", "Alpha"), ("plugin.b", "beta")]
