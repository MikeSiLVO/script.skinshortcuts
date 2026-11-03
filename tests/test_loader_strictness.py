"""A broken definition is skipped with a warning, and a repeated name warns and keeps the first."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from skinshortcuts.exceptions import ConfigError
from skinshortcuts.loaders.background import load_backgrounds
from skinshortcuts.loaders.menu import load_groupings, load_menus
from skinshortcuts.loaders.property import load_properties
from skinshortcuts.loaders.template import load_templates
from skinshortcuts.loaders.views import load_views
from skinshortcuts.loaders.widget import load_widgets

ITEM = '<item name="a"><label>A</label><action>Noop</action></item>'
MENU = f'<menus><menu name="m">{ITEM}</menu>%s</menus>'
ICON = "<overrides><icons>%s</icons></overrides>"


def rule(library: str = "50", views: str = "50", visible: str = "x", plugin: str = "") -> str:
    """A views.xml defining view 50 and one content rule."""
    extra = f' plugin="{plugin}"' if plugin else ""
    return (
        f'<views><view id="50" label="V"/><rules><content name="c" label="C" library="{library}"'
        f"{extra}><visible>{visible}</visible><views>{views}</views></content></rules></views>"
    )


BROKEN = [
    ("widget name", load_widgets, '<widgets><widget label="W"><path>x://</path></widget></widgets>'),
    ("widget label", load_widgets, '<widgets><widget name="w"><path>x://</path></widget></widgets>'),
    ("widget path", load_widgets, '<widgets><widget name="w" label="W"/></widgets>'),
    ("background name", load_backgrounds, '<backgrounds><background label="B"><path>x</path>'
     "</background></backgrounds>"),
    ("background path", load_backgrounds,
     '<backgrounds><background name="b" label="B"/></backgrounds>'),
    ("property name", load_properties, "<properties><property/></properties>"),
    ("button id", load_properties,
     '<properties><buttons><button id="abc" property="x"/></buttons></properties>'),
    ("button property", load_properties,
     '<properties><buttons><button id="301"/></buttons></properties>'),
    ("fallback property", load_properties,
     "<properties><fallbacks><fallback><default>x</default></fallback></fallbacks></properties>"),
    ("preset name", load_templates, "<templates><presets><preset/></presets></templates>"),
    ("template include", load_templates, "<templates><template/></templates>"),
    ("menu name", load_menus, f"<menus><menu>{ITEM}</menu></menus>"),
    ("item name", load_menus, '<menus><menu name="m"><item><label>A</label></item></menu></menus>'),
    ("item label", load_menus, '<menus><menu name="m"><item name="a"/></menu></menus>'),
    ("view id", load_views, '<views><view label="V"/></views>'),
    ("view label", load_views, '<views><view id="50"/></views>'),
    ("content visible", load_views, rule(visible="")),
    ("content views", load_views, rule(views="99")),
    ("content library", load_views, rule(library="99")),
    ("expression name", load_templates, "<templates><expressions><expression>a</expression>"
     "</expressions></templates>"),
    ("preset group name", load_templates,
     "<templates><presetGroups><presetGroup/></presetGroups></templates>"),
    ("preset group preset", load_templates,
     '<templates><presetGroups><presetGroup name="g"><preset/></presetGroup></presetGroups>'
     "</templates>"),
    ("property group name", load_templates,
     "<templates><propertyGroups><propertyGroup/></propertyGroups></templates>"),
    ("variable name", load_templates, "<templates><variables><variable/></variables></templates>"),
    ("variable group name", load_templates,
     "<templates><variables><variableGroup/></variables></templates>"),
    ("variable group nested", load_templates, '<templates><variables><variableGroup name="g">'
     "<variableGroup/></variableGroup></variables></templates>"),
    ("variable group reference", load_templates, '<templates><variables><variableGroup name="g">'
     "<variable/></variableGroup></variables></templates>"),
    ("include name", load_templates, "<templates><includes><include/></includes></templates>"),
    ("template property", load_templates,
     '<templates><template include="t"><property/></template></templates>'),
    ("template var", load_templates,
     '<templates><template include="t"><var/></template></templates>'),
    ("template reference", load_templates,
     '<templates><template include="t"><propertyGroup/></template></templates>'),
    ("property include name", load_properties,
     "<properties><includes><include/></includes></properties>"),
    ("button no id", load_properties,
     '<properties><buttons><button property="x"/></buttons></properties>'),
    ("button rename", load_properties,
     '<properties><buttons><button id="301" property="x" rename="true"/></buttons></properties>'),
    ("context menu value", load_menus, MENU % "<contextmenu>yes</contextmenu>"),
    ("context menu button", load_menus, MENU % '<contextmenu><button id="x"/></contextmenu>'),
    ("context menu enableon", load_menus, MENU % '<contextmenu enableon="x"/>'),
    ("icon override replace", load_menus, MENU % ICON % "<icon>a.png</icon>"),
    ("icon override path", load_menus, MENU % ICON % '<icon replace="a.png"/>'),
    ("icon override relative", load_menus, MENU % ICON % '<icon replace="a.png">b.png</icon>'),
    ("shortcut name", load_groupings,
     '<menus><groupings><shortcut label="S"><action>Noop</action></shortcut></groupings></menus>'),
    ("shortcut label", load_groupings,
     '<menus><groupings><shortcut name="s"><action>Noop</action></shortcut></groupings></menus>'),
    ("input label", load_groupings, "<menus><groupings><input/></groupings></menus>"),
    ("subdialog button id", load_menus, MENU % '<dialogs><subdialog mode="x"/></dialogs>'),
    ("subdialog does nothing", load_menus, MENU % '<dialogs><subdialog buttonID="401"/></dialogs>'),
    ("onclose action", load_menus,
     MENU % '<dialogs><subdialog buttonID="401" mode="x"><onclose/></subdialog></dialogs>'),
    ("action override replace", load_menus, MENU % "<overrides><action>Noop</action></overrides>"),
    ("action override text", load_menus,
     MENU % '<overrides><action replace="ActivateWindow(Videos)"/></overrides>'),
    ("name override replace", load_widgets,
     "<widgets><overrides><widget>new</widget></overrides></widgets>"),
    ("widget content source", load_widgets, "<widgets><content/></widgets>"),
    ("shortcut content source", load_groupings, "<menus><groupings><content/></groupings></menus>"),
    ("background source path", load_backgrounds,
     '<backgrounds><background name="b" label="B" type="playlist"><source label="S"/>'
     "</background></backgrounds>"),
    ("include content", load_properties,
     '<properties><property name="x"><options><include/></options></property></properties>'),
    ("content undefined view", load_views, rule(views="50,99")),
]

DUPLICATES = [
    (
        "property",
        load_properties,
        '<properties><property name="style" value="a"/><property name="style" value="b"/>'
        "</properties>",
        lambda c: c.properties["style"].value,
    ),
    (
        "property differing in case",
        load_properties,
        '<properties><property name="Style" value="a"/><property name="style" value="b"/>'
        "</properties>",
        lambda c: "".join(p.value for p in c.properties.values()),
    ),
    (
        "button",
        load_properties,
        '<properties><buttons><button id="301" property="a"/><button id="301" property="b"/>'
        "</buttons></properties>",
        lambda c: c.buttons[301].property_name,
    ),
    (
        "fallback",
        load_properties,
        '<properties><fallbacks><fallback property="p"><default>a</default></fallback>'
        '<fallback property="p"><default>b</default></fallback></fallbacks></properties>',
        lambda c: c.fallbacks["p"].rules[0].value,
    ),
    (
        "fallback differing in case",
        load_properties,
        '<properties><fallbacks><fallback property="P"><default>a</default></fallback>'
        '<fallback property="p"><default>b</default></fallback></fallbacks></properties>',
        lambda c: "".join(f.rules[0].value for f in c.fallbacks.values()),
    ),
    (
        "property include",
        load_properties,
        '<properties><includes><include name="i"><option value="a"/></include>'
        '<include name="i"><option value="b"/></include></includes>'
        '<property name="x"><options><include content="i"/></options></property></properties>',
        lambda c: c.properties["x"].options[0].value,
    ),
    (
        "preset group",
        load_templates,
        '<templates><presetGroups><presetGroup name="g"><values top="a"/></presetGroup>'
        '<presetGroup name="g"><values top="b"/></presetGroup></presetGroups></templates>',
        lambda s: s.preset_groups["g"].children[0].values["top"],
    ),
    (
        "property group",
        load_templates,
        '<templates><propertyGroups><propertyGroup name="g"><property name="x" value="a"/>'
        '</propertyGroup><propertyGroup name="g"><property name="x" value="b"/></propertyGroup>'
        "</propertyGroups></templates>",
        lambda s: s.property_groups["g"].properties[0].value,
    ),
    (
        "variable",
        load_templates,
        '<templates><variables><variable name="v" output="a"/><variable name="v" output="b"/>'
        "</variables></templates>",
        lambda s: s.variable_definitions["v"].output,
    ),
    (
        "variable group",
        load_templates,
        '<templates><variables><variableGroup name="g"><variable content="a"/></variableGroup>'
        '<variableGroup name="g"><variable content="b"/></variableGroup></variables></templates>',
        lambda s: s.variable_groups["g"].references[0].name,
    ),
    (
        "items template",
        load_templates,
        '<templates><template items="i" source="a"/><template items="i" source="b"/></templates>',
        lambda s: s.items_templates["i"].source,
    ),
    (
        "expression",
        load_templates,
        '<templates><expressions><expression name="e">a</expression>'
        '<expression name="e">b</expression></expressions></templates>',
        lambda s: s.expressions["e"].value.strip("[]"),
    ),
    (
        "preset",
        load_templates,
        '<templates><presets><preset name="p"><values top="a"/></preset>'
        '<preset name="p"><values top="b"/></preset></presets></templates>',
        lambda s: s.presets["p"].rows[0].values["top"],
    ),
    (
        "include",
        load_templates,
        '<templates><includes><include name="i"><a/></include><include name="i"><b/></include>'
        "</includes></templates>",
        lambda s: s.includes["i"].controls[0].tag,
    ),
]


@pytest.fixture
def warned(monkeypatch) -> list[str]:
    """Toasts shown while the loader runs, as heading and message."""
    captured: list[str] = []
    monkeypatch.setattr(
        "xbmcgui.Dialog.notification", lambda _self, h, m, *_: captured.append(f"{h}: {m}")
    )
    return captured


def write(tmp_path: Path, xml: str) -> Path:
    """Write the config under a throwaway name; loaders check only the root element."""
    path = tmp_path / "config.xml"
    path.write_text(xml, encoding="utf-8")
    return path


def test_nameless_widget_group_is_skipped(tmp_path: Path, warned: list[str]) -> None:
    xml = '<widgets><group label="G"><widget name="w" label="W"><path>x://</path></widget>' \
        "</group></widgets>"
    assert load_widgets(write(tmp_path, xml)).groupings == []
    assert warned


@pytest.mark.parametrize(("case", "loader", "xml"), BROKEN, ids=[b[0] for b in BROKEN])
def test_broken_definition_is_reported(
    tmp_path: Path, warned: list[str], case: str, loader: Callable, xml: str
) -> None:
    """Each case shows a toast and the loader carries on."""
    loader(write(tmp_path, xml))
    assert warned


def test_undefined_plugin_view_is_dropped(tmp_path: Path, warned: list[str]) -> None:
    """The rule stays with its library default; only the plugin default goes."""
    content = load_views(write(tmp_path, rule(plugin="99"))).content_rules
    assert [(c.name, c.plugin_default) for c in content] == [("c", "")]
    assert warned


def test_invalid_subdialog_button_id_warns(tmp_path: Path, warned: list[str]) -> None:
    """A non-numeric buttonID drops the subdialog with a toast."""
    xml = f'<menus><menu name="m">{ITEM}</menu>' \
        '<dialogs><subdialog buttonID="abc" mode="x"/></dialogs></menus>'
    assert load_menus(write(tmp_path, xml)).subdialogs == []
    assert warned


@pytest.mark.parametrize(
    ("kind", "loader", "xml", "pick"), DUPLICATES, ids=[d[0] for d in DUPLICATES]
)
def test_repeated_name_warns_and_keeps_the_first(
    tmp_path: Path, warned: list[str], kind: str, loader: Callable, xml: str, pick: Callable
) -> None:
    """Each case shows a toast and the loader keeps the first definition."""
    assert pick(loader(write(tmp_path, xml))) == "a"
    assert warned


def test_unknown_options_include_warns(tmp_path: Path, warned: list[str]) -> None:
    """An include naming no defined include adds no options and shows a toast."""
    xml ='<properties><property name="x"><options><include content="missing"/></options>' \
        "</property></properties>"
    assert load_properties(write(tmp_path, xml)).properties["x"].options == []
    assert warned


@pytest.mark.parametrize(
    "loader",
    [load_menus, load_widgets, load_backgrounds, load_properties, load_templates, load_views],
    ids=["menus", "widgets", "backgrounds", "properties", "templates", "views"],
)
@pytest.mark.parametrize("xml", ["<unclosed>", "<wrong/>"], ids=["parse error", "wrong root"])
def test_unusable_file_is_reported(
    tmp_path: Path, warned: list[str], loader: Callable, xml: str
) -> None:
    """A file that is not XML, or has the wrong root, shows a toast and still raises."""
    with pytest.raises(ConfigError):
        loader(write(tmp_path, xml))
    assert len(warned) == 1 and "'config.xml' could not be loaded" in warned[0]


def test_shortcut_without_action_warns(tmp_path: Path, warned: list[str]) -> None:
    """A shortcut with neither an action nor a browse path is dropped with a toast."""
    xml ='<menus><groupings><shortcut name="s" label="S"/></groupings></menus>'
    assert load_groupings(write(tmp_path, xml)) == []
    assert warned
