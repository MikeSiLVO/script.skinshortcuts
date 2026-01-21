"""Item operations mixin - add, delete, move, label, icon, action."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

try:
    import xbmc
    import xbmcgui

    IN_KODI = True
except ImportError:
    IN_KODI = False

from ..localize import resolve_label
from ..models import Action, BrowseSource, IconSource, MenuItem

if TYPE_CHECKING:
    from ..manager import MenuManager
    from ..models import PropertySchema


class ItemsMixin:
    """Mixin providing item operations - add, delete, move, label, icon, action.

    This mixin implements:
    - Add/delete/move items
    - Set label, icon, action
    - Toggle disabled state
    - Restore deleted items
    - Reset item to defaults
    - Context menu
    - File/image browsing with sources

    Requires DialogBaseMixin to be mixed in first.
    """

    menu_id: str
    manager: MenuManager | None
    items: list[MenuItem]
    property_schema: PropertySchema | None
    icon_sources: list[IconSource]
    shortcuts_path: str

    if TYPE_CHECKING:
        def _get_selected_index(self) -> int: ...
        def _get_selected_item(self) -> MenuItem | None: ...
        def _get_selected_listitem(self) -> xbmcgui.ListItem | None: ...
        def _rebuild_list(self, focus_index: int | None = None) -> None: ...
        def _refresh_selected_item(self) -> None: ...
        def _update_deleted_property(self) -> None: ...
        def _load_items(self) -> None: ...
        def _update_window_properties(self) -> None: ...
        def _suffixed_name(self, name: str) -> str: ...
        def _log(self, msg: str) -> None: ...

    def _add_item(self) -> None:
        """Add a new item after the current selection."""
        if not self.manager:
            return

        index = self._get_selected_index()
        new_item = self.manager.add_item(self.menu_id, after_index=index)
        if new_item:
            insert_pos = index + 1 if index >= 0 else 0
            self._rebuild_list(focus_index=insert_pos)

    def _delete_item(self) -> None:
        """Delete the selected item."""
        if not self.manager:
            return

        item = self._get_selected_item()
        if not item:
            return

        if item.required:
            xbmcgui.Dialog().ok("Cannot Delete", f"'{item.label}' is required.")
            return

        if item.protection and item.protection.protects_delete():
            heading = resolve_label(item.protection.heading) or "Delete Item"
            label = resolve_label(item.label)
            message = resolve_label(item.protection.message) or f"Delete '{label}'?"
            if not xbmcgui.Dialog().yesno(heading, message):
                return

        index = self._get_selected_index()
        self.manager.remove_item(self.menu_id, item.name)

        self._rebuild_list(focus_index=min(index, len(self.items) - 1))
        self._update_deleted_property()

    def _move_item(self, direction: int) -> None:
        """Move item up (-1) or down (1)."""
        if not self.manager:
            return

        item = self._get_selected_item()
        if not item:
            return

        index = self._get_selected_index()
        new_index = index + direction
        if self.manager.move_item(self.menu_id, item.name, direction):
            self._rebuild_list(focus_index=new_index)

    def _set_label(self) -> None:
        """Change the label of selected item."""
        if not self.manager:
            return

        item = self._get_selected_item()
        if not item:
            return

        from ..localize import resolve_label

        current_label = resolve_label(item.label)
        keyboard = xbmc.Keyboard(current_label, xbmc.getLocalizedString(528))
        keyboard.doModal()
        if keyboard.isConfirmed():
            new_label = keyboard.getText()
            self.manager.set_label(self.menu_id, item.name, new_label)
            item.label = new_label
            self._refresh_selected_item()

    def _set_icon(self) -> None:
        """Browse for a new icon using icon sources from menus.xml."""
        if not self.manager:
            return

        item = self._get_selected_item()
        if not item:
            return

        icon = self._browse_with_sources(
            sources=self.icon_sources,
            title=xbmc.getLocalizedString(1030),  # "Choose icon"
            browse_type=2,  # Image file
            mask=".png|.jpg|.gif",
            item_properties=item.properties,
        )
        if icon and isinstance(icon, str):
            self.manager.set_icon(self.menu_id, item.name, icon)
            item.icon = icon
            self._refresh_selected_item()

    def _set_action(self) -> None:
        """Set a custom action."""
        if not self.manager:
            return

        item = self._get_selected_item()
        if not item:
            return

        if item.protection and item.protection.protects_action():
            heading = resolve_label(item.protection.heading) or "Modify Action"
            label = resolve_label(item.label)
            message = resolve_label(item.protection.message) or f"Modify '{label}'?"
            if not xbmcgui.Dialog().yesno(heading, message):
                return

        keyboard = xbmc.Keyboard(item.action or "", "Enter action")
        keyboard.doModal()
        if keyboard.isConfirmed():
            action = keyboard.getText()
            self.manager.set_action(self.menu_id, item.name, action or "noop")
            item.actions = [Action(action=action or "noop")]
            self._refresh_selected_item()

    def _toggle_disabled(self) -> None:
        """Toggle the disabled state of the selected item."""
        if not self.manager:
            return

        item = self._get_selected_item()
        if not item:
            return

        if item.required and not item.disabled:
            xbmcgui.Dialog().ok("Cannot Disable", f"'{item.label}' is required.")
            return

        new_state = not item.disabled
        self.manager.set_disabled(self.menu_id, item.name, new_state)
        self._refresh_selected_item()

    def _restore_deleted_item(self) -> None:
        """Show picker to restore a previously deleted item."""
        if not self.manager:
            return

        removed = self.manager.get_removed_items(self.menu_id)
        if not removed:
            xbmcgui.Dialog().notification("No Deleted Items", "No items to restore")
            return

        labels = [resolve_label(item.label) for item in removed]
        selected = xbmcgui.Dialog().select("Restore Deleted Item", labels)

        if selected < 0:
            return

        item = removed[selected]
        self.manager.restore_item(self.menu_id, item)
        self._load_items()

        restored_index = len(self.items) - 1
        for i, it in enumerate(self.items):
            if it.name == item.name:
                restored_index = i
                break

        self._rebuild_list(focus_index=restored_index)
        self._update_deleted_property()

    def _reset_current_item(self) -> None:
        """Reset current item to skin defaults."""
        if not self.manager:
            return

        item = self._get_selected_item()
        if not item:
            return

        display_label = resolve_label(item.label)
        if not xbmcgui.Dialog().yesno("Reset Item", f"Reset '{display_label}' to defaults?"):
            return

        if not self.manager.reset_item(self.menu_id, item.name):
            return

        index = self._get_selected_index()
        self._rebuild_list(focus_index=index)
        self._update_window_properties()

    def _browse_with_sources(
        self,
        sources: list[IconSource] | list[BrowseSource],
        title: str,
        browse_type: int,
        mask: str = "",
        item_properties: dict[str, str] | None = None,
    ) -> str | None:
        """Browse for a file using configured sources.

        Args:
            sources: List of IconSource or BrowseSource objects
            title: Dialog title
            browse_type: Kodi browse type (0=folder, 2=image file)
            mask: File mask for filtering (e.g., ".png|.jpg")
            item_properties: Current item properties for condition evaluation

        Returns:
            Selected path, or None if cancelled
        """
        from ..conditions import evaluate_condition

        props = item_properties or {}

        visible_sources = []
        for source in sources:
            if source.condition and not evaluate_condition(source.condition, props):
                continue
            visible = getattr(source, "visible", "")
            if visible and not xbmc.getCondVisibility(visible):
                continue
            visible_sources.append(source)

        if not visible_sources:
            result = xbmcgui.Dialog().browse(browse_type, title, "files", mask)
            return result if isinstance(result, str) else None

        if len(visible_sources) == 1 and not visible_sources[0].label:
            path = visible_sources[0].path
            if path.lower() == "browse":
                result = xbmcgui.Dialog().browse(browse_type, title, "files", mask)
            else:
                result = xbmcgui.Dialog().browse(
                    browse_type, title, "files", mask, False, False, path
                )
            return result if isinstance(result, str) else None

        while True:
            listitems = []
            for source in visible_sources:
                label = resolve_label(source.label) if source.label else source.path
                listitem = xbmcgui.ListItem(label)
                if source.icon:
                    listitem.setArt({"icon": source.icon})
                listitems.append(listitem)

            selected = xbmcgui.Dialog().select(title, listitems, useDetails=True)

            if selected == -1:
                return None  # Cancelled

            source = visible_sources[selected]
            path = source.path

            if path.lower() == "browse":
                result = xbmcgui.Dialog().browse(browse_type, title, "files", mask)
            else:
                result = xbmcgui.Dialog().browse(
                    browse_type, title, "files", mask, False, False, path
                )

            if result and isinstance(result, str):
                return result

    def _show_context_menu(self) -> None:
        """Show context menu for selected item."""
        item = self._get_selected_item()
        if not item:
            return

        options = [
            ("Edit Label", self._set_label),
            ("Edit Action", self._set_action),
            ("Change Icon", self._set_icon),
            ("Edit Submenu", self._edit_submenu),
            ("Delete", self._delete_item),
        ]

        labels = [opt[0] for opt in options]
        selected = xbmcgui.Dialog().contextmenu(labels)

        if selected >= 0:
            options[selected][1]()

    def _set_item_property(
        self,
        item: MenuItem,
        name: str,
        value: str | None,
        related: Mapping[str, str | None] | None = None,
        apply_suffix: bool = True,
    ) -> None:
        """Unified property setter for menu items.

        All properties (including widget and background) are stored in item.properties.
        Updates both the manager (for persistence) and local item state (for UI).

        Args:
            item: The menu item to update
            name: Property name (e.g., "widget", "background", "widgetStyle")
            value: Property value, or None/empty string to clear
            related: Optional dict of related properties to auto-populate
                     (e.g., {"widgetLabel": "Movies", "widgetPath": "..."})
            apply_suffix: If True, apply property_suffix to name and related props.
                         Set to False for shared properties like widget/background.
        """
        if not self.manager:
            return

        prop_name = self._suffixed_name(name) if apply_suffix else name

        self.manager.set_custom_property(self.menu_id, item.name, prop_name, value)
        if value:
            item.properties[prop_name] = value
        else:
            if prop_name in item.properties:
                del item.properties[prop_name]
            listitem = self._get_selected_listitem()
            if listitem:
                listitem.setProperty(prop_name, "")
                listitem.setProperty(f"{prop_name}Label", "")

        if related:
            for rel_name, rel_value in related.items():
                rel_prop_name = self._suffixed_name(rel_name) if apply_suffix else rel_name
                self.manager.set_custom_property(
                    self.menu_id, item.name, rel_prop_name, rel_value
                )
                if rel_value:
                    item.properties[rel_prop_name] = rel_value
                else:
                    if rel_prop_name in item.properties:
                        del item.properties[rel_prop_name]
                    listitem = self._get_selected_listitem()
                    if listitem:
                        listitem.setProperty(rel_prop_name, "")

    def _edit_submenu(self) -> None:
        """Edit submenu - implemented by SubdialogsMixin."""
        raise NotImplementedError
