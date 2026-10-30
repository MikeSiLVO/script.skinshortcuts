"""A comparison splits at its first operator."""

from __future__ import annotations

from skinshortcuts.conditions import evaluate_condition

PATH = "plugin://plugin.video.youtube/?action=list"


def test_contains_value_with_equals():
    props = {"widgetPath": PATH}
    assert evaluate_condition("widgetPath~action=list", props)
    assert evaluate_condition("widgetPath~youtube/?action=list", props)
    assert not evaluate_condition("widgetPath~action=play", props)
    assert evaluate_condition("!widgetPath~action=play", props)


def test_equals_value_with_tilde():
    props = {"widgetPath": "special://home/~cache"}
    assert evaluate_condition("widgetPath=special://home/~cache", props)
    assert not evaluate_condition("widgetPath=special://home/~other", props)


def test_equals_value_with_equals():
    assert evaluate_condition(f"widgetPath={PATH}", {"widgetPath": PATH})


def test_or_with_equals_in_values():
    props = {"widgetPath": PATH}
    assert evaluate_condition("widgetPath~action=play | widgetPath~action=list", props)
