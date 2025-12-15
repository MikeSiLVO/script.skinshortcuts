"""Property management mixin - widget, background, toggle, options properties."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Literal

try:
    import xbmcgui

    IN_KODI = True
except ImportError:
    IN_KODI = False

from ..loaders import evaluate_condition, load_widgets
from ..localize import resolve_label
from ..models import (
    Background,
    BackgroundType,
    MenuItem,
    PlaylistSource,
    Widget,
    WidgetGroup,
)
from ..providers import scan_playlist_files

if TYPE_CHECKING:
    from ..manager import MenuManager
    from ..models import PropertySchema


class PropertiesMixin:
    """Mixin providing property management - widget, background, toggle, options.

    This mixin implements:
    - Property button handling from schema
    - Widget property setting/clearing
    - Background property setting/clearing
    - Toggle property handling
    - Options list property handling
    - Playlist picker

    Requires DialogBaseMixin and PickersMixin to be mixed in first.
    """

    # Type hints for mixin - actual values come from base/subclass
    menu_id: str
    shortcuts_path: str
    manager: MenuManager | None
    property_schema: PropertySchema | None
    property_suffix: str

    if TYPE_CHECKING:
        # Methods from DialogBaseMixin - only for type checking
        def _get_selected_item(self) -> MenuItem | None: ...
        def _get_item_properties(self, item: MenuItem) -> dict[str, str]: ...
        def _get_item_property(self, item: MenuItem, name: str) -> str: ...
        def _refresh_selected_item(self) -> None: ...
        def _log(self, msg: str) -> None: ...

        # Methods from ItemsMixin
        def _set_item_property(
            self,
            item: MenuItem,
            name: str,
            value: str | None,
            related: dict[str, str | None] | None = None,
            apply_suffix: bool = True,
        ) -> None: ...

        def _browse_with_sources(
            self,
            sources: list,
            title: str,
            browse_type: int,
            mask: str = "",
            item_properties: dict[str, str] | None = None,
        ) -> str | None: ...

        # Methods from PickersMixin
        def _pick_widget_from_groups(
            self,
            items: list[WidgetGroup | Widget],
            item_props: dict[str, str],
            slot: str = "",
            show_get_more: bool = True,
        ) -> Widget | None | Literal[False]: ...

        def _pick_widget_flat(
            self, widgets: list, item_props: dict[str, str] | None = None, slot: str = ""
        ) -> Widget | None | Literal[False]: ...

        def _nested_picker(
            self,
            title: str,
            items: list[tuple[str, str, str]],
            on_select,
            show_none: bool = True,
            current_value: str = "",
        ): ...

        def _pick_background(
            self, item_props: dict[str, str], current_value: str = ""
        ) -> Background | None | Literal[False]: ...

    def _handle_property_button(self, button_id: int) -> bool:
        """Handle a property button click from the schema.

        Args:
            button_id: The control button ID that was clicked

        Returns:
            True if handled, False if not a property button
        """
        if not self.property_schema or not self.manager:
            return False

        # Look up property and button mapping
        # Always gets base property - suffix is applied at runtime
        prop, button = self.property_schema.get_property_for_button(button_id)
        if not button:
            return False

        item = self._get_selected_item()
        if not item:
            return False

        # Check if requires property is set (button.requires takes precedence)
        # Apply suffix to requires if button is suffix-aware
        requires = button.requires or (prop.requires if prop else "")
        if requires:
            requires_name = requires
            if button.suffix and self.property_suffix:
                requires_name = f"{requires}{self.property_suffix}"
            # Access directly since requires_name already has suffix applied
            required_value = item.properties.get(requires_name, "")
            if not required_value:
                xbmcgui.Dialog().notification(
                    "Not Available",
                    f"Requires {requires_name} to be set first",
                )
                return True

        # Determine effective property name (apply suffix if button is suffix-aware)
        prop_name = prop.name if prop else button.property_name
        if button.suffix and self.property_suffix:
            prop_name = f"{prop_name}{self.property_suffix}"

        # Get type from button first, fall back to property
        prop_type = button.type or (prop.type if prop else "")

        # Handle type="widget" - show widget picker and auto-populate
        if prop_type == "widget":
            self._handle_widget_property(prop, item, prop_name)
            return True

        # Handle type="background" - show background picker and auto-populate
        if prop_type == "background":
            self._handle_background_property(prop, item, prop_name)
            return True

        # Handle type="toggle" - toggle between True and empty
        if prop_type == "toggle":
            self._handle_toggle_property(prop, item, button, prop_name)
            return True

        # Regular property - show options list
        return self._handle_options_property(prop, item, button, prop_name)

    def _handle_widget_property(self, prop, item: MenuItem, prop_name: str) -> None:
        """Handle a widget-type property.

        Shows widget picker and auto-populates related properties:
        - {prefix}Name, {prefix}Path, {prefix}Type, {prefix}Target

        For custom widgets, the user selects "Custom list" which sets widgetType=custom.
        When the subdialog closes, the onclose action checks this condition and opens
        the custom widget menu editor automatically.

        Args:
            prop: The property schema
            item: The menu item
            prop_name: Effective property name (may include suffix like "widget.2")
        """
        if self.manager is None:
            return
        # Check if widgets are allowed
        menu = self.manager.config.get_menu(self.menu_id)
        if menu and not menu.allow.widgets:
            xbmcgui.Dialog().notification("Not Allowed", "Widgets not enabled for this menu")
            return

        # Use prop_name as prefix (includes suffix if applicable)
        prefix = prop_name
        slot = prefix  # Slot is the same as prefix for filtering custom widgets

        # Load widget configuration
        widgets_path = Path(self.shortcuts_path) / "widgets.xml"
        widget_config = load_widgets(widgets_path)

        item_props = self._get_item_properties(item)
        result = None

        if widget_config.groupings:
            result = self._pick_widget_from_groups(
                widget_config.groupings, item_props, slot, widget_config.show_get_more
            )
        else:
            # Fall back to flat widget list
            widgets = self.manager.get_widgets()
            if not widgets:
                xbmcgui.Dialog().notification("No Widgets", "No widgets defined in skin")
                return
            result = self._pick_widget_flat(widgets, item_props, slot)

        if result is None:
            return  # Cancelled

        if result is False:
            # User explicitly chose "None" - clear all widget properties
            self._clear_widget_properties(item, prefix)
        else:
            # Widget selected - set all related properties
            self._log(f"Widget selected: {result.name}")
            self._set_widget_properties(item, prefix, result)

        self._refresh_selected_item()

    def _set_widget_properties(self, item: MenuItem, prefix: str, widget: Widget) -> None:
        """Set widget properties on item with auto-populated values.

        Args:
            item: The menu item
            prefix: Property name prefix (e.g., "widget" or "widget.2")
            widget: The Widget object
        """
        self._log(f"Setting widget properties for {prefix}: {widget.name}")

        # Parse prefix: "widget" -> ("widget", ""), "widget.2" -> ("widget", ".2")
        if "." in prefix:
            base, suffix = prefix.rsplit(".", 1)
            suffix = f".{suffix}"
        else:
            base = prefix
            suffix = ""

        # Substitute {menuitem} placeholder in widget path with item name
        widget_path = widget.path.replace("{menuitem}", item.name)

        # Build related properties dict
        related: dict[str, str | None] = {
            f"{base}Label{suffix}": resolve_label(widget.label),
            f"{base}Path{suffix}": widget_path,
            f"{base}Type{suffix}": widget.type or "",
            f"{base}Target{suffix}": widget.target or "",
        }

        # apply_suffix=False because suffix is already included in prefix and related names
        self._set_item_property(item, prefix, widget.name, related, apply_suffix=False)

    def _clear_widget_properties(self, item: MenuItem, prefix: str) -> None:
        """Clear all widget properties for a prefix."""
        self._log(f"Clearing widget properties for {prefix}")

        # Parse prefix: "widget" -> ("widget", ""), "widget.2" -> ("widget", ".2")
        if "." in prefix:
            base, suffix = prefix.rsplit(".", 1)
            suffix = f".{suffix}"
        else:
            base = prefix
            suffix = ""

        # Build related properties dict with None to clear
        related: dict[str, str | None] = {
            f"{base}Label{suffix}": None,
            f"{base}Path{suffix}": None,
            f"{base}Type{suffix}": None,
            f"{base}Target{suffix}": None,
        }

        # apply_suffix=False because suffix is already included in prefix and related names
        self._set_item_property(item, prefix, "", related, apply_suffix=False)

    def _handle_background_property(self, prop, item: MenuItem, prop_name: str) -> None:
        """Handle a background-type property.

        Shows background picker and auto-populates related properties:
        - {prefix}Name, {prefix}Path

        For type="browse" backgrounds, opens single image browser.
        For type="multi" backgrounds, opens folder browser.

        Args:
            prop: The property schema
            item: The menu item
            prop_name: Effective property name (may include suffix)
        """
        if self.manager is None:
            return
        # Check if backgrounds are allowed
        menu = self.manager.config.get_menu(self.menu_id)
        if menu and not menu.allow.backgrounds:
            xbmcgui.Dialog().notification("Not Allowed", "Backgrounds not enabled for this menu")
            return

        # Use prop_name as prefix (includes suffix if applicable)
        prefix = prop_name

        # Get current background and item properties for picker
        current_bg = self._get_item_property(item, prefix)
        item_props = self._get_item_properties(item)

        # Use hierarchical picker with back navigation
        while True:
            bg = self._pick_background(item_props, current_value=current_bg)

            if bg is None:
                return  # Cancelled completely
            if bg is False:
                # User chose "None"
                self._clear_background_properties(item, prefix)
                self._refresh_selected_item()
                return

            # Handle types that need sub-dialog
            if bg.type == BackgroundType.BROWSE:
                path = self._browse_with_sources(
                    sources=bg.browse_sources,
                    title=resolve_label(bg.label),
                    browse_type=2,  # Image file
                    mask=".jpg|.png|.gif",
                    item_properties=item.properties,
                )
                if path:
                    self._set_background_properties_custom(item, prefix, bg, path)
                    self._refresh_selected_item()
                    return
                # Cancelled browse - loop back to picker
                continue

            if bg.type == BackgroundType.MULTI:
                path = self._browse_with_sources(
                    sources=bg.browse_sources,
                    title=resolve_label(bg.label),
                    browse_type=0,  # Folder
                    item_properties=item.properties,
                )
                if path:
                    self._set_background_properties_custom(item, prefix, bg, path)
                    self._refresh_selected_item()
                    return
                # Cancelled browse - loop back to picker
                continue

            if bg.type in (BackgroundType.PLAYLIST, BackgroundType.LIVE_PLAYLIST) and not bg.path:
                current_playlist = self._get_item_property(item, f"{prefix}Path")
                result = self._pick_playlist(
                    bg.sources, bg.label if bg.sources else "", current_playlist
                )
                if result:
                    path, display_label = result
                    self._set_background_properties_custom(item, prefix, bg, path, display_label)
                    self._refresh_selected_item()
                    return
                # Cancelled playlist picker - loop back to picker
                continue

            # Regular background with predefined path
            self._set_background_properties(item, prefix, bg)
            self._refresh_selected_item()
            return

    def _set_background_properties(self, item: MenuItem, prefix: str, bg) -> None:
        """Set background properties on item with auto-populated values."""
        self._log(f"Setting background properties for {prefix}: {bg.name}")

        related: dict[str, str | None] = {
            f"{prefix}Label": resolve_label(bg.label),
            f"{prefix}Path": bg.path,
        }

        # apply_suffix=False because suffix is already included in prefix
        self._set_item_property(item, prefix, bg.name, related, apply_suffix=False)

    def _set_background_properties_custom(
        self, item: MenuItem, prefix: str, bg, custom_path: str, custom_label: str | None = None
    ) -> None:
        """Set background properties with a user-browsed custom path.

        Used for type="browse" (single image), type="multi" (folder),
        and type="playlist" backgrounds.

        Args:
            item: The menu item
            prefix: Property name prefix
            bg: The Background object
            custom_path: User-selected path
            custom_label: Optional custom label (e.g., "Live Background: Random Movies")
        """
        self._log(f"Setting custom background for {prefix}: {bg.name} -> {custom_path}")

        # Use custom label if provided (e.g., prefixed playlist name), otherwise bg.label
        label = custom_label if custom_label else resolve_label(bg.label)

        related: dict[str, str | None] = {
            f"{prefix}Label": label,
            f"{prefix}Path": custom_path,
        }

        # apply_suffix=False because suffix is already included in prefix
        self._set_item_property(item, prefix, bg.name, related, apply_suffix=False)

    def _clear_background_properties(self, item: MenuItem, prefix: str) -> None:
        """Clear all background properties for a prefix."""
        self._log(f"Clearing background properties for {prefix}")

        related: dict[str, str | None] = {
            f"{prefix}Name": None,
            f"{prefix}Path": None,
        }

        # apply_suffix=False because suffix is already included in prefix
        self._set_item_property(item, prefix, "", related, apply_suffix=False)

    def _pick_playlist(
        self,
        sources: list | None = None,
        label_prefix: str = "",
        current_path: str = "",
    ) -> tuple[str, str] | None:
        """Show picker for available playlists.

        Args:
            sources: List of PlaylistSource objects defining where to scan.
                     If None/empty, uses default user playlist locations.
            label_prefix: Prefix to show on all playlist labels (e.g., "Live Background")
            current_path: Current playlist path to preselect

        Returns:
            Tuple of (path, display_label) or None if cancelled.
            display_label includes the prefix if provided.
        """
        # Default sources if none provided
        if not sources:
            sources = [
                PlaylistSource(
                    label="Video Playlists",
                    path="special://videoplaylists/",
                    icon="DefaultVideoPlaylists.png",
                ),
                PlaylistSource(
                    label="Music Playlists",
                    path="special://musicplaylists/",
                    icon="DefaultMusicPlaylists.png",
                ),
            ]

        # Resolve prefix
        prefix = resolve_label(label_prefix) if label_prefix else ""

        # Scan each source for playlists
        # playlists: list of (display_label, path, icon)
        playlists = []
        preselect = -1
        for source in sources:
            source_playlists = scan_playlist_files(source.path)
            for raw_label, path in source_playlists:
                # Apply prefix to label
                if prefix:
                    display_label = f"{prefix}: {raw_label}"
                else:
                    display_label = raw_label
                # Check for preselect
                if preselect == -1 and path == current_path:
                    preselect = len(playlists)
                playlists.append((display_label, path, source.icon))

        if not playlists:
            xbmcgui.Dialog().notification("No Playlists", "No playlists found")
            return None

        # Build selection list
        listitems = []
        for label, _path, icon in playlists:
            listitem = xbmcgui.ListItem(label)
            listitem.setArt({"icon": icon})
            listitems.append(listitem)

        title = f"Select {prefix}" if prefix else "Select Playlist"
        selected = xbmcgui.Dialog().select(
            title, listitems, useDetails=True, preselect=preselect
        )

        if selected == -1:
            return None

        return (playlists[selected][1], playlists[selected][0])

    def _handle_toggle_property(
        self, prop, item: MenuItem, button, prop_name: str
    ) -> None:
        """Handle a toggle-type property.

        Toggles between "True" and empty (cleared).

        Args:
            prop: The property schema
            item: The menu item
            button: The button mapping
            prop_name: Effective property name (may include suffix)
        """
        # Access directly since prop_name already has suffix applied
        current_value = item.properties.get(prop_name, "")
        if current_value:
            # Currently set, clear it
            self._log(f"Toggling {prop_name} OFF for item {item.name}")
            self._set_item_property(item, prop_name, None, apply_suffix=False)
        else:
            # Currently empty, set to True
            self._log(f"Toggling {prop_name} ON for item {item.name}")
            self._set_item_property(item, prop_name, "True", apply_suffix=False)

        self._refresh_selected_item()

    def _handle_options_property(
        self, prop, item: MenuItem, button, prop_name: str
    ) -> bool:
        """Handle a regular property with options list.

        Args:
            prop: The property schema
            item: The menu item
            button: The button mapping
            prop_name: Effective property name (may include suffix)
        """
        # Get item properties for condition evaluation
        item_props = self._get_item_properties(item)

        # Filter options by conditions
        visible_options = []
        for opt in prop.options:
            if not opt.condition or evaluate_condition(opt.condition, item_props):
                visible_options.append(opt)

        if not visible_options:
            xbmcgui.Dialog().notification("No Options", "No options available")
            return True

        # Build selection list with icons
        listitems = []
        if button.show_none:
            none_item = xbmcgui.ListItem("None")
            none_item.setArt({"icon": "DefaultAddonNone.png"})
            listitems.append(none_item)

        for opt in visible_options:
            listitem = xbmcgui.ListItem(resolve_label(opt.label))
            # Try to get contextual icon from option
            icon = "DefaultAddonNone.png"
            if opt.icons:
                # Find matching icon based on current properties
                for icon_variant in opt.icons:
                    cond = icon_variant.condition
                    if not cond or evaluate_condition(cond, item_props):
                        icon = icon_variant.path
                        break
            listitem.setArt({"icon": icon})
            listitems.append(listitem)

        # Get title from button or fall back to property name
        title = resolve_label(button.title) if button.title else prop_name

        # Find current selection for preselect
        # prop_name already has suffix, access item.properties directly
        current_value = item.properties.get(prop_name, "")
        preselect = -1
        offset = 1 if button.show_none else 0
        for i, opt in enumerate(visible_options):
            if opt.value == current_value:
                preselect = i + offset
                break

        selected = xbmcgui.Dialog().select(
            title, listitems, useDetails=button.show_icons, preselect=preselect
        )

        if selected == -1:
            return True

        # Handle selection - apply_suffix=False since prop_name already has suffix
        if button.show_none and selected == 0:
            # Clear the property
            self._log(f"Clearing property {prop_name} on item {item.name}")
            self._set_item_property(item, prop_name, None, apply_suffix=False)
        else:
            offset = 1 if button.show_none else 0
            value = visible_options[selected - offset].value
            self._log(f"Setting property {prop_name}={value} on item {item.name}")
            self._set_item_property(item, prop_name, value, apply_suffix=False)

        if self.manager:
            self._log(f"has_changes after property set: {self.manager.has_changes()}")
        self._refresh_selected_item()
        return True
