"""Items inserts: an item with every insert empty builds nothing; a mistyped one is named."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import Menu, MenuItem

TEMPLATES = """<templates>
  <template items="widgets">
    <controls><control type="button"><label>$PROPERTY[label]</label></control></controls>
  </template>
  <template items="extras">
    <controls><control type="image"><texture>$PROPERTY[name]</texture></control></controls>
  </template>
  <template include="Row" menu="mainmenu">
    <controls>
      <control type="group"><description>$PROPERTY[name]</description>%s</control>
    </controls>
  </template>
</templates>"""


def build(
    tmp_path: Path, inserts: str, monkeypatch: pytest.MonkeyPatch
) -> tuple[list[str], list[str]]:
    """Items that built a group in the Row include, and the notifications fired."""
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES % inserts, encoding="utf-8")
    notified: list[str] = []
    monkeypatch.setattr(
        "skinshortcuts.builders.template.notify", lambda h, m, *_: notified.append(f"{h}: {m}")
    )
    main = Menu(
        name="mainmenu",
        items=[MenuItem(name="movies", label="Movies"), MenuItem(name="music", label="Music")],
    )
    widgets = Menu(name="movies.widgets", items=[MenuItem(name="w1", label="Recent")])
    root = TemplateBuilder(load_templates(path), [main, widgets]).build()
    include = root.find("include[@name='skinshortcuts-template-Row']")
    assert include is not None
    built = [g.findtext("description") or "" for g in include.iter("control")]
    return [name for name in built if name], notified


def test_item_with_one_filled_insert_keeps_its_siblings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inserts = "<skinshortcuts insert='widgets' /><skinshortcuts insert='extras' />"
    assert build(tmp_path, inserts, monkeypatch)[0] == ["movies"]


def test_item_with_every_insert_empty_builds_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    built, _ = build(tmp_path, "<skinshortcuts insert='widgets' />", monkeypatch)
    assert built == ["movies"]


def test_mistyped_insert_beside_a_filled_one_is_notified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    inserts = "<skinshortcuts insert='widgets' /><skinshortcuts insert='widgts' />"
    _, notified = build(tmp_path, inserts, monkeypatch)
    assert any("widgts" in n for n in notified)


def test_mistyped_only_insert_is_notified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    built, notified = build(tmp_path, "<skinshortcuts insert='widgts' />", monkeypatch)
    assert built == []
    assert any("widgts" in n for n in notified)
