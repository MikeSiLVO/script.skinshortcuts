# dialog/base.py

**Path:** `resources/lib/skinshortcuts/dialog/base.py`
**Purpose:** Core dialog functionality - initialization, list management, event routing.

***

## Overview

DialogBaseMixin provides foundation for the management dialog: initialization, list control management, property access, and event routing.

***

## Control IDs

| Constant | ID | Purpose |
|----------|-----|---------|
| `CONTROL_LIST` | 211 | Menu items list |
| `CONTROL_ADD` | 301 | Add item |
| `CONTROL_DELETE` | 302 | Delete item |
| `CONTROL_MOVE_UP` | 303 | Move up |
| `CONTROL_MOVE_DOWN` | 304 | Move down |
| `CONTROL_SET_LABEL` | 305 | Change label |
| `CONTROL_SET_ICON` | 306 | Change icon |
| `CONTROL_SET_ACTION` | 307 | Change action |
| `CONTROL_RESTORE_DELETED` | 311 | Restore deleted |
| `CONTROL_RESET_ITEM` | 312 | Reset to defaults |
| `CONTROL_TOGGLE_DISABLED` | 313 | Enable/disable |
| `CONTROL_CHOOSE_SHORTCUT` | 401 | Choose from groupings |
| `CONTROL_EDIT_SUBMENU` | 405 | Edit submenu |

***

## Constructor Parameters (via kwargs)

| Parameter | Type | Description |
|-----------|------|-------------|
| `menu_id` | str | Menu to edit (default "mainmenu") |
| `manager` | MenuManager | Shared manager for child dialogs |
| `property_schema` | PropertySchema | Shared schema |
| `dialog_mode` | str | Mode for Home window property |
| `property_suffix` | str | Suffix for widget slots |
| `selected_index` | int | Item to select on open |

***

## Key Methods

| Method | Purpose |
|--------|---------|
| `onInit` | Initialize/reload dialog state |
| `close` | Save changes and close (root dialog only saves) |
| `onClick` | Route control clicks to handlers |
| `onAction` | Handle cancel/context actions |
| `_load_items` | Load menu items from manager |
| `_rebuild_list` | Rebuild list control after changes |
| `_refresh_selected_item` | Update selected item's display |
| `_get_selected_item` | Get currently selected MenuItem |
| `_get_item_property` | Get property with suffix applied |
