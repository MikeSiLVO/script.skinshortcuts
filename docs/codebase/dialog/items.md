# dialog/items.py

**Path:** `resources/lib/skinshortcuts/dialog/items.py`
**Purpose:** Item operations - add, delete, move, label, icon, action.

***

## Overview

ItemsMixin provides all item manipulation operations including add, delete, move, and property changes. Also handles browsing with sources and context menu.

***

## ItemsMixin Class

### Item Operations

#### `_add_item`()

Add a new item after the current selection.

#### `_delete_item`()

Delete the selected item.

**Checks:**

* Required items cannot be deleted
* Protection may require confirmation

**Behavior:**

* Removes from manager's working copy
* Updates deleted property indicator (via manager)

#### `_move_item`(direction)

Move item up (-1) or down (1).

**Note:** Manager handles the swap in working copy; dialog just rebuilds list.

#### `_toggle_disabled`()

Toggle the disabled state of selected item.

**Checks:**

* Required items cannot be disabled

#### `_restore_deleted_item`()

Show picker to restore a previously deleted item.

**Behavior:**

* Gets removed items from manager (compares working vs defaults)
* Items hidden by `dialog_visible` condition are excluded (they're not actually deleted)
* Restores via manager.restore_item()

#### `_reset_current_item`()

Reset item to skin defaults. Restores original properties from skin config.

***

### Label/Icon/Action Methods

#### `_set_label`()

Change label via keyboard input.

#### `_set_icon`()

Browse for icon using icon sources from menus.xml.

#### `_set_action`()

Set custom action via keyboard.

**Checks:**

* Protection may require confirmation for action changes

***

### Property Setter

#### `_set_item_property`(item, name, value, related, apply_suffix)

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

#### `_browse_with_sources`(sources, title, browse_type, mask) → str | None

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

#### `_show_context_menu`()

Show context menu for selected item.

**Options:**

* Edit Label
* Edit Action
* Change Icon
* Edit Submenu
* Delete
