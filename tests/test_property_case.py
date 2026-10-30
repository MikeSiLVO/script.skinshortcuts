"""Property names match without case; written keys take the declared name."""

from __future__ import annotations

import xml.etree.ElementTree as ET

from skinshortcuts.builders.includes import IncludesBuilder
from skinshortcuts.config import SkinConfig
from skinshortcuts.dialog.items import ItemsMixin
from skinshortcuts.dialog.properties import PropertiesMixin
from skinshortcuts.models.menu import Menu, MenuItem
from skinshortcuts.models.property import PropertySchema, SchemaProperty
from skinshortcuts.models.widget import Widget

SORTED = Widget(name="w", label="W", path="p://", limit=40, sort_by="title", sort_order="ascending")
PLAIN = Widget(name="plain", label="Plain", path="plain://")


def _schema() -> PropertySchema:
    """Schema declaring widgetSortby, widgetSortorder and widgetLimit, the first template-only."""
    return PropertySchema(properties={
        "widgetSortby": SchemaProperty(name="widgetSortby", template_only=True),
        "widgetSortorder": SchemaProperty(name="widgetSortorder"),
        "widgetLimit": SchemaProperty(name="widgetLimit"),
    })


def test_get_property_ignores_case():
    schema = _schema()
    assert schema.get_property("widgetSortBy").name == "widgetSortby"
    assert schema.get_property("WIDGETSORTORDER").name == "widgetSortorder"
    assert schema.get_property("widgetPath") is None


def test_declared_name_keeps_slot_and_passes_unknown_through():
    schema = _schema()
    assert schema.declared_name("widgetSortBy.2") == "widgetSortby.2"
    assert schema.declared_name("widgetSortOrder") == "widgetSortorder"
    assert schema.declared_name("widgetPath.3") == "widgetPath.3"


def _config(tmp_path) -> SkinConfig:
    """One-menu config using the test schema and serving SORTED as widget w."""
    (tmp_path / "menus.xml").write_text(
        '<?xml version="1.0"?><menus><menu name="m"><item name="i"><label>I</label>'
        "<action>Noop</action></item></menu></menus>"
    )
    config = SkinConfig.load(tmp_path, load_user=False)
    config.property_schema = _schema()
    config.get_widget = lambda n: SORTED if n == "w" else None
    return config


def test_derived_uses_declared_name(tmp_path):
    item = MenuItem(name="movies", label="M", properties={"widget.2": "w"})
    derived = _config(tmp_path).derived_item_properties(item)
    assert derived["widgetSortby.2"] == "title"
    assert derived["widgetSortorder.2"] == "ascending"
    assert derived["widgetLimit.2"] == "40"
    assert "widgetSortBy.2" not in derived and "widgetSortOrder.2" not in derived


def test_resolve_keeps_user_value_spelled_differently(tmp_path):
    config = _config(tmp_path)
    config.property_schema = PropertySchema()
    item = MenuItem(name="movies", label="M", properties={"widget": "w", "widgetsortby": "year"})
    config.resolve_item_properties(Menu(name="m", items=[item]))
    assert item.properties["widgetsortby"] == "year"
    assert not any(k != "widgetsortby" and k.lower() == "widgetsortby" for k in item.properties)


def test_template_only_matches_any_case():
    item = MenuItem(name="i", label="I", properties={"widgetSortBy.2": "title", "keep": "x"})
    builder = IncludesBuilder(menus=[Menu(name="m", items=[item])], property_schema=_schema())
    xml = ET.tostring(builder.build(), encoding="unicode")
    assert 'name="keep"' in xml
    assert "widgetSortBy" not in xml


class _FakeManager:
    """Manager stand-in logging custom property writes."""

    def __init__(self):
        self.writes: dict[str, str | None] = {}

    def set_custom_property(self, menu_id, item_id, prop_name, value):
        self.writes[prop_name] = value
        return True

    def clear_custom_widget(self, *a):
        return True


class _Dialog(PropertiesMixin, ItemsMixin):
    """Dialog stand-in mixing properties and items, with no suffix."""

    def __init__(self, schema):
        self.manager = _FakeManager()
        self.menu_id = "mainmenu"
        self.property_schema = schema
        self.property_suffix = ""

    def _log(self, msg):
        pass

    def _suffixed_name(self, name):
        return name

    def _get_selected_listitem(self):
        return None


def test_dialog_swap_resets_in_declared_name():
    dialog = _Dialog(_schema())
    item = MenuItem(name="movies", label="M", properties={"widget": "w", "widgetSortby": "title"})
    dialog._set_widget_properties(item, "widget", PLAIN)
    assert dialog.manager.writes["widgetSortby"] == ""
    assert "widgetSortBy" not in dialog.manager.writes
    assert "widgetSortby" not in item.properties


def test_dialog_declared_values_land_in_declared_name():
    dialog = _Dialog(_schema())
    item = MenuItem(name="movies", label="M")
    dialog._set_widget_properties(item, "widget.2", SORTED)
    assert item.properties["widgetSortby.2"] == "title"
    assert item.properties["widgetSortorder.2"] == "ascending"
    assert item.properties["widgetLimit.2"] == "40"
    dialog._clear_widget_properties(item, "widget.2")
    assert not any(k.lower().startswith("widgetsort") for k in item.properties)


