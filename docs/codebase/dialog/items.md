# dialog/items.py

**Path:** `resources/lib/skinshortcuts/dialog/items.py`
**Purpose:** Item operations - add, delete, move, label, icon, action.

***

## Overview

ItemsMixin provides item manipulation operations and context menu.

***

## ItemsMixin Class

### Item Operations

| Method | Purpose |
|--------|---------|
| `_add_item` | Add new item after current selection |
| `_delete_item` | Delete selected (checks required/protection) |
| `_move_item(direction)` | Move item up (-1) or down (1) |
| `_toggle_disabled` | Toggle disabled state (checks required) |
| `_restore_deleted_item` | Show picker to restore deleted item |
| `_reset_current_item` | Reset item to skin defaults |

### Label/Icon/Action

| Method | Purpose |
|--------|---------|
| `_set_label` | Change label via keyboard |
| `_set_icon` | Browse for icon using configured sources |
| `_set_action` | Set custom action (checks protection) |

### Property Setter

#### `_set_item_property`(item, name, value, related, apply_suffix)

Unified property setter. Updates manager and local item state.

### Browse Methods

#### `_browse_with_sources`(sources, title, browse_type, mask) → str | None

Browse for file using configured sources. Handles single/multiple sources and "browse" path.

### Context Menu

#### `_show_context_menu`()

Show context menu with Edit Label, Edit Action, Change Icon, Edit Submenu, Delete.
