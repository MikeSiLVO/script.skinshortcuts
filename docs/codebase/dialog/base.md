# dialog/base.py

**Path:** `resources/lib/skinshortcuts/dialog/base.py`
**Lines:** 671
**Purpose:** Core dialog functionality - initialization, list management, event routing.

***

## Overview

DialogBaseMixin provides the foundation for the management dialog. It handles initialization, list control management, property access, and event routing.

***

## Constants (lines 26-44)

### Control IDs

| Constant | ID | Purpose |
|----------|-----|---------|
| `CONTROL_LIST` | 211 | Menu items list |
| `CONTROL_ADD` | 301 | Add item button |
| `CONTROL_DELETE` | 302 | Delete item button |
| `CONTROL_MOVE_UP` | 303 | Move up button |
| `CONTROL_MOVE_DOWN` | 304 | Move down button |
| `CONTROL_SET_LABEL` | 305 | Change label button |
| `CONTROL_SET_ICON` | 306 | Change icon button |
| `CONTROL_SET_ACTION` | 307 | Change action button |
| `CONTROL_RESTORE_DELETED` | 311 | Restore deleted item |
| `CONTROL_RESET_ITEM` | 312 | Reset item to defaults |
| `CONTROL_TOGGLE_DISABLED` | 313 | Enable/disable item |
| `CONTROL_CHOOSE_SHORTCUT` | 401 | Choose from groupings |
| `CONTROL_EDIT_SUBMENU` | 405 | Edit submenu |

### Action IDs

| Constant | IDs | Purpose |
|----------|-----|---------|
| `ACTION_CANCEL` | 9, 10, 92, 216, 247, 257, 275, 61467, 61448 | Close dialog |
| `ACTION_CONTEXT` | 117 | Show context menu |

***

## Functions

### get_shortcuts_path() → str (line 47)

Get path to current skin's shortcuts folder.

***

## DialogBaseMixin Class (line 55)

### Constructor Parameters (via kwargs)

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `menu_id` | str | "mainmenu" | Menu to edit |
| `shortcuts_path` | str | auto | Path to shortcuts folder |
| `manager` | MenuManager | None | Shared manager (for child dialogs) |
| `property_schema` | PropertySchema | None | Shared schema |
| `icon_sources` | list[IconSource] | None | Shared icon sources |
| `show_context_menu` | bool | None | Context menu visibility |
| `subdialogs` | list[SubDialog] | None | Subdialog definitions |
| `dialog_mode` | str | "" | Mode for Home window property |
| `property_suffix` | str | "" | Suffix for widget slots (set on Home) |
| `setfocus` | int | None | Control to focus on open |
| `selected_index` | int | None | Item index to select |
| `deleted_items` | dict | None | Shared deleted items tracker |

***

## Lifecycle Methods

### onInit() (line 175)

Called when dialog is initialized (and on regain focus).

**Behavior:**

1. Create or reuse MenuManager
2. Load or reuse PropertySchema
3. Load icon sources, context menu toggle, subdialogs
4. Set dialog mode properties on Home window (clears stale props if root dialog)
5. Load and display menu items
6. Set focus if specified

### close() (line 563)

Save changes and close dialog.

Clears Home window properties (`skinshortcuts-dialog`, `skinshortcuts-suffix`) if set.
Only root dialog saves - child dialogs share the manager.

***

## List Management Methods

### `_load_items`() (line 250)

Load menu items from manager. For empty custom widget menus, adds a default item.

### `_display_items`() (line 266)

Display items in list control. Called once during onInit.

### `_rebuild_list`(focus_index) (line 270)

Rebuild list control from self.items. Used for structural changes (add/delete/move).

### `_create_listitem`(item) → ListItem (line 287)

Create ListItem from MenuItem.

### `_populate_listitem`(listitem, item) (line 293)

Populate ListItem with all properties (label, icon, action, widget, background, custom).

### `_refresh_selected_item`() (line 370)

Refresh selected item's ListItem. Used for property changes.

***

## Item Access Methods

### `_get_selected_index`() → int (line 390)

Get currently selected list index.

### `_get_selected_item`() → MenuItem | None (line 398)

Get currently selected MenuItem.

### `_get_selected_listitem`() → ListItem | None (line 363)

Get currently selected ListItem from control.

***

## Property Access Methods

### `_suffixed_name`(name) → str (line 135)

Apply property suffix to property name (e.g., "widgetArt" → "widgetArt.2").

### `_get_item_property`(item, name) → str (line 150)

Get property value with suffix applied.

### `_get_item_properties`(item) → dict (line 406)

Get all properties as dict for condition evaluation.

### `_get_effective_properties`(item) → dict (line 418)

Get properties with fallbacks applied from schema.

### `_get_property_label`(prop_name, prop_value) → str | None (line 441)

Get display label for property value from schema.

***

## Event Routing

### onClick(control_id) (line 503)

Handle control clicks - routes to appropriate handler based on control ID.

### onAction(action) (line 543)

Handle actions (cancel closes dialog, context shows menu).

***

## Window Property Methods

### `_update_window_properties`() (line 481)

Update window properties for skin context (groupname, allowWidgets, etc).

### `_update_deleted_property`() (line 473)

Update window property for deleted items indicator.
