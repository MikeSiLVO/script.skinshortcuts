# manager.py

**Path:** `resources/lib/skinshortcuts/manager.py`
**Lines:** 503
**Purpose:** Menu manager for dialog operations - provides API for modifying menus.

***

## Overview

MenuManager is the primary interface for modifying menus through the management dialog. It uses a working copy architecture where all edits happen in memory, and saves diff-based userdata on close.

***

## Architecture

### Working Copy Pattern

* **defaults**: Immutable skin defaults (from `config.default_menus`)
* **working**: Mutable working copy (deep copy of merged menus)
* **save**: Diffs working against defaults to generate minimal userdata

All edit operations modify `self.working`. On save, the manager compares working against defaults and only writes changes to userdata.

***

## MenuManager Class (line 19)

### `__init__`(shortcuts_path, userdata_path=None) (line 27)

Initialize manager.

**Parameters:**

* `shortcuts_path` - Path to skin's shortcuts folder
* `userdata_path` - Optional custom userdata path (for testing)

**Instance attributes:**

* `shortcuts_path` - Path object
* `userdata_path` - Custom path or None
* `config` - SkinConfig (loaded with userdata merged)
* `working` - Dict[str, Menu] working copy for all edits
* `_changed` - Dirty flag

***

## Menu Access Methods

### get_menu_ids() → list[str] (line 49)

Get all available menu names from config.

### get_all_menus() → list[Menu] (line 53)

Get all menus from working copy.

Returns list of Menu objects ready for building includes.

### get_menu_items(menu_id) → list[MenuItem] (line 61)

Get items for a menu from working copy.

### get_widgets() → list[tuple[str, str]] (line 67)

Get available widgets as (name, label) tuples.

### get_backgrounds() → list[tuple[str, str]] (line 71)

Get available backgrounds as (name, label) tuples.

***

## Item Operations

### add_item(menu_id, after_index=None, label="") → MenuItem (line 111)

Add a new item to a menu.

**Behavior:**

* Generates unique name: `user-{uuid}`
* Creates MenuItem with noop action
* Adds to working copy at specified position or end

**Returns:** The newly created MenuItem

### remove_item(menu_id, item_id) → bool (line 142)

Remove an item from a menu's working copy.

### restore_item(menu_id, item) → bool (line 164)

Restore a previously deleted item to working copy.

Deep copies the item to avoid reference sharing.

### reset_item(menu_id, item_id) → bool (line 183)

Reset an item to its skin default values.

Replaces item in working copy with deep copy from defaults.

### is_item_modified(menu_id, item_id) → bool (line 219)

Check if an item differs from its skin default.

Compares label, actions, icon, disabled, and properties.

### get_removed_items(menu_id) → list[MenuItem] (line 237)

Get default items that have been removed from working copy.

Returns list of MenuItems that can be restored.

### has_removed_items(menu_id) → bool (line 257)

Check if menu has removed items that can be restored.

### move_item(menu_id, item_id, direction) → bool (line 261)

Move an item up (-1) or down (+1) in working copy.

Swaps items directly in the working list.

***

## Property Setters

All return bool (True on success):

### set_label(menu_id, item_id, label) (line 258)

Set the label for an item.

### set_action(menu_id, item_id, action) (line 262)

Set the action(s) for an item.

Accepts string or list of strings.

### set_icon(menu_id, item_id, icon) (line 276)

Set the icon for an item.

### set_widget(menu_id, item_id, widget) (line 280)

Set the widget for an item.

Stored as "widget" property.

### set_background(menu_id, item_id, background) (line 287)

Set the background for an item.

Stored as "background" property.

### set_disabled(menu_id, item_id, disabled) (line 294)

Set the disabled state for an item.

### set_custom_property(menu_id, item_id, prop_name, value) (line 298)

Set a custom property on an item in working copy.

***

## Internal Methods

### `_get_working_item`(menu_id, item_name) → MenuItem | None (line 75)

Get item from working copy.

### `_ensure_working_menu`(menu_id) → Menu (line 83)

Ensure menu exists in working copy, create if needed.

### `_set_item_property`(menu_id, item_id, prop, value) (line 314)

Set a property on an item in working copy.

Handles action list conversion to Action objects.

### `_generate_userdata`() → UserData (line 356)

Generate userdata by diffing working copy against defaults.

### `_diff_menu`(working, default) → MenuOverride | None (line 371)

Generate diff for a single menu.

Tracks removed items, modified items, new items, and position changes.

### `_diff_item`(working, default) → MenuItemOverride | None (line 419)

Generate diff for a single item - only include changed fields.

### `_item_to_override`(item, is_new=False) → MenuItemOverride (line 452)

Convert full item to override format.

***

## Persistence

### has_changes() → bool (line 331)

Check if there are unsaved changes.

### save() → bool (line 335)

Save userdata to disk by diffing working copy against defaults.

Generates minimal userdata containing only changes from defaults.

### reload() (line 346)

Reload config and userdata from disk, rebuild working copy.

***

## Test Candidates

1. Working copy isolation (edits don't affect config)
2. `reset_item()` restores from defaults
3. `is_item_modified()` comparison logic
4. `_generate_userdata()` diff correctness
5. `save()` / `reload()` round-trip with working copy
