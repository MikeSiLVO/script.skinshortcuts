"""A widget assigned to a slot carries its <limit>/<sortby>/<sortorder> like a list item does."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from skinshortcuts.config import SkinConfig


WIDGETS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<widgets>
  <widget name="recent-movies" label="Recently Added" type="movies" target="videos">
    <path>videodb://recentlyaddedmovies/</path>
    <limit>25</limit>
    <sortby>dateadded</sortby>
    <sortorder>descending</sortorder>
  </widget>
  <widget name="plain-movies" label="All Movies" type="movies" target="videos">
    <path>videodb://movies/titles/</path>
  </widget>
</widgets>
"""

TEMPLATES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <template include="test" menu="mainmenu">
    <property name="lim" from="widgetLimit" />
    <property name="sortby" from="widgetSortBy" />
    <property name="order" from="widgetSortOrder" />
    <controls>
      <control type="label">
        <label>[$PROPERTY[lim]][$PROPERTY[sortby]][$PROPERTY[order]]</label>
      </control>
    </controls>
  </template>
</templates>
"""


def _menus(widget: str, slot: str = "widget") -> str:
    """Menus XML whose movies item puts a widget in a given slot."""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies">
      <label>Movies</label>
      <action>ActivateWindow(Videos,videodb://movies/titles/,return)</action>
      <property name="{slot}">{widget}</property>
    </item>
  </menu>
</menus>
"""


def _build(tmp_path: Path, menus: str, templates: bool = False) -> ET.Element:
    """Build includes from given menus, the test widgets and optionally the test templates."""
    shortcuts = tmp_path / "shortcuts"
    shortcuts.mkdir(exist_ok=True)
    (shortcuts / "menus.xml").write_text(menus)
    (shortcuts / "widgets.xml").write_text(WIDGETS_XML)
    if templates:
        (shortcuts / "templates.xml").write_text(TEMPLATES_XML)

    out = tmp_path / "includes.xml"
    SkinConfig.load(shortcuts, load_user=False).build_includes(out)
    return ET.parse(out).getroot()


def _item_properties(root: ET.Element) -> dict[str, str]:
    """Properties on the first built item."""
    item = next(root.iter("item"))
    return {p.get("name", ""): p.text or "" for p in item.findall("property")}


def test_slot_assignment_carries_limit_and_sort(tmp_path: Path):
    props = _item_properties(_build(tmp_path, _menus("recent-movies")))

    assert props["widgetLimit"] == "25"
    assert props["widgetSortBy"] == "dateadded"
    assert props["widgetSortOrder"] == "descending"


def test_numbered_slot_carries_them_too(tmp_path: Path):
    props = _item_properties(_build(tmp_path, _menus("recent-movies", slot="widget.2")))

    assert props["widgetLimit.2"] == "25"
    assert props["widgetSortBy.2"] == "dateadded"
    assert props["widgetSortOrder.2"] == "descending"


def test_widget_without_them_emits_none_of_them(tmp_path: Path):
    props = _item_properties(_build(tmp_path, _menus("plain-movies")))

    assert not [k for k in props if k.startswith(("widgetLimit", "widgetSort"))]


def test_template_reads_them_by_name(tmp_path: Path):
    root = _build(tmp_path, _menus("recent-movies"), templates=True)

    labels = [label.text for label in root.iter("label")]
    assert "[25][dateadded][descending]" in labels


IF_TEMPLATES_XML = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <template include="test" menu="mainmenu">
    <property name="lim" from="widgetLimit" />
    <controls>
      <control type="label">
        <label>$IF[lim THEN $PROPERTY[lim] ELSE 99]</label>
      </control>
    </controls>
  </template>
</templates>
"""


def _if_labels(tmp_path: Path, case: str, widget: str) -> list[str | None]:
    """Labels the $IF default template builds for a widget, in its own case folder."""
    root = tmp_path / case
    shortcuts = root / "shortcuts"
    shortcuts.mkdir(parents=True)
    (shortcuts / "menus.xml").write_text(_menus(widget))
    (shortcuts / "widgets.xml").write_text(WIDGETS_XML)
    (shortcuts / "templates.xml").write_text(IF_TEMPLATES_XML)

    out = root / "includes.xml"
    SkinConfig.load(shortcuts, load_user=False).build_includes(out)
    return [label.text for label in ET.parse(out).getroot().iter("label")]


def test_if_default_uses_the_bare_property_name(tmp_path: Path):
    """The documented default idiom: the condition is the name, not $PROPERTY[name]."""
    assert "99" in _if_labels(tmp_path, "plain", "plain-movies")
    assert "25" in _if_labels(tmp_path, "limited", "recent-movies")
