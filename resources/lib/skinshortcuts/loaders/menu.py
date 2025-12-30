"""Menu loader."""

from __future__ import annotations

from pathlib import Path

from ..exceptions import MenuConfigError
from ..models.menu import (
    Action,
    ActionOverride,
    Content,
    DefaultAction,
    IconSource,
    Menu,
    MenuAllow,
    MenuConfig,
    MenuDefaults,
    MenuItem,
    OnCloseAction,
    Protection,
    Shortcut,
    ShortcutGroup,
    SubDialog,
)
from .base import get_attr, get_text, parse_content, parse_xml


def load_menus(path: str | Path) -> MenuConfig:
    """Load complete menu configuration from menus.xml.

    Returns:
        MenuConfig containing menus, groupings, icon sources, subdialogs, and settings.
    """
    path = Path(path)
    if not path.exists():
        return MenuConfig()

    root = parse_xml(path, "menus", MenuConfigError)
    path_str = str(path)

    menus = _parse_menus(root, path_str)
    groupings = _parse_shortcut_groupings(root, path_str)
    icon_sources = _parse_icons(root)
    subdialogs = _parse_dialogs(root)
    action_overrides = _parse_overrides(root)
    show_context_menu = _parse_context_menu(root)

    return MenuConfig(
        menus=menus,
        groupings=groupings,
        icon_sources=icon_sources,
        subdialogs=subdialogs,
        action_overrides=action_overrides,
        show_context_menu=show_context_menu,
    )


def _parse_menus(root, path: str) -> list[Menu]:
    """Parse menu and submenu elements from root."""
    menus = []

    for elem in root.findall("menu"):
        menu = _parse_menu(elem, path, is_submenu=False)
        menus.append(menu)

    for elem in root.findall("submenu"):
        menu = _parse_menu(elem, path, is_submenu=True)
        menus.append(menu)

    return menus


def _parse_icons(root) -> list[IconSource]:
    """Parse icon sources from <icons> element.

    Supports two formats:
    1. Simple: <icons>path/to/icons/</icons>
    2. Advanced: <icons><source label="..." condition="...">path</source>...</icons>
    """
    icons_elem = root.find("icons")
    if icons_elem is None:
        return []

    sources = []

    source_elems = icons_elem.findall("source")
    if source_elems:
        for source_elem in source_elems:
            label = get_attr(source_elem, "label") or ""
            path = (source_elem.text or "").strip()
            if path:
                sources.append(IconSource(
                    label=label,
                    path=path,
                    condition=get_attr(source_elem, "condition") or "",
                    visible=get_attr(source_elem, "visible") or "",
                    icon=get_attr(source_elem, "icon") or "",
                ))
    else:
        path = (icons_elem.text or "").strip()
        if path:
            sources.append(IconSource(label="", path=path))

    return sources


def _parse_context_menu(root) -> bool:
    """Parse contextmenu setting from <contextmenu> element.

    Returns True (show context menu) by default unless explicitly set to false.
    """
    elem = root.find("contextmenu")
    if elem is None:
        return True

    text = (elem.text or "").strip().lower()
    return text not in ("false", "0", "no", "")


def _parse_dialogs(root) -> list[SubDialog]:
    """Parse subdialog definitions from <dialogs> element.

    Schema:
        <dialogs>
            <subdialog buttonID="800" mode="widget1" setfocus="309">
                <prompt>
                    <option label="Choose Widget" action="subdialog"/>
                    <option label="Edit Custom" action="menu" menu="{item}.customwidget"
                            condition="String.IsEqual(widgetType,custom)"/>
                    <option label="Clear"
                            onclick="RunScript(script.skinshortcuts,type=clear...)"
                            condition="String.IsEqual(widgetType,custom)"/>
                </prompt>
            </subdialog>
        </dialogs>
    """
    dialogs_elem = root.find("dialogs")
    if dialogs_elem is None:
        return []

    subdialogs = []
    for elem in dialogs_elem.findall("subdialog"):
        button_id_str = get_attr(elem, "buttonID")
        mode = get_attr(elem, "mode")

        if not button_id_str or not mode:
            continue

        try:
            button_id = int(button_id_str)
        except ValueError:
            continue

        setfocus = None
        setfocus_str = get_attr(elem, "setfocus")
        if setfocus_str and setfocus_str.isdigit():
            setfocus = int(setfocus_str)

        suffix = get_attr(elem, "suffix") or ""
        onclose_actions = _parse_onclose(elem)

        subdialogs.append(
            SubDialog(
                button_id=button_id,
                mode=mode,
                setfocus=setfocus,
                suffix=suffix,
                onclose=onclose_actions,
            )
        )

    return subdialogs


