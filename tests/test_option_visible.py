"""A property option is offered only while its Kodi visible condition holds."""

from __future__ import annotations

from pathlib import Path

import pytest
import xbmc
from harness import harness_fixture, open_root, write_skin  # noqa: F401

from skinshortcuts.dialog import properties as dialog_properties
from skinshortcuts.loaders.property import load_properties

MENUS = """<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>Noop</action></item>
  </menu>
</menus>"""

PROPERTIES = """<properties>
  <property name="shelfLayout">
    <options>
      <option value="two" label="Two" />
      <option value="threelarge" label="Three large" visible="Skin.HasSetting(VerticalHome)" />
    </options>
  </property>
  <buttons>
    <button id="2101" property="shelfLayout" showNone="false" />
  </buttons>
</properties>"""


def test_loader_reads_the_option_visible(tmp_path: Path) -> None:
    skin = write_skin(tmp_path, MENUS, properties=PROPERTIES)
    prop = load_properties(skin / "properties.xml").get_property("shelfLayout")
    assert prop is not None
    assert [opt.visible for opt in prop.options] == ["", "Skin.HasSetting(VerticalHome)"]


@pytest.mark.parametrize(
    ("vertical", "offered"), [(False, ["Two"]), (True, ["Two", "Three large"])]
)
def test_picker_offers_an_option_only_while_visible(
    harness, monkeypatch, tmp_path: Path, vertical: bool, offered: list[str]
) -> None:
    monkeypatch.setattr(
        xbmc, "getCondVisibility", lambda expr: vertical and expr == "Skin.HasSetting(VerticalHome)"
    )
    seen: list[str] = []

    def select(_kind, _title, listitems, **_kwargs):
        seen.extend(listitem.label for listitem in listitems)
        return -1

    monkeypatch.setattr(dialog_properties, "picker_select", select)
    dialog = open_root(write_skin(tmp_path, MENUS, properties=PROPERTIES), tmp_path)
    dialog._handle_property_button(2101)
    assert seen == offered
