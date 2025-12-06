"""User data storage and merging."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:
    import xbmc
    import xbmcvfs

    IN_KODI = True
except ImportError:
    IN_KODI = False

from .models import Action, Menu, MenuItem


def get_userdata_path() -> str:
    """Get path to userdata file for current skin."""
    if IN_KODI:
        skin_dir = xbmc.getSkinDir()
        data_path = xbmcvfs.translatePath("special://profile/addon_data/script.skinshortcuts/")
        return str(Path(data_path) / f"{skin_dir}.userdata.json")
    return ""


@dataclass
class MenuItemOverride:
    """User override for a menu item."""

    name: str
    label: str | None = None
    actions: list[Action] | None = None  # List of actions (with optional conditions)
    icon: str | None = None
    disabled: bool | None = None
    properties: dict[str, str] = field(default_factory=dict)  # Includes widget/background
    position: int | None = None  # For reordering
    is_new: bool = False  # True if user-added item


@dataclass
class MenuOverride:
    """User overrides for a menu."""

    items: list[MenuItemOverride] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)  # Names of removed items


def _menu_override_to_dict(override: MenuOverride) -> dict[str, Any]:
    """Convert MenuOverride to dict, omitting empty values."""
    result: dict[str, Any] = {}
    if override.items:
        result["items"] = [_item_override_to_dict(item) for item in override.items]
    if override.removed:
        result["removed"] = override.removed
    return result


def _item_override_to_dict(item: MenuItemOverride) -> dict[str, Any]:
    """Convert MenuItemOverride to dict, omitting None/empty values."""
    result: dict[str, Any] = {"name": item.name}

    if item.label is not None:
        result["label"] = item.label
    if item.actions is not None:
        result["actions"] = [asdict(a) for a in item.actions]
    if item.icon is not None:
        result["icon"] = item.icon
    if item.disabled is not None:
        result["disabled"] = item.disabled
    if item.properties:
        result["properties"] = item.properties
    if item.position is not None:
        result["position"] = item.position
    if item.is_new:
        result["is_new"] = item.is_new

    return result


@dataclass
class UserData:
    """All user customizations for a skin."""

    menus: dict[str, MenuOverride] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "menus": {
                menu_id: _menu_override_to_dict(override)
                for menu_id, override in self.menus.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserData:
        """Create from dictionary."""
        menus = {}
        for menu_id, menu_data in data.get("menus", {}).items():
            items = []
            for item_data in menu_data.get("items", []):
                # Convert actions list to Action objects
                actions_data = item_data.pop("actions", None)
                actions = None
                if actions_data is not None:
                    actions = []
                    for act in actions_data:
                        if isinstance(act, dict):
                            actions.append(Action(**act))
                        else:
                            # Legacy: plain string action
                            actions.append(Action(action=act))
                items.append(MenuItemOverride(**item_data, actions=actions))
            removed = menu_data.get("removed", [])
            menus[menu_id] = MenuOverride(items=items, removed=removed)
        return cls(menus=menus)


def load_userdata(path: str | None = None) -> UserData:
    """Load user data from JSON file."""
    if path is None:
        path = get_userdata_path()

    if not path:
        return UserData()

    try:
        file_path = Path(path)
        if file_path.exists():
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
                return UserData.from_dict(data)
    except (OSError, json.JSONDecodeError) as e:
        if IN_KODI:
            xbmc.log(f"[skinshortcuts] Failed to load userdata from {path}: {e}", xbmc.LOGERROR)

    return UserData()


def save_userdata(userdata: UserData, path: str | None = None) -> bool:
    """Save user data to JSON file."""
    if path is None:
        path = get_userdata_path()

    if not path:
        return False

    try:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(userdata.to_dict(), f, indent=2)
        return True
    except OSError as e:
        if IN_KODI:
            xbmc.log(f"[skinshortcuts] Failed to save userdata to {path}: {e}", xbmc.LOGERROR)
        return False


def _check_dialog_visible(condition: str) -> bool:
    """Check if a Kodi visibility condition passes for dialog filtering.

    Returns True if condition is empty or passes.
    """
    if not condition:
        return True
    if not IN_KODI:
        return True
    return xbmc.getCondVisibility(condition)


def merge_menu(default_menu: Menu, override: MenuOverride | None) -> Menu:
    """Merge default menu with user overrides."""
    if override is None:
        # No user customization - filter by dialog_visible
        filtered_items = [
            item for item in default_menu.items
            if _check_dialog_visible(item.dialog_visible)
        ]
        return Menu(
            name=default_menu.name,
            items=filtered_items,
            defaults=default_menu.defaults,
            container=default_menu.container,
            allow=default_menu.allow,
            is_submenu=default_menu.is_submenu,
        )

    # Start with default items, excluding removed ones and those failing dialog_visible
    items: list[MenuItem] = []
    for item in default_menu.items:
        if item.name in override.removed:
            continue
        # Filter by dialog_visible for items not explicitly in userdata
        if item.name not in {o.name for o in override.items} and not _check_dialog_visible(
            item.dialog_visible
        ):
            continue
        items.append(item)

    # Create lookup for overrides
    override_map = {o.name: o for o in override.items}

    # Apply overrides to existing items
    for i, item in enumerate(items):
        if item.name in override_map:
            ovr = override_map[item.name]
            items[i] = _apply_override(item, ovr)

    # Add new user items at their specified positions (or at the end)
    new_items = [o for o in override.items if o.is_new]
    for new_item in new_items:
        items.append(_create_item_from_override(new_item))

    # Reorder items based on positions
    # Positions represent the desired index in the final list
    # Items with positions are placed at their exact index
    # Items without positions keep their relative order, filling gaps

    # Collect items with explicit positions
    positioned_items: dict[int, MenuItem] = {}
    unpositioned_items: list[MenuItem] = []

    for item in items:
        ovr = override_map.get(item.name)
        if ovr and ovr.position is not None:
            positioned_items[ovr.position] = item
        else:
            unpositioned_items.append(item)

    # Build final list by placing items at their positions
    final_items: list[MenuItem] = []
    unpos_iter = iter(unpositioned_items)

    for i in range(len(items)):
        if i in positioned_items:
            final_items.append(positioned_items[i])
        else:
            # Fill with next unpositioned item
            try:
                final_items.append(next(unpos_iter))
            except StopIteration:
                break

    # Append any remaining unpositioned items
    for item in unpos_iter:
        final_items.append(item)

    return Menu(
        name=default_menu.name,
        items=final_items,
        defaults=default_menu.defaults,
        container=default_menu.container,
        allow=default_menu.allow,
        is_submenu=default_menu.is_submenu,
    )


def _apply_override(item: MenuItem, override: MenuItemOverride) -> MenuItem:
    """Apply user override to a menu item."""
    return MenuItem(
        name=item.name,
        label=override.label if override.label is not None else item.label,
        actions=override.actions if override.actions is not None else item.actions,
        label2=item.label2,
        icon=override.icon if override.icon is not None else item.icon,
        thumb=item.thumb,
        visible=item.visible,
        disabled=override.disabled if override.disabled is not None else item.disabled,
        required=item.required,
        protection=item.protection,
        properties={**item.properties, **override.properties},
        submenu=item.submenu,
        original_action=item.action,  # Store original for protection matching
    )


def _create_item_from_override(override: MenuItemOverride) -> MenuItem:
    """Create a new menu item from user override."""
    return MenuItem(
        name=override.name,
        label=override.label or "",
        actions=override.actions or [Action(action="noop")],
        icon=override.icon or "DefaultShortcut.png",
        properties=override.properties,
    )
