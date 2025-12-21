# dialog/properties.py

**Path:** `resources/lib/skinshortcuts/dialog/properties.py`
**Lines:** 565
**Purpose:** Property management - widget, background, toggle, options.

***

## Overview

PropertiesMixin handles property button clicks from the schema and manages widget, background, toggle, and options properties.

***

## PropertiesMixin Class (line 31)

### Property Button Handler

#### `_handle_property_button`(button_id) → bool (line 91)

Handle a property button click from the schema.

**Parameters:**

* `button_id` - The control button ID that was clicked

**Returns:** True if handled, False if not a property button

**Routes to:**

* Widget properties → `_handle_widget_property()`
* Background properties → `_handle_background_property()`
* Toggle properties → `_handle_toggle_property()`
* Options properties → `_handle_options_property()`

***

### Widget Properties

#### `_handle_widget_property`(prop, item) (line 130)

Show widget picker and auto-populate related properties.

**Sets:**

* `{prefix}` - Widget name
* `{prefix}Label` - Display label
* `{prefix}Path` - Widget path
* `{prefix}Type` - Widget type
* `{prefix}Target` - Target window
* `{prefix}Source` - Widget source (library, playlist, addon)

**Note:** For custom widgets, sets `widgetType=custom` which triggers onclose action.

#### `_set_widget_properties`(item, prefix, widget) (line 194)

Set widget properties on item with auto-populated values.

Handles `{menuitem}` placeholder substitution in widget path.

#### `_clear_widget_properties`(item, prefix) (line 223)

Clear all widget properties for a prefix.

***

### Background Properties

#### `_handle_background_property`(prop, item) (line 245)

Show background picker and auto-populate related properties.

**Handles background types:**

* `STATIC` - Predefined path
* `BROWSE` - Single image browser
* `MULTI` - Folder browser
* `PLAYLIST` / `LIVE_PLAYLIST` - Playlist picker

#### `_set_background_properties`(item, prefix, bg) (line 341)

Set background properties on item.

**Sets:**

* `{prefix}` - Background name
* `{prefix}Label` - Display label
* `{prefix}Path` - Background path

#### `_set_background_properties_custom`(item, prefix, bg, custom_path, custom_label) (line 351)

Set background with user-browsed custom path.

Used for browse, multi, and playlist backgrounds.

#### `_clear_background_properties`(item, prefix) (line 377)

Clear all background properties for a prefix.

***

### Playlist Picker

#### `_pick_playlist`(sources, label_prefix, current_path) → tuple[str, str] | None (line 398)

Show picker for available playlists.

**Parameters:**

* `sources` - List of PlaylistSource objects (or defaults to video/music playlists)
* `label_prefix` - Prefix for playlist labels (e.g., "Live Background")
* `current_path` - Current playlist path to preselect (default "")

**Returns:** Tuple of (path, display_label) or None if cancelled

**Behavior:**

* Preselects playlist matching `current_path`
* Uses `scan_playlist_files()` from providers module

***

### Other Property Types

#### `_handle_toggle_property`(prop, item) (line 464)

Toggle between "True" and empty (cleared).

#### `_handle_options_property`(prop, item) → bool (line 480)

Show options list picker.

**Behavior:**

* Filters options by condition
* Shows icons if configured
* Supports "None" option to clear
* Preselects current option value
