"""The addons content placeholder carries its path like any other picker option."""
from __future__ import annotations

from unittest.mock import patch

from skinshortcuts.dialog import pickers
from skinshortcuts.dialog.pickers import PickersMixin, stamp_picker_props
from skinshortcuts.models.menu import Content, Shortcut
from skinshortcuts.models.widget import Widget
from skinshortcuts.providers.content import ResolvedShortcut


class _FakeLI:
    """ListItem stand-in keeping properties readable."""

    def __init__(self) -> None:
        self._p: dict[str, str] = {}

    def setProperty(self, n: str, v: str) -> None:  # noqa: N802
        self._p[n] = v

    def setArt(self, _a) -> None:  # noqa: N802
        pass

    def getProperty(self, n: str) -> str:  # noqa: N802
        return self._p.get(n, "")


class _FakeProvider:
    """Content provider stand-in resolving one pluginsource video add-on."""

    def __init__(self, *_a, **_k) -> None:
        pass

    def resolve(self, _content):
        return [
            ResolvedShortcut(label="TMDb Helper", action="", icon="t",
                             browse_path="plugin://plugin.video.themoviedb.helper/",
                             browse_window="videos"),
        ]


class _Picker(PickersMixin):
    """PickersMixin with no manager, for calling its filters directly."""

    def __init__(self) -> None:
        self.manager = None  # type: ignore[assignment]
        self.shortcuts_path = ""
        self.menu_id = ""


def _stamped(picker, leaf, resolver, prop="path", target="video"):
    """Property stamped on each addons picker item, by item name."""
    items = picker._filter_picker_items(
        [Content(source="addons", target=target)], {},
        leaf_types=(leaf,), group_types=(), content_resolver=resolver,
    )
    out = {}
    for it in items:
        li = _FakeLI()
        stamp_picker_props(li, it)
        out[it.name] = li.getProperty(prop)
    return out


def _paths(picker, leaf, resolver):
    """Path stamped on each addons picker item, by item name."""
    return _stamped(picker, leaf, resolver)


def test_addons_placeholder_stamps_category_path():
    picker = _Picker()
    with patch.object(pickers, "ContentProvider", _FakeProvider):
        sc = _paths(picker, Shortcut, picker._resolve_content_to_shortcuts)
        wd = _paths(picker, Widget, picker._resolve_content_to_widgets)

    for got in (sc, wd):
        assert got["content-placeholder-addons-video"] == "addons://sources/video/"
        assert got["dynamic-addons-0"] == "plugin://plugin.video.themoviedb.helper/"


def test_addons_placeholder_widget_lists_addons():
    """The category path lists add-ons, whatever window they open in."""
    picker = _Picker()
    with patch.object(pickers, "ContentProvider", _FakeProvider):
        for target in ("video", "image", "executable"):
            got = _stamped(picker, Widget, picker._resolve_content_to_widgets,
                           prop="type", target=target)
            name = f"content-placeholder-addons-{target}"
            assert got[name] == "addons", f"{target} placeholder must not carry its target"
