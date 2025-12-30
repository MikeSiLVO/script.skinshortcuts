"""Picker dialogs mixin - shortcut, widget, background pickers."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Literal, Protocol, runtime_checkable

try:
    import xbmc
    import xbmcgui

    IN_KODI = True
except ImportError:
    IN_KODI = False


def _check_visible(visible: str) -> bool:
    """Evaluate a Kodi visibility condition.

    Returns True if condition passes or is empty.
    """
    if not visible:
        return True
    if not IN_KODI:
        return True
    return xbmc.getCondVisibility(visible)


@runtime_checkable
class PickerItem(Protocol):
    """Protocol for leaf items in picker hierarchy (Shortcut, Widget, Background)."""

    name: str
    label: str
    icon: str
    condition: str
    visible: str


@runtime_checkable
class PickerGroup(Protocol):
    """Protocol for group items in picker hierarchy."""

    name: str
    label: str
    icon: str
    condition: str
    visible: str
    items: list


from ..loaders import evaluate_condition, load_groupings
from ..localize import resolve_label
from ..models import (
    Action,
    Background,
    BackgroundGroup,
    Content,
    MenuItem,
    Shortcut,
    ShortcutGroup,
    Widget,
    WidgetGroup,
)
from ..providers import ContentProvider

if TYPE_CHECKING:
    from ..manager import MenuManager


class PickersMixin:
    """Mixin providing picker dialogs for shortcuts and widgets.

    This mixin implements:
    - Shortcut picker from groupings
    - Widget picker from groups/flat list
    - Content resolution (dynamic shortcuts/widgets)
    - Helper methods for action/path extraction

    Requires DialogBaseMixin to be mixed in first.
    """

    menu_id: str
    shortcuts_path: str
    manager: MenuManager | None
    items: list[MenuItem]

    if TYPE_CHECKING:
        def _get_selected_item(self) -> MenuItem | None: ...
        def _get_item_properties(self, item: MenuItem) -> dict[str, str]: ...
        def _refresh_selected_item(self) -> None: ...
        def _log(self, msg: str) -> None: ...

    def _choose_shortcut(self) -> None:
        """Choose a shortcut from groupings."""
        if not self.manager:
            return

        item = self._get_selected_item()
        if not item:
            return

        menus_path = Path(self.shortcuts_path) / "menus.xml"
        groups = load_groupings(menus_path)

        if not groups:
            xbmcgui.Dialog().notification(
                "No Shortcuts",
                "No shortcut groupings defined in skin",
            )
            return

        item_props = self._get_item_properties(item)

        shortcut = self._pick_shortcut(groups, item_props)
        if shortcut:
            action = self._get_shortcut_action(shortcut)
            if action is None:
                return

            self.manager.set_label(self.menu_id, item.name, shortcut.label)
            item.label = shortcut.label
            self.manager.set_action(self.menu_id, item.name, action)
            item.actions = [Action(action=action)] if action else []

            if shortcut.icon:
                self.manager.set_icon(self.menu_id, item.name, shortcut.icon)
                item.icon = shortcut.icon

            self._refresh_selected_item()

    def _get_shortcut_action(self, shortcut: Shortcut) -> str | None:
        """Get action from shortcut, showing playlist choice dialog if applicable."""
        if shortcut.action_play:
            return self._choose_playlist_action(shortcut)
        return shortcut.get_action() if hasattr(shortcut, "get_action") else shortcut.action

    def _choose_playlist_action(self, shortcut: Shortcut) -> str | None:
        """Show dialog asking what to do with a playlist shortcut."""
        from ..localize import LANGUAGE

        if shortcut.action_party:
            result = xbmcgui.Dialog().yesnocustom(  # type: ignore[attr-defined]
                LANGUAGE(32040),
                LANGUAGE(32060),
                customlabel=xbmc.getLocalizedString(589),
                nolabel=LANGUAGE(32061),
                yeslabel=LANGUAGE(32062),
            )
            if result == -1:
                return None
            if result == 0:
                return shortcut.action
            if result == 1:
                return shortcut.action_play
            return shortcut.action_party

        result = xbmcgui.Dialog().yesno(
            LANGUAGE(32040),
            LANGUAGE(32060),
            nolabel=LANGUAGE(32061),
            yeslabel=LANGUAGE(32062),
        )
        return shortcut.action_play if result else shortcut.action

    def _pick_shortcut(
        self, groups: list[ShortcutGroup], item_props: dict[str, str]
    ) -> Shortcut | None:
        """Pick a shortcut from groupings using generic hierarchy picker."""
        result = self._pick_from_hierarchy(
            groups,
            item_props,
            title="Choose Category",
            leaf_types=(Shortcut,),
            group_types=(ShortcutGroup,),
            default_leaf_icon="DefaultShortcut.png",
            default_group_icon="DefaultFolder.png",
            show_none=False,
            content_resolver=self._resolve_content_to_shortcuts,
            create_folder_group=lambda label, items: ShortcutGroup(
                name=f"folder-{label}",
                label=label,
                icon="DefaultFolder.png",
                items=items,
            ),
        )
        return result if isinstance(result, Shortcut) else None

    def _pick_widget_from_groups(
        self,
        items: list[WidgetGroup | Widget],
        item_props: dict[str, str],
        slot: str = "",
        show_get_more: bool = True,
    ) -> Widget | None | Literal[False]:
        """Show widget picker dialog with back navigation.

        Handles both standalone widgets and groups at the top level.

        Args:
            items: Widget groups and/or widgets to pick from
            item_props: Current item properties for condition evaluation
            slot: Current widget slot being edited (e.g., "widget", "widget.2")
            show_get_more: Whether to show "Get More..." option to browse addons

        Returns:
            Widget if selected, None if cancelled completely, False if "None" chosen.
        """
        current_widget = item_props.get(slot, "")

        custom_action = None
        if show_get_more:
            custom_action = (
                "Get More...",
                "DefaultAddonProgram.png",
                self._browse_widget_addons,
            )

        result = self._pick_from_hierarchy(
            items,
            item_props,
            title="Select Widget",
            leaf_types=(Widget,),
            group_types=(WidgetGroup,),
            default_leaf_icon="DefaultAddonNone.png",
            default_group_icon="DefaultFolder.png",
            show_none=True,
            current_value=current_widget,
            content_resolver=self._resolve_content_to_widgets,
            create_folder_group=lambda label, grp_items: WidgetGroup(
                name=f"folder-{label}",
                label=label,
                items=grp_items,
            ),
            custom_action=custom_action,
        )

        return result

    def _pick_widget_flat(
        self, widgets: list, item_props: dict[str, str] | None = None, slot: str = ""
    ) -> Widget | None | Literal[False]:
        """Pick from flat widget list.

        Args:
            widgets: List of (name, label, icon) tuples
            item_props: Current item properties for finding current widget
            slot: Widget slot name (e.g., "widget", "widget.2")

        Returns:
            Widget if selected, None if cancelled, False if "None" chosen.
        """
        current_widget = item_props.get(slot, "") if item_props else ""
        preselect = -1

        listitems = []
        none_item = xbmcgui.ListItem("None")
        none_item.setArt({"icon": "DefaultAddonNone.png"})
        listitems.append(none_item)

        for i, w in enumerate(widgets):
            listitem = xbmcgui.ListItem(resolve_label(w[1]))
            icon = w[2] if len(w) > 2 and w[2] else "DefaultAddonNone.png"
            listitem.setArt({"icon": icon})
            listitems.append(listitem)
            if preselect == -1 and w[0] == current_widget:
                preselect = i + 1  # +1 for "None" option

        selected = xbmcgui.Dialog().select(
            "Select Widget", listitems, useDetails=True, preselect=preselect
        )

        if selected == -1:
            return None
        if selected == 0:
            return False

        widget_name = widgets[selected - 1][0]
        if self.manager is None:
            return None
        return self.manager.config.get_widget(widget_name)

    def _resolve_content_to_widgets(self, content: Content) -> list[Widget]:
        """Resolve a Content reference to a list of Widget objects for the picker."""
        provider = ContentProvider()
        resolved = provider.resolve(content)

        widgets = []
        for item in resolved:
            widget = Widget(
                name=f"dynamic-{content.source}-{len(widgets)}",
                label=item.label,
                path=self._extract_path_from_action(item.action),
                type=content.target or "",
                target=self._map_target_to_window(content.target),
                icon=item.icon,
            )
            widgets.append(widget)

        return widgets

    def _resolve_content_to_shortcuts(self, content: Content) -> list[Shortcut]:
        """Resolve a Content reference to a list of Shortcut objects for the picker."""
        provider = ContentProvider()
        resolved = provider.resolve(content)

        shortcuts = []
        for item in resolved:
            shortcut = Shortcut(
                name=f"dynamic-{content.source}-{len(shortcuts)}",
                label=item.label,
                action=item.action,
                type=item.label2,
                icon=item.icon,
                action_play=item.action_play,
                action_party=item.action_party,
            )
            shortcuts.append(shortcut)

        return shortcuts

    def _extract_path_from_action(self, action: str) -> str:
        """Extract the path from an action string for widget use."""
        if action.lower().startswith("activatewindow("):
            inner = action[15:-1]
            parts = inner.split(",")
            if len(parts) >= 2:
                return parts[1].strip()
        elif action.lower().startswith("playmedia("):
            return action[10:-1]
        elif action.lower().startswith("runaddon("):
            addon_id = action[9:-1]
            return f"plugin://{addon_id}/"
        return action

    def _map_target_to_window(self, target: str) -> str:
        """Map content target to widget target window."""
        from ..constants import TARGET_MAP

        return TARGET_MAP.get(target.lower(), "videos") if target else "videos"

    def _browse_widget_addons(self) -> Widget | None:
        """Browse installed addons to select a widget path.

        Opens a dialog to browse video/audio/program addons that can be
        used as widget content sources.

        Returns:
            Widget if addon selected, None if cancelled.
        """
        addon_types = [
            ("video", "Video Addons", "DefaultAddonVideo.png"),
            ("audio", "Music Addons", "DefaultAddonMusic.png"),
            ("executable", "Program Addons", "DefaultAddonProgram.png"),
        ]

        listitems = []
        for _type_id, label, icon in addon_types:
            listitem = xbmcgui.ListItem(label)
            listitem.setArt({"icon": icon})
            listitems.append(listitem)

        selected = xbmcgui.Dialog().select(
            "Browse Addons", listitems, useDetails=True
        )

        if selected == -1:
            return None

        addon_type = addon_types[selected][0]

        # browse_type for Kodi API, widget_target for our properties
        if addon_type == "video":
            browse_type = "video"
            widget_target = "videos"
        elif addon_type == "audio":
            browse_type = "music"
            widget_target = "music"
        else:
            browse_type = "programs"
            widget_target = "programs"

        result = xbmcgui.Dialog().browse(
            0,  # Folder/file selection
            "Select Widget Source",
            browse_type,
            "",
            False,
            False,
            f"addons://{addon_type}/",
        )

        if not result:
            return None

        path = result[0] if isinstance(result, list) else result
        addon_name = path.split("/")[2] if path.count("/") >= 2 else "Widget"

        return Widget(
            name=f"custom-{addon_name}",
            label=addon_name,
            path=path,
            type=widget_target,
            target=widget_target,
            icon=f"DefaultAddon{addon_type.title()}.png",
        )

    def _nested_picker(
        self,
        title: str,
        items: list[tuple[str, str, str]],
        on_select,
        show_none: bool = True,
        current_value: str = "",
    ):
        """Generic picker that supports sub-dialogs with back navigation.

        Args:
            title: Dialog title
            items: List of (id, label, icon) tuples
            on_select: Callback when item selected. Returns:
                - any value: final selection, exit picker
                - None: sub-dialog cancelled, return to this picker
            show_none: Whether to show "None" option
            current_value: Current item ID to preselect

        Returns:
            Result from on_select, or False if cancelled completely
        """
        preselect = -1
        offset = 1 if show_none else 0
        for i, (item_id, _label, _icon) in enumerate(items):
            if item_id == current_value:
                preselect = i + offset
                break

        while True:
            listitems = []
            if show_none:
                none_item = xbmcgui.ListItem("None")
                none_item.setArt({"icon": "DefaultAddonNone.png"})
                listitems.append(none_item)

            for _item_id, label, icon in items:
                listitem = xbmcgui.ListItem(resolve_label(label))
                listitem.setArt({"icon": icon or "DefaultAddonNone.png"})
                listitems.append(listitem)

            selected = xbmcgui.Dialog().select(
                title, listitems, useDetails=True, preselect=preselect
            )

            if selected == -1:
                return False  # Cancelled completely

            if show_none and selected == 0:
                return "none"  # User chose "None"

            preselect = selected

            offset = 1 if show_none else 0
            item_id = items[selected - offset][0]

            result = on_select(item_id)
            if result is not None:
                return result

    def _pick_from_hierarchy(
        self,
        items: list,
        item_props: dict[str, str],
        *,
        title: str = "Select",
        leaf_types: tuple = (Shortcut,),
        group_types: tuple = (ShortcutGroup,),
        default_leaf_icon: str = "DefaultShortcut.png",
        default_group_icon: str = "DefaultFolder.png",
        show_none: bool = False,
        current_value: str = "",
        content_resolver: Callable[[Content], list] | None = None,
        create_folder_group: Callable[[str, list], Any] | None = None,
        custom_action: tuple[str, str, Callable[[], Any | None]] | None = None,
    ) -> Any | None | Literal[False]:
        """Generic hierarchical picker with back navigation.

        Works with any types that have: name, label, icon, condition, visible.
        Groups additionally have an items list.

        Args:
            items: List of items/groups to pick from
            item_props: Current item properties for condition evaluation
            title: Dialog title
            leaf_types: Tuple of types considered leaf items (selectable)
            group_types: Tuple of types considered groups (navigable)
            default_leaf_icon: Default icon for leaf items
            default_group_icon: Default icon for groups
            show_none: Whether to show "None" option at top level
            current_value: Current item name for preselect
            content_resolver: Optional function to resolve Content to list of items
            create_folder_group: Optional function to create folder group from (label, items)
            custom_action: Optional tuple of (label, icon, callback) for a custom action
                shown at the bottom of the list. The callback should return an item if
                successful, or None to return to the picker.

        Returns:
            Selected leaf item, None if cancelled, False if "None" chosen.
        """
        visible_items = self._filter_picker_items(
            items, item_props, leaf_types, group_types, content_resolver, create_folder_group
        )

        if not visible_items:
            xbmcgui.Dialog().notification("No Items", "No items available")
            return None

        preselect = -1
        offset = 1 if show_none else 0

        for i, vis_item in enumerate(visible_items):
            if hasattr(vis_item, "name") and vis_item.name == current_value:
                preselect = i + offset
                break

        while True:
            listitems = []
            if show_none:
                none_item = xbmcgui.ListItem("None")
                none_item.setArt({"icon": "DefaultAddonNone.png"})
                listitems.append(none_item)

            for vis_item in visible_items:
                label = resolve_label(vis_item.label)
                if isinstance(vis_item, group_types):
                    label = f"{label} >"
                    icon = vis_item.icon if vis_item.icon else default_group_icon
                else:
                    icon = vis_item.icon if vis_item.icon else default_leaf_icon
                listitem = xbmcgui.ListItem(label)
                listitem.setArt({"icon": icon})
                listitems.append(listitem)

            if custom_action:
                action_label, action_icon, _callback = custom_action
                action_item = xbmcgui.ListItem(action_label)
                action_item.setArt({"icon": action_icon})
                listitems.append(action_item)

            selected = xbmcgui.Dialog().select(
                title, listitems, useDetails=True, preselect=preselect
            )

            if selected == -1:
                return None  # Cancelled

            if show_none and selected == 0:
                return False

            if custom_action and selected == len(listitems) - 1:
                _label, _icon, callback = custom_action
                result = callback()
                if result is not None:
                    return result
                continue

            preselect = selected
            selected_item = visible_items[selected - offset]

            if isinstance(selected_item, leaf_types):
                return selected_item

            result = self._pick_from_hierarchy_group(
                selected_item,
                item_props,
                leaf_types=leaf_types,
                group_types=group_types,
                default_leaf_icon=default_leaf_icon,
                default_group_icon=default_group_icon,
                content_resolver=content_resolver,
                create_folder_group=create_folder_group,
            )

            if result is not None:
                return result

    def _pick_from_hierarchy_group(
        self,
        group,
        item_props: dict[str, str],
        *,
        leaf_types: tuple,
        group_types: tuple,
        default_leaf_icon: str,
        default_group_icon: str,
        content_resolver: Callable[[Content], list] | None = None,
        create_folder_group: Callable[[str, list], Any] | None = None,
    ) -> Any | None:
        """Pick from items within a group with back navigation."""
        visible_items = self._filter_picker_items(
            group.items, item_props, leaf_types, group_types, content_resolver, create_folder_group
        )

        if not visible_items:
            xbmcgui.Dialog().notification("No Items", "No items available in this group")
            return None

        if len(visible_items) == 1 and isinstance(visible_items[0], leaf_types):
            return visible_items[0]

        preselect = -1
        while True:
            listitems = []
            for vis_item in visible_items:
                label = resolve_label(vis_item.label)
                if isinstance(vis_item, group_types):
                    label = f"{label} >"
                    icon = vis_item.icon if vis_item.icon else default_group_icon
                else:
                    icon = vis_item.icon if vis_item.icon else default_leaf_icon
                listitem = xbmcgui.ListItem(label)
                listitem.setArt({"icon": icon})
                listitems.append(listitem)

            title = resolve_label(group.label)
            selected = xbmcgui.Dialog().select(
                title, listitems, useDetails=True, preselect=preselect
            )

            if selected == -1:
                return None  # Go back

            preselect = selected
            selected_item = visible_items[selected]

            if isinstance(selected_item, leaf_types):
                return selected_item

            result = self._pick_from_hierarchy_group(
                selected_item,
                item_props,
                leaf_types=leaf_types,
                group_types=group_types,
                default_leaf_icon=default_leaf_icon,
                default_group_icon=default_group_icon,
                content_resolver=content_resolver,
                create_folder_group=create_folder_group,
            )

            if result is not None:
                return result

    def _filter_picker_items(
        self,
        items: list,
        item_props: dict[str, str],
        leaf_types: tuple,
        group_types: tuple,
        content_resolver: Callable[[Content], list] | None = None,
        create_folder_group: Callable[[str, list], Any] | None = None,
    ) -> list:
        """Filter and resolve picker items based on conditions and visibility."""
        visible_items = []

        for item in items:
            if isinstance(item, Content):
                if item.condition and not evaluate_condition(item.condition, item_props):
                    continue
                if item.visible and not _check_visible(item.visible):
                    continue
                if content_resolver:
                    resolved = content_resolver(item)
                    if item.folder and resolved and create_folder_group:
                        folder = create_folder_group(item.folder, resolved)
                        visible_items.append(folder)
                    else:
                        visible_items.extend(resolved)
            elif isinstance(item, (*leaf_types, *group_types)):
                if not _check_visible(getattr(item, "visible", "")):
                    continue
                condition = getattr(item, "condition", "")
                if condition and not evaluate_condition(condition, item_props):
                    continue
                visible_items.append(item)

        return visible_items

    def _pick_background(
        self, item_props: dict[str, str], current_value: str = ""
    ) -> Background | None | Literal[False]:
        """Pick a background from groupings.

        Returns:
            Background if selected, None if cancelled, False if "None" chosen.
        """
        if not self.manager:
            return None

        groupings = self.manager.config.background_groupings
        if not groupings:
            xbmcgui.Dialog().notification("No Backgrounds", "No backgrounds defined")
            return None

        return self._pick_from_hierarchy(
            groupings,
            item_props,
            title="Select Background",
            leaf_types=(Background,),
            group_types=(BackgroundGroup,),
            default_leaf_icon="DefaultPicture.png",
            default_group_icon="DefaultFolder.png",
            show_none=True,
            current_value=current_value,
        )
