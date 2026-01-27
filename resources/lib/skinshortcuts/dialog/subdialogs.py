"""Subdialog management mixin - submenu editing, widget slots, onclose handling."""

from __future__ import annotations

from typing import TYPE_CHECKING

try:
    import xbmcgui

    IN_KODI = True
except ImportError:
    IN_KODI = False

from ..loaders import evaluate_condition
from ..models import MenuItem

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
        def _get_selected_index(self) -> int: ...
        def _get_selected_item(self) -> MenuItem | None: ...
        def _get_item_properties(self, item: MenuItem) -> dict[str, str]: ...
        def _refresh_selected_item(self) -> None: ...
        def _clear_subdialog_list(self) -> None: ...
        def _log(self, msg: str) -> None: ...

        def setProperty(self, key: str, value: str) -> None: ...
        def clearProperty(self, key: str) -> None: ...

    def _edit_submenu(self) -> None:
        """Spawn child dialog to edit submenu for selected item."""
        item = self._get_selected_item()
        if not item:
            return

        if not self.manager:
            return

        menu = self.manager.config.get_menu(self.menu_id)
        if menu and not menu.allow.submenus:
            xbmcgui.Dialog().notification("Not Allowed", "Submenus not enabled for this menu")
            return

        submenu_name = item.submenu or item.name
        if submenu_name not in self.manager.working:
            self.manager._ensure_working_menu(submenu_name)

        self.setProperty("additionalDialog", "true")
        subdialogs_list = list(self._subdialogs.values())

        from . import ManagementDialog

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

        self._open_subdialog(subdialog)

        if subdialog.onclose:
            self._handle_onclose(subdialog, item)

    def _handle_onclose(self, subdialog: SubDialog, item: MenuItem) -> None:
        """Handle onclose actions after a subdialog closes.

        Evaluates each onclose action's condition against the current item state.
        The first matching action is executed.

        Supports special menu placeholders:
        - {customWidget} - custom widget slot 1
        - {customWidget.2} - custom widget slot 2, etc.

        Args:
            subdialog: The subdialog definition with onclose actions
            item: The original menu item (used as fallback)
        """
        if not self.manager:
            return

        current_item = self._get_selected_item()
        if not current_item:
            return

        item_props = self._get_item_properties(current_item)

        for action in subdialog.onclose:
            if action.condition and not evaluate_condition(action.condition, item_props):
                continue

            if action.action == "menu" and action.menu:
                menu_name = self._resolve_menu_reference(action.menu, current_item, subdialog)
                if menu_name:
                    self._log(f"Onclose: opening menu {menu_name}")
                    self._open_onclose_menu(menu_name, subdialog)
                return

    def _resolve_menu_reference(
        self, menu_ref: str, item: MenuItem, subdialog: SubDialog
    ) -> str:
        """Resolve a menu reference from an onclose action.

        Handles special placeholders:
        - {customWidget} or {customWidget.N} - get/create custom widget menu
        - {item}.X - legacy format, converted to explicit reference

        Args:
            menu_ref: The menu reference string from onclose action
            item: The current menu item
            subdialog: The subdialog definition

        Returns:
            Resolved menu name/ID
        """
        if not self.manager:
            return ""

        if menu_ref.startswith("{customWidget"):
            suffix = ""
            if "." in menu_ref:
                suffix = "." + menu_ref.split(".")[1].rstrip("}")
            else:
                suffix = subdialog.suffix or ""

            prop_name = f"customWidget{suffix}"
            menu_id = item.properties.get(prop_name)

            if not menu_id:
                menu_id = self.manager.create_custom_widget_menu(
                    self.menu_id, item.name, suffix
                )
                self._log(f"Created custom widget menu: {menu_id}")

            return menu_id

        # Handle legacy {item}.customwidget format - convert to explicit reference
        if "{item}" in menu_ref and ".customwidget" in menu_ref:
            resolved = menu_ref.replace("{item}", item.name)
            suffix = ""
            if ".customwidget." in resolved:
                suffix = "." + resolved.split(".customwidget.")[1]
            elif resolved.endswith(".customwidget"):
                suffix = ""
            else:
                suffix = subdialog.suffix or ""

            prop_name = f"customWidget{suffix}"
            menu_id = item.properties.get(prop_name)

            if not menu_id:
                menu_id = self.manager.create_custom_widget_menu(
                    self.menu_id, item.name, suffix
                )
                self._log(f"Created custom widget menu (legacy): {menu_id}")

            return menu_id

        return menu_ref.replace("{item}", item.name)

    def _open_onclose_menu(self, menu_name: str, subdialog: SubDialog) -> None:
        """Open a menu from an onclose action.

        Args:
            menu_name: Name of the menu to open (already resolved)
            subdialog: The parent subdialog definition (for dialog mode)
        """
        if not self.manager:
            return

        self._log(f"Opening onclose menu: {menu_name}")

        menu = self.manager.config.get_menu(menu_name)
        if not menu:
            menu = self.manager.working.get(menu_name)
        if not menu:
            self._log(f"Menu not found: {menu_name}")
            return

        selected_index = self._get_selected_index()

        self.setProperty("additionalDialog", "true")
        subdialogs_list = list(self._subdialogs.values())
        dialog_mode = f"custom-{subdialog.mode}" if subdialog.mode else "customwidget"

        from . import ManagementDialog

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

        self.clearProperty("additionalDialog")
        self._refresh_selected_item()

    def _open_subdialog(self, subdialog: SubDialog) -> None:
        """Open the subdialog for widget/property editing.

        Args:
            subdialog: The subdialog definition
        """
        selected_index = self._get_selected_index()

        self.setProperty("additionalDialog", "true")
        subdialogs_list = list(self._subdialogs.values())

        from . import ManagementDialog

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

        self.clearProperty("additionalDialog")
        home = xbmcgui.Window(10000)
        home.clearProperty("skinshortcuts-suffix")
        home.clearProperty("skinshortcuts-dialog")

        self._refresh_selected_item()
