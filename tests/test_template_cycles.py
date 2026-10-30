"""A template reference that leads back to itself stops the loop and names it in a notification."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.models.menu import Menu, MenuItem

TEMPLATES = """<templates>
  <expressions>
    <expression name="loopA">$EXP[loopB] | widgetPath</expression>
    <expression name="loopB">$EXP[loopA]</expression>
  </expressions>
  <includes>
    <include name="Self">
      <control type="image"><texture>a.png</texture></control>
      <skinshortcuts include="Self" />
    </include>
    <include name="RowA">
      <control type="image"><texture>a.png</texture></control>
      <skinshortcuts include="RowB" />
    </include>
    <include name="RowB">
      <control type="label"><label>b</label></control>
      <skinshortcuts include="RowA" />
    </include>
  </includes>
  <variables>
    <variable name="Plain"><value>x</value></variable>
    <variableGroup name="GroupA">
      <variable content="Plain" />
      <variableGroup content="GroupB" />
    </variableGroup>
    <variableGroup name="GroupB">
      <variableGroup content="GroupA" />
    </variableGroup>
  </variables>
  <template include="%s">
    %s
  </template>
</templates>"""

BODIES = {
    "expression": "<condition>$EXP[loopA]</condition><controls><control type='button'/></controls>",
    "self-include": "<controls><skinshortcuts include='Self' /></controls>",
    "include-chain": "<controls><skinshortcuts include='RowA' /></controls>",
    "variable-group": "<variableGroup content='GroupA' />",
}


@pytest.fixture
def shallow_stack():
    """Keep a runaway recursion short."""
    limit = sys.getrecursionlimit()
    sys.setrecursionlimit(400)
    yield
    sys.setrecursionlimit(limit)


def build(tmp_path: Path, body: str, monkeypatch: pytest.MonkeyPatch) -> list[str] | None:
    """Notifications from building one template over a one-item menu; None if it recursed."""
    path = tmp_path / "templates.xml"
    path.write_text(TEMPLATES % ("Row", body), encoding="utf-8")
    notified: list[str] = []
    monkeypatch.setattr(
        "skinshortcuts.builders.template.notify", lambda h, m, *_: notified.append(f"{h}: {m}")
    )
    item = MenuItem(name="movies", label="Movies", properties={"widgetPath": "x"})
    builder = TemplateBuilder(load_templates(path), [Menu(name="mainmenu", items=[item])])
    try:
        builder.build()
    except RecursionError:
        return None
    return notified


@pytest.mark.parametrize(
    ("case", "name"),
    [
        ("expression", "loop"),
        ("self-include", "Self"),
        ("include-chain", "Row"),
        ("variable-group", "Group"),
    ],
)
def test_circular_reference_builds_and_notifies(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, shallow_stack, case: str, name: str
) -> None:
    notified = build(tmp_path, BODIES[case], monkeypatch)
    assert notified is not None
    assert any(name in text for text in notified)


def test_shared_group_is_not_circular(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    diamond = TEMPLATES.replace(
        """    <variableGroup name="GroupB">
      <variableGroup content="GroupA" />
    </variableGroup>""",
        """    <variableGroup name="GroupB"><variable content="Plain" /></variableGroup>
    <variableGroup name="Top">
      <variableGroup content="GroupA" />
      <variableGroup content="GroupB" />
    </variableGroup>""",
    )
    path = tmp_path / "templates.xml"
    path.write_text(diamond % ("Row", "<variableGroup content='Top' />"), encoding="utf-8")
    notified: list[str] = []
    monkeypatch.setattr(
        "skinshortcuts.builders.template.notify", lambda h, m, *_: notified.append(f"{h}: {m}")
    )
    item = MenuItem(name="movies", label="Movies", properties={"widgetPath": "x"})
    root = TemplateBuilder(load_templates(path), [Menu(name="mainmenu", items=[item])]).build()
    assert notified == []
    assert root.find("variable[@name='Plain']") is not None
