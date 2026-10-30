"""RunScript arguments: an & first argument, later comma arguments and prop/value pairing."""

from __future__ import annotations

import sys

import pytest
import xbmcgui

from skinshortcuts import entry


def run(monkeypatch: pytest.MonkeyPatch, *argv: str) -> tuple[dict[str, str], dict[str, str]]:
    """Run main() with Kodi's argv, returning the dispatched args and Home during dispatch."""
    home = xbmcgui.Window(10000)
    home.props.clear()
    seen: dict[str, dict[str, str]] = {}

    def dispatch(args: dict[str, str]) -> None:
        seen["args"] = dict(args)
        seen["home"] = dict(home.props)

    monkeypatch.setattr(sys, "argv", ["default.py", *argv])
    monkeypatch.setattr(entry, "_dispatch", dispatch)
    entry.main()
    return seen["args"], seen["home"]


def test_comma_form_pairs_by_position(monkeypatch: pytest.MonkeyPatch) -> None:
    _args, home = run(monkeypatch, "type=unknown", "prop=a", "value=", "prop=b", "value=2")
    assert home == {"a": "", "b": "2"}


def test_comma_values_are_taken_as_written(monkeypatch: pytest.MonkeyPatch) -> None:
    _args, home = run(monkeypatch, "type=unknown", "prop=x", "value=Rock %26 Roll")
    assert home == {"x": "Rock %26 Roll"}


def test_comma_arguments_after_an_ampersand_first_argument(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    args, home = run(
        monkeypatch, "type=manage&menu=mainmenu", "prop=widgetContext", "value=spotlight"
    )
    assert args == {"type": "manage", "menu": "mainmenu"}
    assert home == {"widgetContext": "spotlight"}


def test_ampersand_in_first_comma_value_keeps_the_type(monkeypatch: pytest.MonkeyPatch) -> None:
    args, _home = run(monkeypatch, "skinLabel=A&B", "type=skinstring")
    assert args.get("type") == "skinstring"


def test_query_form_pairs_by_position(monkeypatch: pytest.MonkeyPatch) -> None:
    _args, home = run(monkeypatch, "type=unknown&prop=a&value=&prop=b&value=2")
    assert home == {"a": "", "b": "2"}
