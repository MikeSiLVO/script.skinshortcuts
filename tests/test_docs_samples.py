"""Load the docs' XML samples through the real loaders."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "docs" / "migration-v2-to-v3.md"
STARTER = ROOT / "docs" / "skinning" / "starter.md"
WIDGETS_DOC = ROOT / "docs" / "skinning" / "widgets.md"
MENUS_DOC = ROOT / "docs" / "skinning" / "menus.md"
SCHEMA_DOC = ROOT / "docs" / "schema.md"


def blocks(doc: Path) -> dict[int, str]:
    """XML fences in a doc, keyed by the line the fence opens on."""
    text = doc.read_text(encoding="utf-8")
    return {
        text[: m.start()].count("\n") + 1: m.group(1)
        for m in re.finditer(r"```xml\n(.*?)```", text, re.DOTALL)
    }


def block_with(doc: Path, marker: str) -> str:
    """The one XML sample holding a given string, asserted unique."""
    hits = [body for body in blocks(doc).values() if marker in body]
    assert len(hits) == 1, f"{doc.name}: {len(hits)} samples contain {marker!r}"
    return hits[0]


def write(tmp_path: Path, name: str, body: str) -> str:
    """Write a sample to a temp config file and return its path."""
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return str(path)


def in_menu(fragment: str) -> str:
    """Wrap a menu-level fragment in a loadable menus.xml."""
    return f'<menus>\n<menu name="mainmenu">\n{fragment}\n</menu>\n</menus>\n'


def test_menus_sample(tmp_path: Path) -> None:
    from skinshortcuts.loaders.menu import load_groupings, load_menus

    path = write(
        tmp_path, "menus.xml", block_with(MIGRATION, '<menu name="mainmenu" container="9000">')
    )
    config = load_menus(path)

    main = next(m for m in config.menus if m.name == "mainmenu")
    assert main.container == "9000"
    assert main.allow.widgets and main.allow.backgrounds and main.allow.submenus
    assert main.defaults.properties["widget"] == "default-widget"
    assert main.defaults.properties["background"] == "default-bg"
    assert [(a.action, a.when) for a in main.defaults.actions] == [
        ("Dialog.Close(all,true)", "before")
    ]
    assert main.defaults.properties["widgetStyle"] == "Panel"

    movies = main.get_item("movies")
    assert movies is not None
    assert movies.submenu == "movies"
    assert movies.properties["widget"] == "recent-movies"
    assert movies.properties["background"] == "movie-fanart"
    assert movies.icon == "DefaultMovies.png"
    assert movies.visible == "Library.HasContent(movies)"
    assert movies.properties["widgetStyle"] == "Panel"
    assert movies.action == "ActivateWindow(Videos,videodb://movies/)"

    submenu = next(m for m in config.menus if m.name == "movies")
    assert submenu.is_submenu
    assert not submenu.allow.widgets
    assert [i.name for i in submenu.items] == ["all", "recent"]

    assert config.icon_sources[0].label == "Skin Icons"
    assert config.icon_sources[0].path == "special://skin/extras/icons/"
    assert config.icon_sources[1].path == "browse"

    dialog = next(d for d in config.subdialogs if d.button_id == 801)
    assert (dialog.mode, dialog.setfocus, dialog.suffix) == ("widget2", 309, ".2")

    override = config.action_overrides[0]
    assert override.replace == "ActivateWindow(favourites)"
    assert override.value == "ActivateWindow(favouritesbrowser)"

    assert config.context_menu.enabled

    groups = load_groupings(path, "mainmenu")
    common = next(g for g in groups if g.name == "common")
    assert {getattr(i, "name", "") for i in common.items} >= {"movies", "tvshows"}
    sources = {getattr(i, "source", "") for i in common.items}
    assert {"playlists", "favourites"} <= sources


def test_defaults_action_when(tmp_path: Path) -> None:

    from skinshortcuts.loaders.menu import load_menus
    path = write(tmp_path, "menus.xml", in_menu(block_with(MIGRATION, '<action when="after"')))
    menu = load_menus(path).menus[0]
    assert [(a.action, a.when) for a in menu.defaults.actions] == [
        ("Dialog.Close(all,true)", "before"),
        ("SetProperty(...)", "after"),
    ]
    assert menu.defaults.actions[1].condition == "..."


def test_conditional_item_actions(tmp_path: Path) -> None:

    from skinshortcuts.loaders.menu import load_menus
    path = write(tmp_path, "menus.xml", in_menu(
        block_with(MIGRATION, '<action condition="!Library.HasContent(movies)">')
    ))
    item = load_menus(path).menus[0].items[0]
    assert [(a.action, a.condition) for a in item.actions] == [
        ("ActivateWindow(Videos,videodb://movies/)", "Library.HasContent(movies)"),
        ("ActivateWindow(Videos,files)", "!Library.HasContent(movies)"),
    ]


def test_context_menu_sample(tmp_path: Path) -> None:

    from skinshortcuts.loaders.menu import load_menus
    path = write(
        tmp_path,
        "menus.xml",
        f"<menus>\n{block_with(MIGRATION, '<contextmenu enableon="211">')}\n</menus>\n",
    )
    context = load_menus(path).context_menu
    assert context.enabled
    assert context.enable_on == [211]
    assert [(b.button_id, b.label) for b in context.buttons] == [
        (313, ""),
        (302, "$LOCALIZE[117]"),
    ]


def test_required_item(tmp_path: Path) -> None:

    from skinshortcuts.loaders.menu import load_menus
    path = write(tmp_path, "menus.xml", in_menu(block_with(MIGRATION, 'required="true"')))
    item = load_menus(path).menus[0].items[0]
    assert item.required


def test_protect_sample(tmp_path: Path) -> None:

    from skinshortcuts.loaders.menu import load_menus
    path = write(tmp_path, "menus.xml", in_menu(block_with(MIGRATION, '<protect type="action"')))
    item = load_menus(path).menus[0].items[0]
    protect = item.protection
    assert protect.type == "action"
    assert protect.heading == "Confirm"
    assert protect.message == "Change power action?"
    assert protect.protects_action()


def test_widgets_sample(tmp_path: Path) -> None:
    from skinshortcuts.loaders.widget import load_widgets

    path = write(tmp_path, "widgets.xml", block_with(MIGRATION, '<widget name="recent-movies"'))
    config = load_widgets(path)

    group = next(g for g in config.groupings if getattr(g, "name", "") == "movies")
    recent = next(i for i in group.items if getattr(i, "name", "") == "recent-movies")
    assert recent.path == "videodb://recentlyaddedmovies/"
    assert recent.limit == 25
    assert recent.sort_by == "dateadded"
    assert recent.sort_order == "descending"

    contents = [i for i in group.items if getattr(i, "source", "")]
    assert {(c.source, c.target) for c in contents} >= {
        ("playlists", "videos"),
        ("library", "moviegenres"),
        ("addons", "videos"),
    }

    flat = {w.name: w for w in config.widgets}
    assert flat["favourites"].path == "favourites://"
    assert flat["custom"].type == "custom"
    assert flat["custom"].slot == "widget"


def test_backgrounds_sample(tmp_path: Path) -> None:
    from skinshortcuts.loaders.background import load_backgrounds

    path = write(tmp_path, "backgrounds.xml", block_with(MIGRATION, 'live-playlist'))
    config = load_backgrounds(path)
    by_name = {b.name: b for b in config.backgrounds}

    assert by_name["movie-fanart"].type_name == "property"
    assert by_name["movie-fanart"].path == "$INFO[Window(Home).Property(MovieFanart)]"
    assert by_name["movie-fanart"].visible == "Library.HasContent(movies)"
    assert by_name["default"].type_name == "static"
    assert by_name["custom"].type_name == "browse"
    assert [s.path for s in by_name["custom"].browse_sources] == [
        "special://skin/backgrounds/",
        "browse",
    ]


def test_properties_sample(tmp_path: Path) -> None:
    from skinshortcuts.loaders.property import load_properties

    path = write(tmp_path, "properties.xml", block_with(MIGRATION, '<buttons suffix="true">'))
    schema = load_properties(path)

    style = schema.get_property("widgetStyle")
    assert style is not None
    assert style.type == "options"
    assert style.requires == "widget"
    assert [o.value for o in style.options] == ["Panel", "Wide", "Poster", "Landscape"]
    assert style.options[1].condition == "widgetType=movies"
    assert style.options[2].icons[0].path == "poster.png"

    button = schema.buttons.get(350)
    assert button is not None
    assert button.property_name == "widgetStyle"
    assert button.suffix is True
    assert button.requires == "widget"
    grouped = schema.buttons.get(360)
    assert grouped is not None
    assert grouped.suffix is False
    assert grouped.type == "toggle"

    fallback = schema.fallbacks["widgetStyle"]
    assert [(r.value, r.condition) for r in fallback.rules] == [
        ("Panel", "widgetType=movies"),
        ("Wide", "widgetType=tvshows"),
        ("Panel", ""),
    ]


def load_template_block(tmp_path: Path, marker: str):
    """Load a templates.xml sample, wrapping a bare fragment in <templates>."""
    from skinshortcuts.loaders.template import load_templates

    body = block_with(MIGRATION, marker)
    if not body.lstrip().startswith("<templates"):
        body = f"<templates>\n{body}\n</templates>\n"
    return load_templates(write(tmp_path, "templates.xml", body))


def test_template_other_migration(tmp_path: Path) -> None:
    schema = load_template_block(tmp_path, '<template include="main-menu-onright"')
    template = schema.templates[0]
    assert template.include == "main-menu-onright"
    assert template.menu == "mainmenu"
    assert template.controls is not None
    assert template.controls.find("onright") is not None


def test_template_expressions(tmp_path: Path) -> None:
    schema = load_template_block(tmp_path, '<expression name="HasWidget">')
    # the loader brackets every expression; a reference stays one term
    assert schema.get_expression("HasWidget").value == "[widgetPath]"
    assert schema.get_expression("IsMovies").value == "[widgetType=movies]"


def test_template_presets(tmp_path: Path) -> None:
    schema = load_template_block(tmp_path, '<preset name="WidgetDimensions">')
    preset = schema.get_preset("WidgetDimensions")
    assert [(row.condition, row.values) for row in preset.rows] == [
        ("widgetArt=Poster", {"width": "200", "height": "300"}),
        ("widgetArt=Landscape", {"width": "356", "height": "200"}),
        ("", {"width": "200", "height": "200"}),
    ]


def test_template_property_groups(tmp_path: Path) -> None:
    schema = load_template_block(tmp_path, '<propertyGroup name="widgetProps">')
    group = schema.get_property_group("widgetProps")
    assert [(p.name, p.from_source) for p in group.properties] == [
        ("path", "widgetPath"),
        ("target", "widgetTarget"),
    ]
    assert group.vars[0].name == "layout"


def test_template_multi_output(tmp_path: Path) -> None:
    schema = load_template_block(tmp_path, '<output include="widget1"')
    template = schema.templates[0]
    assert [(o.include, o.id_prefix, o.suffix) for o in template.get_outputs()] == [
        ("widget1", "8011", ""),
        ("widget2", "8021", ".2"),
    ]
    assert template.conditions == ["widgetPath"]


def test_template_items_iteration(tmp_path: Path) -> None:
    schema = load_template_block(tmp_path, '<template items="widgets"')
    items = schema.get_items_template("widgets")
    assert items.get_source() == "widgets"
    assert items.filter == "widgetArt=Poster"

    holder = next(t for t in schema.templates if t.include == "Widgets")
    assert holder.conditions == ["widgetType=custom"]
    assert holder.controls is not None
    inserts = [e.get("insert") for e in holder.controls.iter("skinshortcuts")]
    assert "widgets" in inserts


def test_starter_groupings(tmp_path: Path) -> None:

    from skinshortcuts.loaders.menu import load_groupings
    from skinshortcuts.loaders.menu import load_menus
    groupings = block_with(STARTER, '<group name="common"')
    path = write(
        tmp_path,
        "menus.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n<menus>\n'
        '  <menu name="mainmenu" container="9000">\n'
        '    <item name="movies"><label>Movies</label></item>\n'
        "  </menu>\n"
        + groupings
        + "\n</menus>\n",
    )
    assert [m.name for m in load_menus(path).menus] == ["mainmenu"]

    groups = load_groupings(path, "mainmenu")
    assert [g.name for g in groups] == [
        "common", "tv", "radio", "library", "playlists", "addons", "sources",
        "favourites", "settings", "commands",
    ]
    common = next(g for g in groups if g.name == "common")
    assert "favourites" in {getattr(i, "name", "") for i in common.items}


def test_starter_widgets(tmp_path: Path) -> None:

    from skinshortcuts.loaders.widget import load_widgets
    path = write(tmp_path, "widgets.xml", block_with(STARTER, '<group name="movies"'))
    config = load_widgets(path)
    assert "favourites" in {w.name for w in config.widgets}

    def names(entries: list) -> set[str]:
        found = set()
        for entry in entries:
            found.add(getattr(entry, "name", ""))
            found |= names(getattr(entry, "items", []))
        return found

    assert {"recent-movies", "recent-episodes", "recent-albums"} <= names(config.groupings)


VALID_TARGETS = {
    "sources": {"video", "videos", "music", "pictures", "picture", "files", "file",
                "programs", "program"},
    "playlists": {"video", "videos", "music", ""},
    "addons": {"video", "videos", "audio", "music", "image", "images", "picture",
               "pictures", "executable", "program", "programs", "game", "games"},
    "pvr": {"tv", "television", "radio"},
    "nodes": {"video", "videos", "music", "library", "all", ""},
    "favourites": {""},
    "commands": {""},
    "settings": {""},
    "library": {"genres", "moviegenres", "tvgenres", "musicgenres", "years", "movieyears",
                "tvyears", "studios", "moviestudios", "tvstudios", "tags", "movietags",
                "tvtags", "actors", "movieactors", "tvactors", "directors", "moviedirectors",
                "tvdirectors", "artists", "albums"},
}


@pytest.mark.parametrize("doc", [MIGRATION, STARTER, WIDGETS_DOC, MENUS_DOC])
def test_content_targets_are_known(doc: Path) -> None:
    import xml.etree.ElementTree as ET

    for line, body in blocks(doc).items():
        body = re.sub(r"<\?xml[^>]*\?>", "", body)
        try:
            root = ET.fromstring(f"<_root>{body}</_root>")
        except ET.ParseError:
            continue
        for content in root.iter("content"):
            source = content.get("source")
            if source is None:
                continue
            target = content.get("target", "")
            assert source in VALID_TARGETS, f"{doc.name}:{line} unknown source {source}"
            assert target in VALID_TARGETS[source], (
                f"{doc.name}:{line} {source}: bad target {target}"
            )


@pytest.mark.parametrize("line", sorted(blocks(SCHEMA_DOC)))
def test_schema_samples_load(tmp_path: Path, line: int) -> None:
    from skinshortcuts.loaders.background import load_backgrounds
    from skinshortcuts.loaders.menu import load_menus
    from skinshortcuts.loaders.property import load_properties
    from skinshortcuts.loaders.template import load_templates
    from skinshortcuts.loaders.widget import load_widgets
    from skinshortcuts.loaders.views import load_views

    loaders = {
        "menus": load_menus,
        "widgets": load_widgets,
        "backgrounds": load_backgrounds,
        "properties": load_properties,
        "templates": load_templates,
        "views": load_views,
    }

    body = blocks(SCHEMA_DOC)[line]
    root_tag = body.lstrip().split(">", 1)[0].lstrip("<").split()[0]
    loader = loaders.get(root_tag)
    assert loader is not None, f"schema.md:{line} unknown root <{root_tag}>"
    loader(write(tmp_path, f"{root_tag}.xml", body))


TEMPLATES_DOC = ROOT / "docs" / "skinning" / "templates.md"

TEMPLATE_SECTIONS = {
    "template", "submenu", "expressions", "presets", "presetGroups",
    "propertyGroups", "variables", "includes", "expression", "preset",
    "presetGroup", "propertyGroup", "variableGroup", "include",
}


@pytest.mark.parametrize("line", sorted(blocks(TEMPLATES_DOC)))
def test_templates_doc_samples(tmp_path: Path, line: int) -> None:
    from skinshortcuts.loaders.template import load_templates
    import xml.etree.ElementTree as ET

    body = blocks(TEMPLATES_DOC)[line]
    if body.lstrip().startswith("<?xml"):
        root = ET.fromstring(body)
        tags = {root.tag}
        payload = body
    else:
        root = ET.fromstring(f"<_wrap>{body}</_wrap>")
        tags = {child.tag for child in root}
        payload = f"<templates>\n{body}\n</templates>"

    if not tags:
        return
    if tags == {"templates"}:
        payload = body
    elif not tags <= TEMPLATE_SECTIONS:
        return
    load_templates(write(tmp_path, "templates.xml", payload))


MENUS_TOP = {"menu", "submenu", "groupings", "icons", "overrides", "dialogs",
             "contextmenu", "submenuPath"}
MENUS_IN_MENU = {"item", "allow", "defaults"}


@pytest.mark.parametrize("line", sorted(blocks(MENUS_DOC)))
def test_menus_doc_samples(tmp_path: Path, line: int) -> None:
    """Every fence is well-formed XML; complete ones also load."""
    from skinshortcuts.loaders.menu import load_menus
    import xml.etree.ElementTree as ET

    body = blocks(MENUS_DOC)[line]
    if body.lstrip().startswith("<?xml"):
        tags = {ET.fromstring(body).tag}
    else:
        tags = {child.tag for child in ET.fromstring(f"<_wrap>{body}</_wrap>")}

    # "..." marks an abridged structural example, not a loadable config
    if "..." in body or not tags:
        return

    if tags == {"menus"}:
        payload = body
    elif tags <= MENUS_TOP:
        payload = f"<menus>\n{body}\n</menus>"
    elif tags <= MENUS_IN_MENU:
        payload = f'<menus>\n<menu name="mainmenu">\n{body}\n</menu>\n</menus>'
    else:
        return
    load_menus(write(tmp_path, "menus.xml", payload))


@pytest.mark.parametrize("line", sorted(blocks(WIDGETS_DOC)))
def test_widgets_doc_samples(tmp_path: Path, line: int) -> None:
    """Every fence is well-formed XML; complete ones also load."""
    from skinshortcuts.loaders.widget import load_widgets
    import xml.etree.ElementTree as ET

    body = blocks(WIDGETS_DOC)[line]
    if body.lstrip().startswith("<?xml"):
        tags = {ET.fromstring(body).tag}
    else:
        tags = {child.tag for child in ET.fromstring(f"<_wrap>{body}</_wrap>")}

    if "..." in body or not tags:
        return
    if tags == {"widgets"}:
        payload = body
    elif tags <= {"widget", "group", "content"}:
        payload = f"<widgets>\n{body}\n</widgets>"
    else:
        return
    load_widgets(write(tmp_path, "widgets.xml", payload))


BACKGROUNDS_DOC = ROOT / "docs" / "skinning" / "backgrounds.md"


@pytest.mark.parametrize("line", sorted(blocks(BACKGROUNDS_DOC)))
def test_backgrounds_doc_samples(tmp_path: Path, line: int) -> None:
    """Every fence is well-formed XML; complete ones also load."""
    from skinshortcuts.loaders.background import load_backgrounds
    import xml.etree.ElementTree as ET

    body = blocks(BACKGROUNDS_DOC)[line]
    if body.lstrip().startswith("<?xml"):
        tags = {ET.fromstring(body).tag}
    else:
        tags = {child.tag for child in ET.fromstring(f"<_wrap>{body}</_wrap>")}

    if "..." in body or not tags:
        return
    if tags == {"backgrounds"}:
        payload = body
    elif tags <= {"background", "group", "content"}:
        payload = f"<backgrounds>\n{body}\n</backgrounds>"
    else:
        return
    load_backgrounds(write(tmp_path, "backgrounds.xml", payload))


PROPERTIES_DOC = ROOT / "docs" / "skinning" / "properties.md"


@pytest.mark.parametrize("line", sorted(blocks(PROPERTIES_DOC)))
def test_properties_doc_samples(tmp_path: Path, line: int) -> None:
    """Every fence is well-formed XML; complete ones also load."""
    from skinshortcuts.loaders.property import load_properties
    import xml.etree.ElementTree as ET

    body = blocks(PROPERTIES_DOC)[line]
    if body.lstrip().startswith("<?xml"):
        tags = {ET.fromstring(body).tag}
    else:
        tags = {child.tag for child in ET.fromstring(f"<_wrap>{body}</_wrap>")}

    if "..." in body or not tags:
        return
    if tags == {"properties"}:
        payload = body
    elif tags <= {"property", "buttons", "fallbacks", "includes", "options"}:
        payload = f"<properties>\n{body}\n</properties>"
    else:
        return
    load_properties(write(tmp_path, "properties.xml", payload))


VIEWS_DOC = ROOT / "docs" / "skinning" / "views.md"


@pytest.mark.parametrize("line", sorted(blocks(VIEWS_DOC)))
def test_views_doc_samples(tmp_path: Path, line: int) -> None:
    """Every fence is well-formed XML; complete ones also load."""
    from skinshortcuts.loaders.views import load_views
    import xml.etree.ElementTree as ET

    body = blocks(VIEWS_DOC)[line]
    if body.lstrip().startswith("<?xml"):
        tags = {ET.fromstring(body).tag}
    else:
        tags = {child.tag for child in ET.fromstring(f"<_wrap>{body}</_wrap>")}

    if "..." in body or not tags:
        return
    if tags == {"views"}:
        payload = body
    elif tags <= {"view", "rules", "content"}:
        # the loader rejects a rule naming a view the file never defines
        wrapped = ET.fromstring(f"<_wrap>{body}</_wrap>")
        ids = {
            view_id.strip()
            for views_elem in wrapped.iter("views")
            for view_id in (views_elem.text or "").split(",")
            if view_id.strip()
        }
        defs = "\n".join(f'<view id="{i}" label="{i}" />' for i in sorted(ids))
        payload = f"<views>\n{defs}\n{body}\n</views>"
    else:
        return
    load_views(write(tmp_path, "views.xml", payload))
