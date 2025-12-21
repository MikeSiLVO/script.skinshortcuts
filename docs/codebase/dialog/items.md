# dialog/items.py

**Path:** `resources/lib/skinshortcuts/dialog/items.py`
**Lines:** 408
**Purpose:** Item operations - add, delete, move, label, icon, action.

***

## Overview

ItemsMixin provides all item manipulation operations including add, delete, move, and property changes. Also handles browsing with sources and context menu.

***

## ItemsMixin Class (line 24)

### Item Operations

#### `_add_item`() (line 54)

Add a new item after the current selection.

#### `_delete_item`() (line 74)

Delete the selected item.

**Checks:**

* Required items cannot be deleted
* Protection may require confirmation

**Behavior:**

* Removes from manager's working copy
* Updates deleted property indicator (via manager)

#### `_move_item`(direction) (line 106)

Move item up (-1) or down (1).

**Note:** Manager handles the swap in working copy; dialog just rebuilds list.

#### `_toggle_disabled`() (line 184)

Toggle the disabled state of selected item.

#### `_restore_deleted_item`() (line 198)

Show picker to restore a previously deleted item.

**Behavior:**

* Gets removed items from manager (compares working vs defaults)
* Restores via manager.restore_item()

#### `_reset_current_item`() (line 233)

Reset item to skin defaults. Restores original properties from skin config.

***

### Label/Icon/Action Methods

#### `_set_label`() (line 121)

Change label via keyboard input.

#### `_set_icon`() (line 139)

Browse for icon using icon sources from menus.xml.

#### `_set_action`() (line 159)

Set custom action via keyboard.

**Checks:**

* Protection may require confirmation for action changes

***

### Property Setter

#### `_set_item_property`(item, name, value, related, apply_suffix) (line 346)

Unified property setter for menu items.

**Parameters:**

* `item` - The menu item to update
* `name` - Property name (e.g., "widget", "background")
* `value` - Property value, or None to clear
* `related` - Optional dict of related properties to auto-populate
* `apply_suffix` - If True, apply property_suffix to names

**Behavior:**

* Updates both manager (for persistence) and local item state (for UI)
* Handles clearing properties when value is None

***

### Browse Methods

#### `_browse_with_sources`(sources, title, browse_type, mask) → str | None (line 255)

Browse for a file using configured sources.

**Parameters:**

* `sources` - List of IconSource or BrowseSource objects
* `title` - Dialog title
* `browse_type` - Kodi browse type (0=folder, 2=image file)
* `mask` - File mask for filtering (e.g., ".png|.jpg")

**Behavior:**

* No sources: Free browse
* Single source without label: Browse directly from path
* Multiple sources: Show picker first, then browse from selection
* "browse" path: Free file browser

***

### Context Menu

#### `_show_context_menu`() (line 326)

Show context menu for selected item.

**Options:**

* Edit Label
* Edit Action
* Change Icon
* Edit Submenu
* Delete
