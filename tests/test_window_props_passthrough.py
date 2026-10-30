"""Paired prop=NAME,value=VAL args set on Home for picker lifecycle, cleared after dispatch."""

from __future__ import annotations

import sys
from unittest.mock import patch

import xbmcgui

from skinshortcuts.entry import main


def test_main_sets_single_prop_pair_on_home(monkeypatch):
    home = xbmcgui.Window(10000)
    home.props.clear()

    monkeypatch.setattr(
        sys, "argv", ["script.skinshortcuts", "type=unknown&prop=SpotlightWidget&value=home"]
    )

    with patch("skinshortcuts.entry._dispatch") as dispatch:
        def assert_set_during_dispatch(args):
            assert home.getProperty("SpotlightWidget") == "home"
            assert "prop" not in args
            assert "value" not in args

        dispatch.side_effect = assert_set_during_dispatch
        main()

    assert home.getProperty("SpotlightWidget") == ""


def test_main_sets_multiple_prop_pairs_on_home(monkeypatch):
    home = xbmcgui.Window(10000)
    home.props.clear()

    monkeypatch.setattr(
        sys,
        "argv",
        ["script.skinshortcuts", "type=unknown&prop=X&value=1&prop=Y&value=2"],
    )

    with patch("skinshortcuts.entry._dispatch") as dispatch:
        def assert_set_during_dispatch(_args):
            assert home.getProperty("X") == "1"
            assert home.getProperty("Y") == "2"

        dispatch.side_effect = assert_set_during_dispatch
        main()

    assert home.getProperty("X") == ""
    assert home.getProperty("Y") == ""


def test_main_clears_props_even_when_dispatch_raises(monkeypatch):
    home = xbmcgui.Window(10000)
    home.props.clear()

    monkeypatch.setattr(
        sys, "argv", ["script.skinshortcuts", "type=unknown&prop=X&value=1&prop=Y&value=2"]
    )

    def boom(_args):
        raise RuntimeError("dispatch failed")

    with patch("skinshortcuts.entry._dispatch", side_effect=boom):
        try:
            main()
        except RuntimeError:
            pass

    assert home.getProperty("X") == ""
    assert home.getProperty("Y") == ""


def test_main_unpaired_prop_defaults_to_true(monkeypatch):
    home = xbmcgui.Window(10000)
    home.props.clear()

    monkeypatch.setattr(sys, "argv", ["script.skinshortcuts", "type=unknown&prop=BoolFlag"])

    with patch("skinshortcuts.entry._dispatch") as dispatch:
        def assert_set_during_dispatch(_args):
            assert home.getProperty("BoolFlag") == "true"

        dispatch.side_effect = assert_set_during_dispatch
        main()

    assert home.getProperty("BoolFlag") == ""


def test_main_comma_form_supports_pairs(monkeypatch):
    home = xbmcgui.Window(10000)
    home.props.clear()

    monkeypatch.setattr(
        sys,
        "argv",
        ["script.skinshortcuts", "type=unknown", "prop=A", "value=1", "prop=B", "value=2"],
    )

    with patch("skinshortcuts.entry._dispatch") as dispatch:
        def assert_set_during_dispatch(_args):
            assert home.getProperty("A") == "1"
            assert home.getProperty("B") == "2"

        dispatch.side_effect = assert_set_during_dispatch
        main()

    assert home.getProperty("A") == ""
    assert home.getProperty("B") == ""
