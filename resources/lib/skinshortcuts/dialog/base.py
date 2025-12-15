"""Core dialog class with initialization and event handling."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

try:
    import xbmc
    import xbmcgui
    import xbmcvfs

    IN_KODI = True
except ImportError:
    IN_KODI = False

from ..loaders import evaluate_condition, load_menu_config, load_properties
from ..localize import resolve_label
from ..manager import MenuManager
from ..models import MenuItem, PropertySchema
from ..providers.content import clear_content_cache

if TYPE_CHECKING:
    from ..models import IconSource
    from ..models.menu import SubDialog

# Control IDs (matching v2 for compatibility)
CONTROL_LIST = 211  # Menu items list
CONTROL_SUBDIALOG_LIST = 212  # Subdialog context list
CONTROL_ADD = 301  # Add item
CONTROL_DELETE = 302  # Delete item
CONTROL_MOVE_UP = 303  # Move up
CONTROL_MOVE_DOWN = 304  # Move down
CONTROL_SET_LABEL = 305  # Change label
CONTROL_SET_ICON = 306  # Change icon
CONTROL_SET_ACTION = 307  # Change action
CONTROL_RESTORE_DELETED = 311  # Restore a deleted item
CONTROL_RESET_ITEM = 312  # Reset current item to defaults
# Widget/background buttons are now schema-driven via properties.xml
CONTROL_TOGGLE_DISABLED = 313  # Enable/disable item
CONTROL_CHOOSE_SHORTCUT = 401  # Choose shortcut/action from groupings
CONTROL_EDIT_SUBMENU = 405  # Edit submenu

# Actions
ACTION_CANCEL = (9, 10, 92, 216, 247, 257, 275, 61467, 61448)
ACTION_CONTEXT = (117,)


def get_shortcuts_path() -> str:
    """Get path to current skin's shortcuts folder."""
    if not IN_KODI:
        return ""
    skin_path = xbmcvfs.translatePath("special://skin/")
    return str(Path(skin_path) / "shortcuts")