def test_dialog_without_schema_keeps_script_name():
    dialog = _Dialog(None)
    item = MenuItem(name="movies", label="M")
    dialog._set_widget_properties(item, "widget", SORTED)
    assert item.properties["widgetSortBy"] == "title"


def test_conditions_read_any_case():
    from skinshortcuts.conditions import evaluate_condition

    props = {"widgetSortby": "title", "widgetSortorder": ""}
    assert evaluate_condition("widgetSortBy=title", props)
    assert evaluate_condition("widgetSortBy~tit", props)
    assert evaluate_condition("widgetSortBy IN year,title", props)
    assert evaluate_condition("widgetSortBy", props)
    assert evaluate_condition("widgetSortOrder EMPTY", props)
    assert not evaluate_condition("!widgetSortBy", props)


def test_conditions_exact_name_wins():
    from skinshortcuts.conditions import evaluate_condition

    props = {"widgetSortby": "title", "widgetSortBy": "year"}
    assert evaluate_condition("widgetSortBy=year", props)
    assert evaluate_condition("widgetSortby=title", props)


TEMPLATE_MENUS = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies">
      <label>Movies</label>
      <action>Noop</action>
      <property name="widgetSortby">title</property>
    </item>
  </menu>
</menus>
"""

TEMPLATE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <template include="t" menu="mainmenu">
    <condition>widgetSortBy=title</condition>
    <property name="sort" from="widgetSortBy" />
    <property name="flag" condition="widgetSortBy">on</property>
    <controls>
      <control type="label">
        <label>$PROPERTY[sort]|$PROPERTY[widgetSortBy]|$PROPERTY[flag]</label>
      </control>
    </controls>
  </template>
</templates>
"""


def test_template_reads_any_case(tmp_path):
    (tmp_path / "menus.xml").write_text(TEMPLATE_MENUS)
    (tmp_path / "templates.xml").write_text(TEMPLATE_XML)
    config = SkinConfig.load(tmp_path, load_user=False)
    out = tmp_path / "includes.xml"
    config.build_includes(out)
    labels = [e.text for e in ET.parse(out).getroot().iter("label")]
    assert "title|title|on" in labels


def test_math_reads_any_case():
    from skinshortcuts.expressions import evaluate_math

    assert evaluate_math("widgetLimit * 2", {"widgetlimit": "20"}) == "40"
    assert evaluate_math("missing + 1", {}) == "1"


def test_item_added_from_widget_uses_declared_name():
    item = _Dialog(_schema())._create_item_from_widget(SORTED)
    assert item.properties["widgetSortby"] == "title"
    assert item.properties["widgetSortorder"] == "ascending"
    assert item.properties["widgetPath"] == "p://"
    assert "widgetSortBy" not in item.properties


def test_item_added_from_widget_without_schema():
    item = _Dialog(None)._create_item_from_widget(SORTED)
    assert item.properties["widgetSortBy"] == "title"


def test_schema_and_item_reads_agree():
    from skinshortcuts.conditions import lookup

    both = PropertySchema(properties={
        "widgetSortby": SchemaProperty(name="widgetSortby"),
        "widgetSortBy": SchemaProperty(name="widgetSortBy"),
    })
    values = {"widgetSortby": "a", "widgetSortBy": "b"}
    for name in ("widgetSortby", "widgetSortBy", "WIDGETSORTBY"):
        prop = both.get_property(name)
        assert prop is not None
        assert values[prop.name] == lookup(name, values)


DEFAULTS_MENUS = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <defaults><property name="widgetsortby">year</property></defaults>
    <item name="movies">
      <label>Movies</label>
      <action>Noop</action>
      <property name="widgetSortby">title</property>
    </item>
  </menu>
</menus>
"""

DEFAULTS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <template include="t" menu="mainmenu">
    <controls>
      <control type="label"><label>$PROPERTY[widgetsortby]|$PROPERTY[WidgetSortBy]</label></control>
    </controls>
  </template>
</templates>
"""


def test_item_property_replaces_default_spelled_differently(tmp_path):
    (tmp_path / "menus.xml").write_text(DEFAULTS_MENUS)
    (tmp_path / "templates.xml").write_text(DEFAULTS_TEMPLATE)
    config = SkinConfig.load(tmp_path, load_user=False)
    out = tmp_path / "includes.xml"
    config.build_includes(out)
    root = ET.parse(out).getroot()

    assert "title|title" in [e.text for e in root.iter("label")]
    sort_props = [
        p.text for p in root.iter("property") if (p.get("name") or "").lower() == "widgetsortby"
    ]
    assert sort_props == ["title"]


def test_skin_value_replaces_builtin_spelled_differently(tmp_path):
    (tmp_path / "menus.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies"><label>Movies</label><action>Noop</action>
      <property name="Path">custom://</property>
    </item>
  </menu>
</menus>
""")
    config = SkinConfig.load(tmp_path, load_user=False)
    out = tmp_path / "includes.xml"
    config.build_includes(out)
    paths = [
        p.text for p in ET.parse(out).getroot().iter("property")
        if (p.get("name") or "").lower() == "path"
    ]
    assert paths == ["custom://"]
