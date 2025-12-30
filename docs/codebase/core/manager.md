# manager.py

**Path:** `resources/lib/skinshortcuts/manager.py`
**Purpose:** Menu manager for dialog operations - API for modifying menus.

***

## Overview

MenuManager provides the API for modifying menus through the management dialog. Uses a working copy pattern where edits happen in memory and saves diff-based userdata on close.

***

## Architecture

- **defaults**: Immutable skin defaults (from config.default_menus)
- **working**: Mutable working copy for all edits
- **save**: Diffs working against defaults to generate minimal userdata

***

## MenuManager Class

### `__init__`(shortcuts_path, userdata_path=None)

Initialize manager. Loads config and creates working copy.

### Menu Access

| Method | Returns | Description |
|--------|---------|-------------|
| `get_menu_ids()` | list[str] | All menu names |
| `get_all_menus()` | list[Menu] | All menus from working copy |
| `get_menu_items(menu_id)` | list[MenuItem] | Items for a menu |

### Item Operations

| Method | Returns | Description |
|--------|---------|-------------|
| `add_item(menu_id, after_index, label)` | MenuItem | Add new item |
| `remove_item(menu_id, item_id)` | bool | Remove item |
| `restore_item(menu_id, item)` | bool | Restore deleted item |
| `reset_item(menu_id, item_id)` | bool | Reset to skin defaults |
| `move_item(menu_id, item_id, direction)` | bool | Move up (-1) or down (+1) |
| `is_item_modified(menu_id, item_id)` | bool | Check if differs from default |
| `get_removed_items(menu_id)` | list[MenuItem] | Restorable items |

### Property Setters

All return bool. Update working copy.

| Method | Description |
|--------|-------------|
| `set_label(menu_id, item_id, label)` | Set label |
| `set_action(menu_id, item_id, action)` | Set action(s) |
| `set_icon(menu_id, item_id, icon)` | Set icon |
| `set_disabled(menu_id, item_id, disabled)` | Set disabled state |
| `set_custom_property(menu_id, item_id, name, value)` | Set custom property |

### Persistence

| Method | Returns | Description |
|--------|---------|-------------|
| `has_changes()` | bool | Check for unsaved changes |
| `save()` | bool | Save userdata (diff against defaults) |
| `reload()` | None | Reload from disk |
