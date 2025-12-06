"""Menu manager for dialog operations."""

from __future__ import annotations

import copy
import uuid
from pathlib import Path

from .config import SkinConfig
from .models import Action, Menu, MenuItem
from .userdata import (
    MenuItemOverride,
    MenuOverride,
    UserData,
    _check_dialog_visible,
    save_userdata,
)


class MenuManager:
    """Manages menu operations with working copy and diff-based save.

    Architecture:
    - defaults: Immutable skin defaults (from config.default_menus)
    - working: Mutable working copy (all edits happen here)
    - Save diffs working against defaults to generate minimal userdata
    """

    def __init__(self, shortcuts_path: str | Path, userdata_path: str | None = None):
        """Initialize manager.

        Args:
            shortcuts_path: Path to skin's shortcuts folder
            userdata_path: Optional path to userdata file (for testing)
        """
        self.shortcuts_path = Path(shortcuts_path)
        self.userdata_path = userdata_path

        # Load config with user customizations
        self.config = SkinConfig.load(shortcuts_path, load_user=True, userdata_path=userdata_path)

        # Working copy: deep copy of merged menus (defaults + userdata)
        # All edits happen here, diffed against defaults on save
        self.working: dict[str, Menu] = {
            menu.name: copy.deepcopy(menu) for menu in self.config.menus
        }

        self._changed = False

    def get_menu_ids(self) -> list[str]:
        """Get all available menu names."""
        return [menu.name for menu in self.config.menus]

    def get_all_menus(self) -> list[Menu]:
        """Get all menus from working copy.

        Returns:
            List of Menu objects ready for building includes
        """
        return list(self.working.values())

    def get_menu_items(self, menu_id: str) -> list[MenuItem]:
        """Get items for a menu from working copy."""
        if menu_id in self.working:
            return self.working[menu_id].items
        return []

    def get_widgets(self) -> list[tuple[str, str]]:
        """Get available widgets as (name, label) tuples."""
        return [(w.name, w.label) for w in self.config.widgets]

    def get_backgrounds(self) -> list[tuple[str, str]]:
        """Get available backgrounds as (name, label) tuples."""
        return [(b.name, b.label) for b in self.config.backgrounds]

    def _get_working_item(self, menu_id: str, item_name: str) -> MenuItem | None:
        """Get item from working copy."""
        if menu_id in self.working:
            for item in self.working[menu_id].items:
                if item.name == item_name:
                    return item
        return None

    def _ensure_working_menu(self, menu_id: str) -> Menu:
        """Ensure menu exists in working copy, create if needed."""
        if menu_id not in self.working:
            self.working[menu_id] = Menu(name=menu_id, is_submenu=True)
        return self.working[menu_id]

    def add_item(self, menu_id: str, after_index: int | None = None, label: str = "") -> MenuItem:
        """Add a new item to a menu.

        Args:
            menu_id: Menu to add item to
            after_index: Insert after this index (None = append)
            label: Initial label for the item

        Returns:
            The newly created MenuItem
        """
        # Generate unique name for user-added items
        item_name = f"user-{uuid.uuid4().hex[:8]}"

        # Create new item
        new_item = MenuItem(
            name=item_name,
            label=label or "New Item",
            actions=[Action(action="noop")],
        )

        # Add to working copy
        menu = self._ensure_working_menu(menu_id)
        if after_index is not None and 0 <= after_index < len(menu.items):
            menu.items.insert(after_index + 1, new_item)
        else:
            menu.items.append(new_item)

        self._changed = True
        return new_item

    def remove_item(self, menu_id: str, item_id: str) -> bool:
        """Remove an item from a menu.

        Args:
            menu_id: Menu containing the item
            item_id: ID of item to remove

        Returns:
            True if item was removed
        """
        if menu_id not in self.working:
            return False

        menu = self.working[menu_id]
        for i, item in enumerate(menu.items):
            if item.name == item_id:
                menu.items.pop(i)
                self._changed = True
                return True

        return False

    def restore_item(self, menu_id: str, item: MenuItem) -> bool:
        """Restore a previously deleted item.

        Args:
            menu_id: Menu to restore item to
            item: The MenuItem to restore (will be deep copied)

        Returns:
            True if item was restored
        """
        menu = self._ensure_working_menu(menu_id)

        # Deep copy to avoid sharing references
        restored = copy.deepcopy(item)
        menu.items.append(restored)
        self._changed = True
        return True

    def reset_item(self, menu_id: str, item_id: str) -> bool:
        """Reset an item to its skin default values.

        Args:
            menu_id: Menu containing the item
            item_id: ID of item to reset

        Returns:
            True if item was reset
        """
        # Get the default item
        default_menu = self.config.get_default_menu(menu_id)
        if not default_menu:
            return False

        default_item = None
        for item in default_menu.items:
            if item.name == item_id:
                default_item = item
                break

        if not default_item:
            return False

        # Find and replace in working copy
        if menu_id not in self.working:
            return False

        for i, item in enumerate(self.working[menu_id].items):
            if item.name == item_id:
                self.working[menu_id].items[i] = copy.deepcopy(default_item)
                self._changed = True
                return True

        return False

    def is_item_modified(self, menu_id: str, item_id: str) -> bool:
        """Check if an item differs from its skin default.

        Args:
            menu_id: Menu containing the item
            item_id: ID of item to check

        Returns:
            True if item is modified from defaults
        """
        working_item = self._get_working_item(menu_id, item_id)
        if not working_item:
            return False

        default_menu = self.config.get_default_menu(menu_id)
        if not default_menu:
            # No defaults means it's a user-created item
            return False

        default_item = None
        for item in default_menu.items:
            if item.name == item_id:
                default_item = item
                break

        if not default_item:
            # Item doesn't exist in defaults (user-added)
            return False

        # Compare key properties
        if working_item.label != default_item.label:
            return True
        if working_item.actions != default_item.actions:
            return True
        if working_item.icon != default_item.icon:
            return True
        if working_item.disabled != default_item.disabled:
            return True

        return working_item.properties != default_item.properties

    def get_removed_items(self, menu_id: str) -> list[MenuItem]:
        """Get default items that have been removed from working copy.

        Args:
            menu_id: Menu to check

        Returns:
            List of MenuItems that can be restored
        """
        default_menu = self.config.get_default_menu(menu_id)
        if not default_menu:
            return []

        working_menu = self.working.get(menu_id)
        if not working_menu:
            return list(default_menu.items)

        working_names = {item.name for item in working_menu.items}
        return [item for item in default_menu.items if item.name not in working_names]

    def has_removed_items(self, menu_id: str) -> bool:
        """Check if menu has removed items that can be restored."""
        return bool(self.get_removed_items(menu_id))

    def move_item(self, menu_id: str, item_id: str, direction: int) -> bool:
        """Move an item up or down in the menu.

        Args:
            menu_id: Menu containing the item
            item_id: ID of item to move
            direction: -1 for up, 1 for down

        Returns:
            True if item was moved
        """
        if menu_id not in self.working:
            return False

        items = self.working[menu_id].items
        if not items:
            return False

        # Find current index
        current_index = None
        for i, item in enumerate(items):
            if item.name == item_id:
                current_index = i
                break

        if current_index is None:
            return False

        new_index = current_index + direction
        if new_index < 0 or new_index >= len(items):
            return False

        # Swap items in working copy
        items[current_index], items[new_index] = items[new_index], items[current_index]

        self._changed = True
        return True

    def set_label(self, menu_id: str, item_id: str, label: str) -> bool:
        """Set the label for an item."""
        return self._set_item_property(menu_id, item_id, "label", label)

    def set_action(self, menu_id: str, item_id: str, action: str | list[str]) -> bool:
        """Set the action(s) for an item.

        Args:
            menu_id: Menu containing the item
            item_id: ID of item to update
            action: Single action string or list of actions
        """
        if isinstance(action, str):
            actions = [action]
        else:
            actions = action
        return self._set_item_property(menu_id, item_id, "actions", actions)

    def set_icon(self, menu_id: str, item_id: str, icon: str) -> bool:
        """Set the icon for an item."""
        return self._set_item_property(menu_id, item_id, "icon", icon)

    def set_widget(self, menu_id: str, item_id: str, widget: str | None) -> bool:
        """Set the widget for an item.

        Widget is stored as a property in the properties dict.
        """
        return self.set_custom_property(menu_id, item_id, "widget", widget)

    def set_background(self, menu_id: str, item_id: str, background: str | None) -> bool:
        """Set the background for an item.

        Background is stored as a property in the properties dict.
        """
        return self.set_custom_property(menu_id, item_id, "background", background)

    def set_disabled(self, menu_id: str, item_id: str, disabled: bool) -> bool:
        """Set the disabled state for an item."""
        return self._set_item_property(menu_id, item_id, "disabled", disabled)

    def set_custom_property(
        self, menu_id: str, item_id: str, prop_name: str, value: str | None
    ) -> bool:
        """Set a custom property on an item (stored in properties dict)."""
        item = self._get_working_item(menu_id, item_id)
        if not item:
            return False

        if value:
            item.properties[prop_name] = value
        elif prop_name in item.properties:
            del item.properties[prop_name]

        self._changed = True
        return True

    def _set_item_property(
        self, menu_id: str, item_id: str, prop: str, value: str | bool | list[str] | None
    ) -> bool:
        """Set a property on an item in working copy."""
        item = self._get_working_item(menu_id, item_id)
        if not item:
            return False

        if prop == "actions" and isinstance(value, list):
            # Convert action strings to Action objects
            item.actions = [Action(action=a) for a in value]
        else:
            setattr(item, prop, value)

        self._changed = True
        return True

    def has_changes(self) -> bool:
        """Check if there are unsaved changes."""
        return self._changed

    def save(self) -> bool:
        """Save userdata to disk by diffing working copy against defaults."""
        if not self._changed:
            return True

        userdata = self._generate_userdata()
        success = save_userdata(userdata, self.userdata_path)
        if success:
            self._changed = False
        return success

    def reload(self) -> None:
        """Reload config and userdata from disk, rebuild working copy."""
        self.config = SkinConfig.load(
            self.shortcuts_path, load_user=True, userdata_path=self.userdata_path
        )
        self.working = {
            menu.name: copy.deepcopy(menu) for menu in self.config.menus
        }
        self._changed = False

    def _generate_userdata(self) -> UserData:
        """Generate userdata by diffing working copy against defaults."""
        userdata = UserData()

        # Build default menu lookup
        default_menus = {m.name: m for m in self.config.default_menus}

        for menu_id, working_menu in self.working.items():
            default_menu = default_menus.get(menu_id)
            menu_override = self._diff_menu(working_menu, default_menu)
            if menu_override:
                userdata.menus[menu_id] = menu_override

        return userdata

    def _diff_menu(self, working: Menu, default: Menu | None) -> MenuOverride | None:
        """Generate diff for a single menu."""
        override = MenuOverride()

        if default is None:
            # Entirely user-created menu - all items are new
            for item in working.items:
                override.items.append(self._item_to_override(item, is_new=True))
            return override if override.items else None

        default_items = {item.name: item for item in default.items}
        working_items = {item.name: item for item in working.items}

        # Find removed items (skip items filtered by dialog_visible)
        for name, default_item in default_items.items():
            if name not in working_items:
                # Don't mark as removed if it was filtered by dialog_visible
                if default_item.dialog_visible and not _check_dialog_visible(
                    default_item.dialog_visible
                ):
                    continue
                override.removed.append(name)

        # Find modified or new items (preserving working order for position tracking)
        for idx, working_item in enumerate(working.items):
            default_item = default_items.get(working_item.name)

            if default_item is None:
                # New item
                item_override = self._item_to_override(working_item, is_new=True)
                item_override.position = idx
                override.items.append(item_override)
            else:
                # Check for modifications or position change
                default_idx = next(
                    (i for i, d in enumerate(default.items) if d.name == working_item.name),
                    None
                )
                position_changed = default_idx != idx
                item_diff = self._diff_item(working_item, default_item)

                if item_diff or position_changed:
                    if item_diff is None:
                        item_diff = MenuItemOverride(name=working_item.name)
                    # Always include position if item is in userdata
                    item_diff.position = idx
                    override.items.append(item_diff)

        # Only return if there are actual changes
        if not override.items and not override.removed:
            return None
        return override

    def _diff_item(self, working: MenuItem, default: MenuItem) -> MenuItemOverride | None:
        """Generate diff for a single item - only include changed fields."""
        diff = MenuItemOverride(name=working.name)
        has_changes = False

        if working.label != default.label:
            diff.label = working.label
            has_changes = True

        if working.actions != default.actions:
            diff.actions = working.actions
            has_changes = True

        if working.icon != default.icon:
            diff.icon = working.icon
            has_changes = True

        if working.disabled != default.disabled:
            diff.disabled = working.disabled
            has_changes = True

        # Check properties - only save those that differ
        if working.properties != default.properties:
            diff_props = {
                k: v for k, v in working.properties.items()
                if default.properties.get(k) != v
            }
            if diff_props:
                diff.properties = diff_props
                has_changes = True

        return diff if has_changes else None

    def _item_to_override(self, item: MenuItem, is_new: bool = False) -> MenuItemOverride:
        """Convert full item to override format."""
        return MenuItemOverride(
            name=item.name,
            label=item.label,
            actions=item.actions,
            icon=item.icon,
            disabled=item.disabled if item.disabled else None,
            properties=item.properties.copy() if item.properties else {},
            is_new=is_new,
        )
