"""Template markers the builder cannot resolve are left out and named in a notification."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import Menu, MenuItem

TEMPLATES = """<templates>
  <includes>
    <include name="WidgetRow"><control type="image"><texture>a.png</texture></control></include>
  </includes>
  <template include="Row">
    <controls>%s</controls>
  </template>
</templates>"""


def build(
    tmp_path: Path, controls: str, monkeypatch: pytest.MonkeyPatch, container: str | None = None
) -> tuple[str, list[str]]:
    """The built Row include as text, and the notifications fired."""
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES % controls, encoding="utf-8")
    notified: list[str] = []
    monkeypatch.setattr(
        "skinshortcuts.builders.template.notify", lambda h, m, *_: notified.append(f"{h}: {m}")
    )
    item = MenuItem(name="movies", label="Movies")
    menu = Menu(name="mainmenu", items=[item], container=container)
    root = TemplateBuilder(load_templates(path), [menu]).build()
    include = root.find("include[@name='skinshortcuts-template-Row']")
    assert include is not None
    return ET.tostring(include, encoding="unicode"), notified


def test_known_include_expands(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    text, _ = build(tmp_path, "<skinshortcuts include='WidgetRow' />", monkeypatch)
    assert "a.png" in text
    assert "skinshortcuts" not in text.replace("skinshortcuts-template-Row", "")


def test_visibility_with_container_becomes_visible(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    controls = "<control type='button'><skinshortcuts>visibility</skinshortcuts></control>"
    text, _ = build(tmp_path, controls, monkeypatch, container="9000")
    assert "<visible>String.IsEqual(Container(9000).ListItem.Property(name),movies)" in text


def test_unknown_include_is_left_out_and_notified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    controls = "<control type='group'><skinshortcuts include='WidgetRo' /></control>"
    text, notified = build(tmp_path, controls, monkeypatch)
    assert "WidgetRo" not in text
    assert any("WidgetRo" in n for n in notified)


def test_visibility_without_container_is_left_out_and_notified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    controls = "<control type='button'><skinshortcuts>visibility</skinshortcuts></control>"
    text, notified = build(tmp_path, controls, monkeypatch)
    assert "<skinshortcuts>" not in text
    assert any("mainmenu" in n for n in notified)


def test_unknown_include_log_suggests_a_close_match(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES % "<skinshortcuts include='WidgetRo' />", encoding="utf-8")
    details: list[str] = []
    monkeypatch.setattr(
        "skinshortcuts.builders.template.notify", lambda _h, _m, detail: details.append(detail)
    )
    menu = Menu(name="mainmenu", items=[MenuItem(name="movies", label="Movies")])
    TemplateBuilder(load_templates(path), [menu]).build()
    assert any("did you mean 'WidgetRow'?" in d for d in details)
