"""Property condition grammar, case by case."""

from __future__ import annotations

import pytest

from skinshortcuts.conditions import evaluate_condition, expand_compact_or

MOVIE = {
    "widgetPath": "videodb://movies/titles/",
    "widgetType": "movies",
    "widgetStyle": "Panel",
    "widgetArt": "Poster",
    "disabled": "True",
    "flagOff": "false",
    "flagOn": "TRUE",
    "blank": "",
    "suffix": ".2",
    "widgetType.2": "episodes",
    "plugin": "plugin://plugin.video.youtube/?action=list&x=1",
}

CASES = [
    ("", True),
    ("   ", True),
    ("widgetPath", True),
    ("missing", False),
    ("blank", False),
    ("flagOff", False),
    ("flagOn", True),
    ("!widgetPath", False),
    ("!missing", True),
    ("!flagOff", True),
    ("NOT widgetPath", False),
    ("NOT missing", True),
    # literal booleans after substitution
    ("true", True),
    ("false", False),
    ("True=true", True),
    ("false=true", False),
    ("widgetPath EMPTY", False),
    ("missing EMPTY", True),
    ("blank EMPTY", True),
    ("!widgetPath EMPTY", True),
    ("NOT widgetPath EMPTY", True),
    ("widgetType=movies", True),
    ("widgetType=Movies", False),
    ("widgetType = movies", True),
    ("widgetType EQUALS movies", True),
    ("widgetType=tvshows", False),
    ("missing=", True),
    ("widgetType=", False),
    ("suffix=.2", True),
    ("!widgetType=movies", False),
    ("NOT widgetType EQUALS movies", False),
    # boolean values compare without case, others exactly
    ("disabled=true", True),
    ("disabled=TRUE", True),
    ("flagOff=False", True),
    ("widgetPath~videodb://", True),
    ("widgetPath CONTAINS movies", True),
    ("widgetPath~musicdb://", False),
    ("missing~x", False),
    ("!widgetPath~musicdb://", True),
    # values holding the other operator
    ("plugin~action=list", True),
    ("plugin~action=play", False),
    ("plugin=plugin://plugin.video.youtube/?action=list&x=1", True),
    ("plugin~?action=list&x=1", True),
    ("widgetType IN movies,episodes,tvshows", True),
    ("widgetType IN episodes, tvshows", False),
    ("widgetType IN episodes , movies", True),
    ("!widgetType IN movies,episodes", False),
    ("disabled IN false,TRUE", True),
    ("missing IN a,b", False),
    ("widgetType=movies + widgetStyle=Panel", True),
    ("widgetType=movies + widgetStyle=List", False),
    ("widgetType EQUALS movies AND widgetStyle EQUALS Panel", True),
    ("widgetType=tvshows | widgetType=movies", True),
    ("widgetType=tvshows | widgetType=albums", False),
    ("widgetType EQUALS tvshows OR widgetType EQUALS movies", True),
    # AND binds tighter than OR
    ("widgetType=tvshows + widgetStyle=Panel | widgetArt=Poster", True),
    ("widgetType=movies | widgetType=tvshows + missing", True),
    ("[widgetType=movies | widgetType=tvshows] + missing", False),
    ("widgetType=episodes | movies | tvshows", True),
    ("widgetType=episodes | albums", False),
    ("widgetType=albums | widgetStyle=List | Panel", True),
    ("widgetType=albums | widgetStyle=List | Wide", False),
    ("widgetType=tvshows | movies + widgetStyle=List", False),
    ("[widgetType=tvshows | movies] + widgetStyle=Panel", True),
    ("widgetPath~musicdb | videodb", True),
    ("!widgetType=movies | tvshows", False),
    # negation reaches only the next term
    ("!missing + widgetArt=Poster", True),
    ("NOT missing AND widgetArt EQUALS Poster", True),
    ("!widgetPath + widgetArt=Poster", False),
    ("![widgetType=movies | widgetType=tvshows]", False),
    ("![widgetType=albums | widgetType=tvshows]", True),
    ("[widgetType=movies | widgetType=tvshows] + [widgetStyle=Panel | widgetStyle=Wide]", True),
    ("![widgetType=movies | [widgetType=tvshows + widgetStyle=Panel]]", False),
    ("[[widgetType=movies]]", True),
    ("[widgetType=movies] + [widgetStyle=List]", False),
    ("[widgetType=albums] | [widgetStyle=Panel]", True),
    ("widgetType.2=episodes", True),
    ("widgetType.2 IN movies,episodes", True),
    ("widgetType.3 EMPTY", True),
]


@pytest.mark.parametrize(("condition", "expected"), CASES)
def test_grammar(condition, expected):
    assert evaluate_condition(condition, MOVIE) is expected


def test_keywords_are_uppercase_only():
    assert evaluate_condition("widgetType equals movies", MOVIE) is False
    assert evaluate_condition("widgetType=tvshows or widgetType=movies", MOVIE) is False


def test_keyword_inside_value_is_rewritten():
    props = {"widgetPath": "plugin.AND.test"}
    assert evaluate_condition("widgetPath=plugin.AND.test", props) is False
    assert evaluate_condition("widgetPath=plugin_AND_test", {"widgetPath": "plugin_AND_test"})


@pytest.mark.parametrize(("compact", "full"), [
    ("widgetType=movies | episodes", "widgetType=movies | widgetType=episodes"),
    ("a=1 | 2 + b=3", "a=1 | a=2 + b=3"),
    ("a~x | y", "a~x | a~y"),
    ("[a=1 | 2] + b", "[a=1 | a=2] + b"),
    ("!a=1 | 2", "!a=1 | a=2"),
    ("a=1 | b=2 | 3", "a=1 | b=2 | b=3"),
    ("a | b", "a | b"),
    ("", ""),
])
def test_compact_or_expansion(compact, full):
    assert expand_compact_or(compact) == full
