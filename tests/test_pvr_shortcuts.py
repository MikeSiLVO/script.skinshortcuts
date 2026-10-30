"""PVR channel shortcuts play the channel through the script."""

from __future__ import annotations

import json

import pytest
import xbmc

from skinshortcuts import entry
from skinshortcuts.models.menu import Content
from skinshortcuts.providers.content import ContentProvider


def pvr_rpc(_method: str, _params: dict | None = None) -> dict:
    """One TV channel, in the shape PVR.GetChannels returns it."""
    return {"channels": [{"channelid": 7, "channelnumber": 1, "label": "News", "thumbnail": ""}]}


@pytest.mark.parametrize("target", ["tv", "radio", ""])
def test_channel_plays_through_runscript(monkeypatch: pytest.MonkeyPatch, target: str) -> None:
    monkeypatch.setattr(xbmc, "getCondVisibility", lambda _expr: True)
    provider = ContentProvider()
    monkeypatch.setattr(provider, "_jsonrpc", pvr_rpc)
    [shortcut] = provider.resolve(Content(source="pvr", target=target))
    assert shortcut.action == "RunScript(script.skinshortcuts,type=playchannel,channel=7)"


def dispatch(monkeypatch: pytest.MonkeyPatch, channel: str, reply: dict) -> list[dict]:
    """Dispatch playchannel on a supported skin, returning the JSON-RPC requests it sent."""
    sent: list[dict] = []

    def execute(request: str) -> str:
        sent.append(json.loads(request))
        return json.dumps(reply)

    monkeypatch.setattr(xbmc, "executeJSONRPC", execute, raising=False)
    monkeypatch.setattr(entry, "_skin_supported", lambda *_a, **_k: True)
    entry._dispatch({"type": "playchannel", "channel": channel})
    return sent


def test_playchannel_opens_the_channel_by_id(monkeypatch: pytest.MonkeyPatch) -> None:
    [request] = dispatch(monkeypatch, "7", {"result": "OK"})
    assert request["method"] == "Player.Open"
    assert request["params"] == {"item": {"channelid": 7}}


def test_playchannel_warns_on_an_unknown_channel(monkeypatch: pytest.MonkeyPatch) -> None:
    logged: list[str] = []
    monkeypatch.setattr(entry.log, "warning", logged.append)
    dispatch(monkeypatch, "7", {"error": {"code": -32602, "message": "Invalid params."}})
    assert logged and "PVR channel 7" in logged[0]


def test_playchannel_sends_nothing_without_an_id(monkeypatch: pytest.MonkeyPatch) -> None:
    assert dispatch(monkeypatch, "news", {"result": "OK"}) == []
