"""The onclick marker writes the item's actions in their documented order, conditions kept."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from skinshortcuts.builders.template import TemplateBuilder
from skinshortcuts.loaders.menu import load_menus
from skinshortcuts.loaders.template import load_templates

MENUS = """<menus><menu name="buttons" container="9000">
<defaults>
  <action when="after">AfterAction()</action>
  <action when="before">Dialog.Close(all,true)</action>
  <action when="after" condition="Window.IsVisible(Home)">SetProperty(done,1,Home)</action>
</defaults>
<item name="settings"><label>Settings</label>
  <action>ActivateWindow(Settings)</action>
  <action condition="System.Platform.Windows">WindowsAction()</action>
</item>
</menu></menus>"""

TEMPLATES = """<templates><template include="Buttons" menu="buttons">
<controls><control type="button" id="$PROPERTY[id]">
  <label>$PROPERTY[label]</label>
  <skinshortcuts>onclick</skinshortcuts>
  <visible>System.CanPowerDown</visible>
</control></controls>
</template></templates>"""


def build(tmp_path: Path) -> ET.Element:
    """The button control the template builds for the one item."""
    (tmp_path / "menus.xml").write_text(MENUS, encoding="utf-8")
    (tmp_path / "templates.xml").write_text(TEMPLATES, encoding="utf-8")
    menus = load_menus(str(tmp_path / "menus.xml"))
    root = TemplateBuilder(load_templates(str(tmp_path / "templates.xml")), menus.menus).build()
    control = root.find("include/control")
    assert control is not None
    return control


def test_actions_follow_the_documented_order(tmp_path: Path) -> None:
    """Actions follow before defaults, conditional, unconditional, then after defaults."""
    onclicks = [(o.get("condition"), o.text) for o in build(tmp_path).iter("onclick")]
    assert onclicks == [
        (None, "Dialog.Close(all,true)"),
        ("System.Platform.Windows", "WindowsAction()"),
        (None, "ActivateWindow(Settings)"),
        (None, "AfterAction()"),
        ("Window.IsVisible(Home)", "SetProperty(done,1,Home)"),
    ]


def test_marker_is_replaced_in_place(tmp_path: Path) -> None:
    """The marker is replaced by the onclicks, between the same siblings."""
    assert [child.tag for child in build(tmp_path)] == ["label", *["onclick"] * 5, "visible"]
