"""A submenu template with empty or missing controls still defines its include."""

from __future__ import annotations

from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import Menu, MenuItem

TEMPLATES = """<templates>
  <submenu include="Empty" level="1"><controls /></submenu>
  <submenu include="Bare" level="1" />
</templates>"""


@pytest.mark.parametrize("name", ["Empty", "Bare"])
def test_include_is_defined_with_a_description(tmp_path: Path, name: str) -> None:
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES, encoding="utf-8")
    main = Menu(name="mainmenu", items=[MenuItem(name="movies", label="Movies")])
    sub = Menu(name="mainmenu/movies", items=[MenuItem(name="a", label="A")], is_submenu=True)
    root = TemplateBuilder(load_templates(path), [main, sub]).build()
    include = root.find(f"include[@name='skinshortcuts-{name}']")
    assert include is not None
    assert [child.tag for child in include] == ["description"]