class DialogBaseMixin(xbmcgui.WindowXMLDialog):
    """Core dialog functionality - initialization, list management, event routing.

    This mixin provides:
    - Constructor with all shared state setup
    - onInit/close lifecycle methods
    - List control management (display, rebuild, refresh)
    - Property access helpers
    - Event routing (onClick/onAction)

    Inherits from WindowXMLDialog for type checking. At runtime, the final
    ManagementDialog class also inherits from WindowXMLDialog, so the MRO
    is correct.
    """


    # Type hints for mixin - actual values come from subclass or WindowXMLDialog
    menu_id: str
    shortcuts_path: str
    manager: MenuManager | None
    items: list[MenuItem]
    property_schema: PropertySchema | None
    icon_sources: list[IconSource]
    show_context_menu: bool
    dialog_mode: str
    property_suffix: str
    is_child: bool
    changes_saved: bool
    _shared_manager: MenuManager | None
    _shared_schema: PropertySchema | None
    _shared_icon_sources: list[IconSource] | None
    _shared_show_context_menu: bool | None
    _shared_subdialogs: list[SubDialog] | None
    _subdialogs: dict[int, SubDialog]
    _setfocus: int | None
    _selected_index: int | None
    _dialog_xml: str
    _skin_path: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.menu_id = kwargs.get("menu_id", "mainmenu")
        self.shortcuts_path = kwargs.get("shortcuts_path", get_shortcuts_path())

        # Accept shared manager from parent dialog, or create in onInit
        self._shared_manager = kwargs.get("manager")
        self.manager = None
        self.items = []

        # Property schema (shared with child dialogs)
        self._shared_schema = kwargs.get("property_schema")
        self.property_schema = None

        # Icon sources (loaded from menus.xml)
        self._shared_icon_sources = kwargs.get("icon_sources")
        self.icon_sources = []

        # Context menu toggle (loaded from menus.xml)
        self._shared_show_context_menu = kwargs.get("show_context_menu")
        self.show_context_menu = True

        # Sub-dialog definitions (loaded from menus.xml)
        self._shared_subdialogs = kwargs.get("subdialogs")
        self._subdialogs = {}

        # Dialog mode for sub-dialogs (e.g., "widget1", "widget2")
        # When set, Window.Property(skinshortcuts-dialog) is set to this value
        self.dialog_mode = kwargs.get("dialog_mode", "")

        # Property suffix for widget slots (e.g., ".2" for widget 2)
        # When set, all property reads/writes are automatically suffixed
        self.property_suffix = kwargs.get("property_suffix", "")

        # Control ID to focus when dialog opens (for sub-dialogs)
        self._setfocus = kwargs.get("setfocus")

        # Selected item index to restore in child dialog
        self._selected_index = kwargs.get("selected_index")

        # Track if we're a child dialog (spawned from parent)
        self.is_child = self._shared_manager is not None

        # Store dialog XML path for spawning children
        self._dialog_xml = args[0] if args else "script-skinshortcuts.xml"
        self._skin_path = args[1] if len(args) > 1 else ""

        # Track if changes were saved (for return value)
        self.changes_saved = False

    def _suffixed_name(self, name: str) -> str:
        """Apply property suffix to a property name.

        Widget properties are stored with suffix (e.g., widgetArt.2) to allow
        multiple widget slots per menu item. This method applies the current
        dialog's suffix to property names.

        Args:
            name: Base property name (e.g., "widgetArt", "widgetStyle")

        Returns:
            Suffixed property name (e.g., "widgetArt.2") or original if no suffix
        """
        if self.property_suffix:
            return f"{name}{self.property_suffix}"
        return name

    def _get_item_property(self, item: MenuItem, name: str) -> str:
        """Get a property value with suffix applied.

        Args:
            item: The menu item to read from
            name: Base property name (suffix will be applied)

        Returns:
            Property value or empty string if not set
        """
        suffixed = self._suffixed_name(name)
        return item.properties.get(suffixed, "")

    def onInit(self):  # noqa: N802
        """Called when dialog is initialized.

        Note: In Kodi, onInit() is called every time the window regains focus,
        not just on first open. We must avoid recreating the manager to preserve
        unsaved changes.
        """
        self._log(f"onInit: shortcuts_path={self.shortcuts_path}, menu_id={self.menu_id}")

        # Use shared manager or create new one (only if we don't have one yet)
        if self.manager is None:
            if self._shared_manager:
                self.manager = self._shared_manager
            else:
                self.manager = MenuManager(self.shortcuts_path)
                # Clear content cache for root dialog to ensure fresh data
                # (e.g., newly added favourites are visible in the picker)
                clear_content_cache()

            # Log what was loaded (only on first init)
            menu_ids = self.manager.get_menu_ids()
            self._log(f"Loaded menus: {menu_ids}")

        # Use shared property schema or load from skin (only if we don't have one yet)
        if self.property_schema is None:
            if self._shared_schema:
                self.property_schema = self._shared_schema
            else:
                schema_path = Path(self.shortcuts_path) / "properties.xml"
                self.property_schema = load_properties(schema_path)

        # Use shared icon sources/context menu/subdialogs setting or load from menus.xml
        if not self.icon_sources:
            if self._shared_icon_sources is not None:
                self.icon_sources = self._shared_icon_sources
                self.show_context_menu = (
                    self._shared_show_context_menu
                    if self._shared_show_context_menu is not None
                    else True
                )
                # Build subdialogs lookup from shared list
                if self._shared_subdialogs:
                    self._subdialogs = {sd.button_id: sd for sd in self._shared_subdialogs}
            else:
                menus_path = Path(self.shortcuts_path) / "menus.xml"
                menu_config = load_menu_config(menus_path)
                self.icon_sources = menu_config.icon_sources
                self.show_context_menu = menu_config.show_context_menu
                # Build subdialogs lookup
                self._subdialogs = {sd.button_id: sd for sd in menu_config.subdialogs}

        # Set dialog mode and suffix properties on Home window
        home = xbmcgui.Window(10000)
        if not self.is_child:
            # Clear stale properties from previous session/crash
            home.clearProperty("skinshortcuts-dialog")
            home.clearProperty("skinshortcuts-suffix")
        if self.property_suffix:
            home.setProperty("skinshortcuts-suffix", self.property_suffix)
        if self.dialog_mode:
            home.setProperty("skinshortcuts-dialog", self.dialog_mode)

        self._load_items()
        self._log(f"Loaded {len(self.items)} items for menu '{self.menu_id}'")
        self._display_items()
        self._update_window_properties()

        # Set focus to specified control (for sub-dialogs)
        if self._setfocus:
            try:
                self.setFocusId(self._setfocus)
                self._log(f"Set focus to control {self._setfocus}")
            except RuntimeError:
                pass

    def _log(self, msg: str) -> None:
        """Log debug message."""
        if IN_KODI:
            xbmc.log(f"[skinshortcuts.dialog] {msg}", xbmc.LOGINFO)

    def _load_items(self) -> None:
        """Load menu items from manager."""
        if self.manager:
            self.items = self.manager.get_menu_items(self.menu_id)

            # For custom widget menus, add a default item if empty
            # This allows editing without pre-persisting to userdata
            if not self.items and self.dialog_mode.startswith("custom-"):
                default_item = MenuItem(
                    name=f"user-{self.menu_id[:8]}",
                    label="New Item",
                    icon="DefaultFolder.png",
                )
                self.items.append(default_item)
                self._log(f"Added default item to empty custom menu: {self.menu_id}")

    def _display_items(self) -> None:
        """Display items in the list control. Called once during onInit."""
        self._rebuild_list(focus_index=self._selected_index)
        # Populate subdialog list (212) if in subdialog mode
        if self.dialog_mode:
            self._populate_subdialog_list()

    def _populate_subdialog_list(self) -> None:
        """Populate Container 212 with current item for subdialog variable access.

        Container 212 is a single-item list used by widget settings controls
        to read properties without conflicting with the parent dialog's Container 211.
        """
        try:
            subdialog_list = self.getControl(CONTROL_SUBDIALOG_LIST)
        except RuntimeError:
            self._log("Container 212 not found in skin - subdialog list not populated")
            return

        subdialog_list.reset()

        # Get current selected item
        item = self._get_selected_item()
        if item:
            listitem = self._create_listitem(item)
            subdialog_list.addItem(listitem)
            subdialog_list.selectItem(0)
            self._log(f"Populated subdialog list (212) with item: {item.name}")

    def _clear_subdialog_list(self) -> None:
        """Clear Container 212 after subdialog closes."""
        try:
            subdialog_list = self.getControl(CONTROL_SUBDIALOG_LIST)
            subdialog_list.reset()
        except RuntimeError:
            pass

    def _rebuild_list(self, focus_index: int | None = None) -> None:
        """Rebuild the list control from self.items.

        Use this for structural changes (add/delete/move/reset).
        For property changes, use _refresh_selected_item() instead.
        """
        try:
            list_control = self.getControl(CONTROL_LIST)
        except RuntimeError:
            return

        list_control.reset()

        for item in self.items:
            listitem = self._create_listitem(item)
            list_control.addItem(listitem)

        if focus_index is not None and 0 <= focus_index < len(self.items):
            list_control.selectItem(focus_index)

    def _create_listitem(self, item: MenuItem) -> xbmcgui.ListItem:
        """Create a ListItem from a MenuItem."""
        display_label = resolve_label(item.label)
        listitem = xbmcgui.ListItem(label=display_label, offscreen=True)
        self._populate_listitem(listitem, item)
        return listitem

    def _populate_listitem(self, listitem: xbmcgui.ListItem, item: MenuItem) -> None:
        """Populate a ListItem with all properties from a MenuItem."""
        listitem.setLabel(resolve_label(item.label))
        listitem.setLabel2(item.action or "")
        listitem.setProperty("name", item.name)
        listitem.setProperty("path", item.action or "")
        listitem.setProperty("originalAction", item.original_action or item.action or "")
        listitem.setProperty("skinshortcuts-disabled", "True" if item.disabled else "False")

        if item.icon:
            listitem.setArt({"thumb": item.icon, "icon": item.icon})

        # Widget properties are stored directly in item.properties
        widget_name = item.properties.get("widget", "")
        if widget_name:
            listitem.setProperty("widget", widget_name)
            listitem.setProperty("widgetLabel", item.properties.get("widgetLabel", ""))
            listitem.setProperty("widgetPath", item.properties.get("widgetPath", ""))
            listitem.setProperty("widgetType", item.properties.get("widgetType", ""))
            listitem.setProperty("widgetTarget", item.properties.get("widgetTarget", ""))
        else:
            # Clear widget properties if no widget
            listitem.setProperty("widget", "")
            listitem.setProperty("widgetLabel", "")
            listitem.setProperty("widgetPath", "")
            listitem.setProperty("widgetType", "")
            listitem.setProperty("widgetTarget", "")

        # Background properties are stored directly in item.properties
        background_name = item.properties.get("background", "")
        if background_name:
            listitem.setProperty("background", background_name)
            listitem.setProperty("backgroundLabel", item.properties.get("backgroundLabel", ""))
            listitem.setProperty("backgroundPath", item.properties.get("backgroundPath", ""))
        else:
            # Clear background properties if no background
            listitem.setProperty("background", "")
            listitem.setProperty("backgroundLabel", "")
            listitem.setProperty("backgroundPath", "")

        # Add custom properties from schema with resolved names
        # Use effective properties (includes fallbacks) for display
        effective_props = self._get_effective_properties(item)
        for prop_name, prop_value in effective_props.items():
            # Skip built-in properties we already handle
            if prop_name in (
                "widget",
                "widgetPath",
                "widgetType",
                "widgetTarget",
                "widgetLabel",
                "background",
                "backgroundLabel",
                "backgroundPath",
                "name",
                "label",
            ):
                continue
            # Skip widget-related properties if no widget is set for that slot
            # (don't show fallback values for widgetStyle/widgetArt when widget is cleared)
            # Check suffix to determine which widget slot this property belongs to
            if prop_name.startswith("widget"):
                # Extract suffix (e.g., ".2" from "widgetStyle.2")
                if "." in prop_name:
                    suffix = "." + prop_name.split(".", 1)[-1]
                    slot_widget = item.properties.get(f"widget{suffix}", "")
                else:
                    slot_widget = widget_name
                if not slot_widget:
                    listitem.setProperty(prop_name, "")
                    listitem.setProperty(f"{prop_name}Label", "")
                    continue
            listitem.setProperty(prop_name, prop_value)
            # Look up the resolved label for this value from schema
            resolved_label = self._get_property_label(prop_name, prop_value)
            if resolved_label:
                listitem.setProperty(f"{prop_name}Label", resolved_label)

        # Check if item has a submenu with actual items
        if self.manager:
            submenu_name = item.submenu or item.name
            submenu = self.manager.config.get_menu(submenu_name)
            if submenu and submenu.items:
                listitem.setProperty("hasSubmenu", "true")
                listitem.setProperty("submenu", submenu_name)

            # Check if item can be reset (exists in defaults and has been modified)
            is_modified = False
            if self.manager:
                is_modified = self.manager.is_item_modified(self.menu_id, item.name)
            listitem.setProperty("isResettable", "true" if is_modified else "")

    def _get_selected_listitem(self) -> xbmcgui.ListItem | None:
        """Get the currently selected ListItem from the control."""
        try:
            list_control = self.getControl(CONTROL_LIST)
            return list_control.getSelectedItem()
        except RuntimeError:
            return None

    def _refresh_selected_item(self) -> None:
        """Refresh the selected item's ListItem from our local item state.

        Call this after making changes to sync the UI with item state.
        """
        index = self._get_selected_index()
        if index < 0 or index >= len(self.items):
            return

        # Get the existing ListItem and update its properties in place
        listitem = self._get_selected_listitem()
        if listitem:
            self._populate_listitem(listitem, self.items[index])

        # Also refresh subdialog list (212) if in subdialog mode
        if self.dialog_mode:
            self._populate_subdialog_list()

    def _get_selected_index(self) -> int:
        """Get the currently selected list index."""
        try:
            list_control = self.getControl(CONTROL_LIST)
            return list_control.getSelectedPosition()
        except RuntimeError:
            return -1

    def _get_selected_item(self) -> MenuItem | None:
        """Get the currently selected MenuItem."""
        index = self._get_selected_index()
        if 0 <= index < len(self.items):
            return self.items[index]
        return None

    def _get_item_properties(self, item: MenuItem) -> dict[str, str]:
        """Get all properties of an item as a dict for condition evaluation.

        All properties including widget and background are stored in item.properties.
        """
        props = dict(item.properties)  # All properties are in item.properties

        # Add item identifiers
        props["name"] = item.name
        props["label"] = item.label

        return props

    def _get_effective_properties(self, item: MenuItem) -> dict[str, str]:
        """Get item properties with fallbacks applied.

        Returns a dict of property name -> effective value, including
        fallback values for properties that aren't explicitly set.
        """
        # Start with base properties
        props = self._get_item_properties(item)

        # Apply fallbacks from property schema
        if not self.property_schema:
            return props

        for prop_name, fallback in self.property_schema.fallbacks.items():
            # Skip if property is already set
            if prop_name in props and props[prop_name]:
                continue

            # Evaluate fallback rules in order
            for rule in fallback.rules:
                if not rule.condition or evaluate_condition(rule.condition, props):
                    props[prop_name] = rule.value
                    break

        return props

    def _get_property_label(self, prop_name: str, prop_value: str) -> str | None:
        """Get the resolved display label for a property value.

        Looks up the property in the schema, finds the matching option,
        and returns its resolved label.

        Args:
            prop_name: The property name (e.g., "widgetStyle")
            prop_value: The property value (e.g., "Panel")

        Returns:
            The resolved label, or None if not found
        """
        if not self.property_schema:
            return None

        prop = self.property_schema.get_property(prop_name)
        if not prop:
            return None

        # Find option with matching value
        for opt in prop.options:
            if opt.value == prop_value:
                return resolve_label(opt.label)

        return None

    def _update_deleted_property(self) -> None:
        """Update window property to indicate if deleted items exist for current menu."""
        has_deleted = self.manager.has_removed_items(self.menu_id) if self.manager else False
        self.setProperty("skinshortcuts-hasdeleted", "true" if has_deleted else "")

    def _update_window_properties(self) -> None:
        """Update window properties for skin to show current context."""
        try:
            # V2 compatibility: groupname is the menu ID
            self.setProperty("groupname", self.menu_id)

            # Get menu's allow config
            if self.manager:
                menu = self.manager.config.get_menu(self.menu_id)
                if menu:
                    allow = menu.allow
                    self.setProperty("allowWidgets", "true" if allow.widgets else "false")
                    self.setProperty("allowBackgrounds", "true" if allow.backgrounds else "false")
                    self.setProperty("allowSubmenus", "true" if allow.submenus else "false")

            # Update deleted items property
            self._update_deleted_property()

        except RuntimeError:
            pass

    def onClick(self, control_id: int):  # noqa: N802
        """Handle control clicks - routes to appropriate handler."""
        if not self.manager:
            return

        if control_id == CONTROL_ADD:
            self._add_item()
        elif control_id == CONTROL_DELETE:
            self._delete_item()
        elif control_id == CONTROL_MOVE_UP:
            self._move_item(-1)
        elif control_id == CONTROL_MOVE_DOWN:
            self._move_item(1)
        elif control_id == CONTROL_SET_LABEL:
            self._set_label()
        elif control_id == CONTROL_SET_ICON:
            self._set_icon()
        elif control_id == CONTROL_SET_ACTION:
            self._set_action()
        elif control_id == CONTROL_TOGGLE_DISABLED:
            self._toggle_disabled()
        elif control_id == CONTROL_CHOOSE_SHORTCUT:
            self._choose_shortcut()
        elif control_id == CONTROL_RESTORE_DELETED:
            self._restore_deleted_item()
        elif control_id == CONTROL_RESET_ITEM:
            self._reset_current_item()
        elif control_id == CONTROL_EDIT_SUBMENU:
            self._edit_submenu()
        elif control_id in self._subdialogs:
            # Spawn sub-dialog for this button
            self._spawn_subdialog(self._subdialogs[control_id])
        else:
            # Try to handle as a property button from schema
            self._handle_property_button(control_id)

    def onAction(self, action):  # noqa: N802
        """Handle actions."""
        action_id = action.getId()
        if action_id in ACTION_CANCEL:
            self.close()
        elif action_id in ACTION_CONTEXT and self.show_context_menu:
            self._show_context_menu()

    def close(self) -> None:
        """Save changes and close dialog.

        Note: Home properties (skinshortcuts-dialog/suffix) are cleared by
        the parent after doModal() returns, not here.
        """
        if not self.is_child and self.manager and self.manager.has_changes():
            self.manager.save()
            self.changes_saved = True
        xbmcgui.WindowXMLDialog.close(self)

    # Abstract methods that must be implemented by other mixins
    def _add_item(self) -> None:
        """Add a new item - implemented by ItemsMixin."""
        raise NotImplementedError

    def _delete_item(self) -> None:
        """Delete selected item - implemented by ItemsMixin."""
        raise NotImplementedError

    def _move_item(self, direction: int) -> None:
        """Move item up/down - implemented by ItemsMixin."""
        raise NotImplementedError

    def _set_label(self) -> None:
        """Change item label - implemented by ItemsMixin."""
        raise NotImplementedError

    def _set_icon(self) -> None:
        """Change item icon - implemented by ItemsMixin."""
        raise NotImplementedError

    def _set_action(self) -> None:
        """Change item action - implemented by ItemsMixin."""
        raise NotImplementedError

    def _toggle_disabled(self) -> None:
        """Toggle disabled state - implemented by ItemsMixin."""
        raise NotImplementedError

    def _restore_deleted_item(self) -> None:
        """Restore deleted item - implemented by ItemsMixin."""
        raise NotImplementedError

    def _reset_current_item(self) -> None:
        """Reset item to defaults - implemented by ItemsMixin."""
        raise NotImplementedError

    def _choose_shortcut(self) -> None:
        """Choose shortcut from groupings - implemented by PickersMixin."""
        raise NotImplementedError

    def _handle_property_button(self, button_id: int) -> bool:
        """Handle property button - implemented by PropertiesMixin."""
        raise NotImplementedError

    def _edit_submenu(self) -> None:
        """Edit submenu - implemented by SubdialogsMixin."""
        raise NotImplementedError

    def _spawn_subdialog(self, subdialog: SubDialog) -> None:
        """Spawn subdialog - implemented by SubdialogsMixin."""
        raise NotImplementedError

    def _show_context_menu(self) -> None:
        """Show context menu - implemented by ItemsMixin."""
        raise NotImplementedError