def _parse_onclose(subdialog_elem) -> list[OnCloseAction]:
    """Parse onclose actions from a subdialog element.

    <onclose condition="widgetType=custom" action="menu" menu="{item}.customwidget"/>
    <onclose condition="widgetType.2=custom" action="menu" menu="{item}.customwidget.2"/>
    """
    actions = []
    for elem in subdialog_elem.findall("onclose"):
        action = get_attr(elem, "action")
        if not action:
            continue

        actions.append(
            OnCloseAction(
                action=action,
                menu=get_attr(elem, "menu") or "",
                condition=get_attr(elem, "condition") or "",
            )
        )

    return actions


def _parse_overrides(root) -> list[ActionOverride]:
    """Parse action overrides from <overrides> element.

    Schema:
        <overrides>
            <action replace="ActivateWindow(favourites)">ActivateWindow(favouritesbrowser)</action>
        </overrides>
    """
    overrides_elem = root.find("overrides")
    if overrides_elem is None:
        return []

    overrides = []
    for elem in overrides_elem.findall("action"):
        replace = get_attr(elem, "replace")
        action = (elem.text or "").strip()

        if replace and action:
            overrides.append(ActionOverride(replace=replace, action=action))

    return overrides


def _parse_menu(elem, path: str, is_submenu: bool = False) -> Menu:
    menu_name = get_attr(elem, "name")
    if not menu_name:
        raise MenuConfigError(path, "Menu missing 'name' attribute")

    items = []
    for item_elem in elem.findall("item"):
        item = _parse_item(item_elem, menu_name, path)
        items.append(item)

    defaults = _parse_defaults(elem.find("defaults"))
    allow = _parse_allow(elem.find("allow"))
    container = get_attr(elem, "container") or None

    return Menu(
        name=menu_name,
        items=items,
        defaults=defaults,
        allow=allow,
        container=container,
        is_submenu=is_submenu,
    )


def _parse_item(elem, menu_name: str, path: str) -> MenuItem:
    item_name = get_attr(elem, "name")
    if not item_name:
        raise MenuConfigError(path, f"Menu '{menu_name}' has item without 'name'")

    label = get_text(elem, "label")
    if not label:
        raise MenuConfigError(path, f"Item '{item_name}' missing <label>")

    actions = []
    for action_elem in elem.findall("action"):
        if action_elem.text:
            actions.append(Action(
                action=action_elem.text.strip(),
                condition=get_attr(action_elem, "condition") or "",
            ))


    properties = {}
    for prop_elem in elem.findall("property"):
        prop_name = get_attr(prop_elem, "name")
        if prop_name and prop_elem.text:
            properties[prop_name] = prop_elem.text.strip()

    visible = get_text(elem, "visible") or ""

    widget_attr = get_attr(elem, "widget")
    if widget_attr:
        properties["widget"] = widget_attr
    background_attr = get_attr(elem, "background")
    if background_attr:
        properties["background"] = background_attr

    protection = None
    protect_elem = elem.find("protect")
    if protect_elem is not None:
        protection = Protection(
            type=get_attr(protect_elem, "type", "all"),
            heading=get_attr(protect_elem, "heading", ""),
            message=get_attr(protect_elem, "message", ""),
        )

    dialog_visible = get_attr(elem, "visible") or ""

    return MenuItem(
        name=item_name,
        label=label,
        actions=actions,
        label2=get_text(elem, "label2"),
        icon=get_text(elem, "icon", "DefaultShortcut.png"),
        thumb=get_text(elem, "thumb"),
        visible=visible,
        dialog_visible=dialog_visible,
        disabled=get_text(elem, "disabled", "false").lower() == "true",
        required=get_attr(elem, "required", "false").lower() == "true",
        protection=protection,
        properties=properties,
        submenu=get_attr(elem, "submenu"),
    )


