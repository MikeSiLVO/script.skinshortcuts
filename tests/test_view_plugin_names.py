"""The plugin view picker names an add-on by its id when the reply carries no name."""

from __future__ import annotations

import json

import pytest
import xbmc

from skinshortcuts.dialog import views


def test_nameless_addon_falls_back_to_its_id(monkeypatch: pytest.MonkeyPatch) -> None:
    reply = json.dumps({"result": {"addons": [{"addonid": "plugin.a"}]}})
    monkeypatch.setattr(xbmc, "executeJSONRPC", lambda _request: reply, raising=False)
    assert views._get_video_plugins() == [("plugin.a", "plugin.a")]
