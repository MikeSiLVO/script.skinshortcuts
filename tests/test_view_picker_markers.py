"""The view picker marks its content type lists `content` and its view list `view`."""

from __future__ import annotations

import pytest
import xbmcgui

from skinshortcuts.dialog import views
from skinshortcuts.models.views import View, ViewConfig, ViewContent
from skinshortcuts.userdata import UserData


class _Item:
    """ListItem stand-in that ignores every call."""

    def __init__(self, *_a, **_k) -> None:
        pass

    def setLabel2(self, _label: str) -> None:  # noqa: N802
        pass

    def setArt(self, _art: dict) -> None:  # noqa: N802
        pass

    def setProperty(self, _key: str, _value: str) -> None:  # noqa: N802
        pass


@pytest.fixture
def selects(monkeypatch: pytest.MonkeyPatch) -> tuple[list[str], list[int]]:
    seen: list[str] = []
    answers: list[int] = []

    class Dialog:
        def select(self, *_a, **_k) -> int:
            seen.append(xbmcgui.Window(10000).getProperty("skinshortcuts-picker"))
            return answers.pop(0)

    monkeypatch.setattr(xbmcgui, "Dialog", Dialog)
    monkeypatch.setattr(xbmcgui, "ListItem", _Item)
    monkeypatch.setattr(views, "LANGUAGE", lambda _id: "%s")
    return seen, answers


CONFIG = ViewConfig(
    views=[View("50", "List")],
    content_rules=[ViewContent("movies", "Movies", "", ["50"], "50")],
)


def test_library_content_list_then_view_list(selects: tuple[list[str], list[int]]) -> None:
    seen, answers = selects
    answers += [0, -1, -1]
    views._browse_source_menu(CONFIG, UserData(), "library", "Library")
    assert seen == ["content", "view", "content"]
    assert xbmcgui.Window(10000).getProperty("skinshortcuts-picker") == ""


def test_plugin_override_marks_only_its_content_and_view_lists(
    selects: tuple[list[str], list[int]], monkeypatch: pytest.MonkeyPatch
) -> None:
    seen, answers = selects
    monkeypatch.setattr(views, "_get_video_plugins", lambda: [("plugin.a", "A")])
    answers += [0, 0, -1]
    views._add_plugin_override(CONFIG, UserData())
    assert seen == ["", "content", "view"]