def _parse_defaults(elem) -> MenuDefaults:
    if elem is None:
        return MenuDefaults()

    properties = {}
    for prop_elem in elem.findall("property"):
        name = get_attr(prop_elem, "name")
        if name and prop_elem.text:
            properties[name] = prop_elem.text.strip()

    widget_attr = get_attr(elem, "widget")
    if widget_attr:
        properties["widget"] = widget_attr
    background_attr = get_attr(elem, "background")
    if background_attr:
        properties["background"] = background_attr

    actions = []
    for action_elem in elem.findall("action"):
        if action_elem.text:
            actions.append(DefaultAction(
                action=action_elem.text.strip(),
                when=get_attr(action_elem, "when") or "before",
                condition=get_attr(action_elem, "condition") or "",
            ))

    return MenuDefaults(
        properties=properties,
        actions=actions,
    )


def _parse_allow(elem) -> MenuAllow:
    if elem is None:
        return MenuAllow()

    def parse_bool(value: str | None, default: bool = True) -> bool:
        if value is None:
            return default
        return value.lower() == "true"

    return MenuAllow(
        widgets=parse_bool(get_attr(elem, "widgets")),
        backgrounds=parse_bool(get_attr(elem, "backgrounds")),
        submenus=parse_bool(get_attr(elem, "submenus")),
    )


def load_groupings(path: str | Path) -> list[ShortcutGroup]:
    """Load shortcut groupings from menus.xml file.

    Groupings define the available shortcuts for the picker dialog.
    They are stored inside a <groupings> element within <menus>.

    Note: Consider using load_menus() instead which returns full MenuConfig.

    Schema:
        <menus>
          ...
          <groupings>
            <group name="..." label="..." icon="..." condition="...">
              <shortcut name="..." label="..." icon="..." type="..." condition="...">
                <action>...</action>
              </shortcut>
              <shortcut name="..." label="..." browse="videos">
                <path>videodb://movies/genres/</path>
              </shortcut>
              <content source="playlists" target="videos"/>
              <group name="...">...</group>  <!-- nested -->
            </group>
          </groupings>
        </menus>
    """
    path = Path(path)
    if not path.exists():
        return []

    root = parse_xml(path, "menus", MenuConfigError)
    return _parse_shortcut_groupings(root, str(path))


def _parse_shortcut_groupings(root, path: str) -> list[ShortcutGroup]:
    """Parse groupings from root element."""
    groupings_elem = root.find("groupings")
    if groupings_elem is None:
        return []

    groups = []
    for group_elem in groupings_elem.findall("group"):
        group = _parse_shortcut_group(group_elem, path)
        if group:
            groups.append(group)

    return groups


def _parse_shortcut_group(elem, path: str) -> ShortcutGroup | None:
    """Parse a group element (supports nested groups, shortcuts, and content refs)."""
    group_name = get_attr(elem, "name")
    label = get_attr(elem, "label")
    if not group_name or not label:
        return None

    condition = get_attr(elem, "condition") or ""
    icon = get_attr(elem, "icon") or ""
    items: list[Shortcut | ShortcutGroup | Content] = []

    for child in elem:
        if child.tag == "shortcut":
            shortcut = _parse_shortcut(child, path)
            if shortcut:
                items.append(shortcut)
        elif child.tag == "group":
            nested = _parse_shortcut_group(child, path)
            if nested:
                items.append(nested)
        elif child.tag == "content":
            content = parse_content(child)
            if content:
                items.append(content)

    visible = get_attr(elem, "visible") or ""
    return ShortcutGroup(
        name=group_name, label=label, condition=condition, visible=visible, icon=icon, items=items
    )


def _parse_shortcut(elem, path: str) -> Shortcut | None:
    """Parse a shortcut element.

    Supports two modes:
    1. Action mode: <action>ActivateWindow(...)</action>
    2. Browse mode: browse="videos" with <path>videodb://...</path>
    """
    shortcut_name = get_attr(elem, "name")
    label = get_attr(elem, "label")
    if not shortcut_name or not label:
        return None

    action = get_text(elem, "action") or ""
    shortcut_path = get_text(elem, "path") or ""
    browse = get_attr(elem, "browse") or ""

    # Must have either action or (browse + path)
    if not action and not (browse and shortcut_path):
        return None

    return Shortcut(
        name=shortcut_name,
        label=label,
        action=action,
        path=shortcut_path,
        browse=browse,
        type=get_attr(elem, "type") or "",
        icon=get_attr(elem, "icon") or "DefaultShortcut.png",
        condition=get_attr(elem, "condition") or "",
        visible=get_attr(elem, "visible") or "",
    )


