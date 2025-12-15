"""Subdialog management mixin - submenu editing, widget slots, onclose handling."""

from __future__ import annotations

from typing import TYPE_CHECKING

try:
    import xbmcgui

    IN_KODI = True
except ImportError:
    IN_KODI = False

from ..loaders import evaluate_condition
from ..models import Menu, MenuItem

if TYPE_CHECKING:
    from ..manager import MenuManager
    from ..models import IconSource, PropertySchema
    from ..models.menu import SubDialog


class SubdialogsMixin:
    """Mixin providing subdialog management - submenu editing, widget slots.

    This mixin implements:
    - Edit submenu spawning
    - Subdialog spawning with mode/suffix
    - Onclose action handling
    - Custom widget menu creation

    Requires DialogBaseMixin to be mixed in first.
    """

    # Type hints for mixin - actual values come from base/subclass
    menu_id: str
    shortcuts_path: str
    manager: MenuManager | None
    property_schema: PropertySchema | None
    icon_sources: list[IconSource]
    show_context_menu: bool
    _subdialogs: dict[int, SubDialog]
    _dialog_xml: str
    _skin_path: str

    if TYPE_CHECKING:
        # Methods from DialogBaseMixin - only for type checking
        def _get_selected_index(self) -> int: ...
        def _get_selected_item(self) -> MenuItem | None: ...
        def _get_item_properties(self, item: MenuItem) -> dict[str, str]: ...
        def _refresh_selected_item(self) -> None: ...
        def _log(self, msg: str) -> None: ...

        # Methods from WindowXMLDialog (must be available through inheritance)
        def setProperty(self, key: str, value: str) -> None: ...
        def clearProperty(self, key: str) -> None: ...

    def _edit_submenu(self) -> None:
        """Spawn child dialog to edit submenu for selected item."""
        item = self._get_selected_item()
        if not item:
            return

        if not self.manager:
            return

        # Check if submenus are allowed for this menu
        menu = self.manager.config.get_menu(self.menu_id)
        if menu and not menu.allow.submenus:
            xbmcgui.Dialog().notification("Not Allowed", "Submenus not enabled for this menu")
            return

        # Check if item has a submenu (submenu or fall back to item name)
        submenu_name = item.submenu or item.name
        submenu = self.manager.config.get_menu(submenu_name)
        if not submenu:
            xbmcgui.Dialog().notification("No Submenu", f"No submenu defined for '{item.label}'")
            return

        # Hide parent while child is open
        self.setProperty("additionalDialog", "true")

        # Build subdialogs list from dict for sharing
        subdialogs_list = list(self._subdialogs.values())

        # Import here to avoid circular imports
        from . import ManagementDialog

        # Spawn child dialog with shared manager, schema, and icon sources
        child = ManagementDialog(
            self._dialog_xml,
            self._skin_path,
            "Default",
            menu_id=submenu_name,
            shortcuts_path=self.shortcuts_path,
            manager=self.manager,
            property_schema=self.property_schema,
            icon_sources=self.icon_sources,
            show_context_menu=self.show_context_menu,
            subdialogs=subdialogs_list,
        )
        child.doModal()
        del child

        # Show parent again (child edits different menu, no refresh needed)
        self.clearProperty("additionalDialog")

    def _spawn_subdialog(self, subdialog: SubDialog) -> None:
        """Spawn a child dialog for a subdialog definition.

        Opens the subdialog, and after it closes, evaluates any onclose actions.
        Onclose actions can trigger follow-up dialogs based on conditions.

        Args:
            subdialog: The subdialog definition containing the mode, suffix, and onclose
        """
        self._log(f"Spawning subdialog with mode: {subdialog.mode}, suffix: {subdialog.suffix}")

        item = self._get_selected_item()
        if not item:
            return

        # Open the subdialog
        self._open_subdialog(subdialog)

        # After subdialog closes, check onclose actions
        if subdialog.onclose:
            self._handle_onclose(subdialog, item)

    def _handle_onclose(self, subdialog: SubDialog, item: MenuItem) -> None:
        """Handle onclose actions after a subdialog closes.

        Evaluates each onclose action's condition against the current item state.
        The first matching action is executed.

        Args:
            subdialog: The subdialog definition with onclose actions
            item: The original menu item (used as fallback)
        """
        if not self.manager:
            return

        # Re-fetch item to get updated properties after subdialog edits
        current_item = self._get_selected_item()
        if not current_item:
            return

        # Get item properties for condition evaluation
        item_props = self._get_item_properties(current_item)

        for action in subdialog.onclose:
            # Check condition - skip if condition doesn't match
            if action.condition and not evaluate_condition(action.condition, item_props):
                continue

            # Execute the action
            if action.action == "menu" and action.menu:
                # Substitute {item} placeholder with current item name
                menu_name = action.menu.replace("{item}", current_item.name)
                self._log(f"Onclose: opening menu {menu_name}")
                self._open_onclose_menu(menu_name, subdialog)
                return  # Only execute first matching action

    def _open_onclose_menu(self, menu_name: str, subdialog: SubDialog) -> None:
        """Open a menu from an onclose action.

        Used for custom widget editing where we open the custom menu
        after the widget picker closes with widgetType=custom.

        Args:
            menu_name: Name of the menu to open
            subdialog: The parent subdialog definition (for dialog mode)
        """
        if not self.manager:
            return

        self._log(f"Opening onclose menu: {menu_name}")

        # Ensure menu exists (create if needed for custom widget menus)
        menu = self.manager.config.get_menu(menu_name)
        if not menu:
            menu = Menu(name=menu_name, is_submenu=True)
            self.manager.config.menus.append(menu)
            self._log(f"Created new menu from onclose: {menu_name}")

        # Get current selected index to pass to child
        selected_index = self._get_selected_index()

        # Hide parent while child is open
        self.setProperty("additionalDialog", "true")

        # Build subdialogs list from dict for sharing
        subdialogs_list = list(self._subdialogs.values())

        # Determine dialog mode for custom menu
        # Use the subdialog mode but indicate it's a custom menu
        dialog_mode = f"custom-{subdialog.mode}" if subdialog.mode else "customwidget"

        # Import here to avoid circular imports
        from . import ManagementDialog

        # Spawn child dialog to edit the menu
        child = ManagementDialog(
            self._dialog_xml,
            self._skin_path,
            "Default",
            menu_id=menu_name,
            shortcuts_path=self.shortcuts_path,
            manager=self.manager,
            property_schema=self.property_schema,
            icon_sources=self.icon_sources,
            show_context_menu=self.show_context_menu,
            subdialogs=subdialogs_list,
            dialog_mode=dialog_mode,
            selected_index=selected_index,
        )
        child.doModal()
        del child

        # Show parent again
        self.clearProperty("additionalDialog")
        self._refresh_selected_item()

    def _open_subdialog(self, subdialog: SubDialog) -> None:
        """Open the subdialog for widget/property editing.

        Args:
            subdialog: The subdialog definition
        """
        # Get current selected index to pass to child
        selected_index = self._get_selected_index()

        # Hide parent while child is open
        self.setProperty("additionalDialog", "true")

        # Build subdialogs list from dict for sharing
        subdialogs_list = list(self._subdialogs.values())

        # Import here to avoid circular imports
        from . import ManagementDialog

        # Spawn child dialog with same menu but different dialog_mode and suffix
        child = ManagementDialog(
            self._dialog_xml,
            self._skin_path,
            "Default",
            menu_id=self.menu_id,  # Same menu
            shortcuts_path=self.shortcuts_path,
            manager=self.manager,
            property_schema=self.property_schema,
            icon_sources=self.icon_sources,
            show_context_menu=self.show_context_menu,
            subdialogs=subdialogs_list,
            dialog_mode=subdialog.mode,  # Different mode
            property_suffix=subdialog.suffix,  # Property suffix for this widget slot
            setfocus=subdialog.setfocus,  # Focus control
            selected_index=selected_index,  # Preserve selection
        )
        child.doModal()
        del child

        self._clear_subdialog_list()

        # Clear all visibility properties together
        self.clearProperty("additionalDialog")
        home = xbmcgui.Window(10000)
        home.clearProperty("skinshortcuts-suffix")
        home.clearProperty("skinshortcuts-dialog")

        self._refresh_selected_item()
