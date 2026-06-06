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
| `get_widgets()` | list[tuple[str,str]] | Available widgets as (name, label) |
| `get_backgrounds()` | list[tuple[str,str]] | Available backgrounds as (name, label) |

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
| `has_removed_items(menu_id)` | bool | Whether menu has restorable removed items |

### Property Setters

All return bool. Update working copy.

| Method | Description |
|--------|-------------|
| `set_label(menu_id, item_id, label)` | Set label |
| `set_action(menu_id, item_id, action)` | Set action(s) |
| `set_icon(menu_id, item_id, icon)` | Set icon |
| `set_disabled(menu_id, item_id, disabled)` | Set disabled state |
| `set_submenu(menu_id, item_id, submenu)` | Set or clear submenu template reference |
| `set_visible(menu_id, item_id, visible)` | Set runtime visibility condition (used by shortcut picker) |
| `set_widget(menu_id, item_id, widget)` | Set widget property (delegates to set_custom_property) |
| `set_background(menu_id, item_id, background)` | Set background property (delegates to set_custom_property) |
| `set_custom_property(menu_id, item_id, name, value)` | Set custom property |

### Submenu Operations

Each item linked to a `<submenu>` template has its own working copy, keyed by `{parent_menu}/{item_name}` in `self.working`. Referenced templates are filtered out of `self.working` at init (they are seed sources only).

| Method | Returns | Description |
|--------|---------|-------------|
| `submenu_key(parent, item_name)` | str | Compute the per-item working key |
| `submenu_template(item)` | str | Template name to seed from (`item.submenu`, or empty string if unbound) |
| `ensure_item_submenu(parent, item)` | Menu | Return the per-item submenu, seeding from template on first access |
| `drop_per_item_submenu(parent, item_name)` | None | Discard per-item submenu so next access reseeds from template |

### Custom Widget Operations

| Method | Returns | Description |
|--------|---------|-------------|
| `create_custom_widget_menu(menu_id, item_id, suffix)` | str | Create custom widget menu, return its ID |
| `get_custom_widget_menu(menu_id, item_id, suffix)` | str | Get custom widget menu ID |
| `clear_custom_widget(menu_id, item_id, suffix)` | bool | Clear custom widget menu and reference |

Custom widget menus use auto-generated IDs (`custom-{uuid}`) and are referenced via `customWidget` or `customWidget.{N}` properties on items.

### Reset Operations

| Method | Returns | Description |
|--------|---------|-------------|
| `reset_menu(menu_id)` | bool | Reset single menu to defaults |
| `reset_menu_tree(menu_id)` | bool | Reset menu and all referenced submenus |
| `reset_all_submenus()` | bool | Reset all menus with `is_submenu=True` |

**reset_menu**: For per-item keys (`parent/item`), re-seeds from the item's template.

**reset_menu_tree**: Recurses into per-item submenu keys with cycle detection.

**reset_all_submenus**: Resets menus defined with `<submenu>` tag (not `<menu>`).

### Persistence

| Method | Returns | Description |
|--------|---------|-------------|
| `has_changes()` | bool | Check for unsaved changes |
| `save()` | bool | Save userdata (diff against defaults) |
| `reload()` | None | Reload from disk |
