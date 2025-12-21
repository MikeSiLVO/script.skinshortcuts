# dialog/properties.py

**Path:** `resources/lib/skinshortcuts/dialog/properties.py`
**Purpose:** Property management - widget, background, toggle, options.

***

## Overview

PropertiesMixin handles property button clicks from the schema and manages widget, background, toggle, and options properties.

***

## PropertiesMixin Class

### Property Button Handler

#### `_handle_property_button`(button_id) → bool

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

#### `_handle_widget_property`(prop, item)

Show widget picker and auto-populate related properties.

**Sets:**

* `{prefix}` - Widget name
* `{prefix}Label` - Display label
* `{prefix}Path` - Widget path
* `{prefix}Type` - Widget type
* `{prefix}Target` - Target window
* `{prefix}Source` - Widget source (library, playlist, addon)

**Note:** For custom widgets, sets `widgetType=custom` which triggers onclose action.

#### `_set_widget_properties`(item, prefix, widget)

Set widget properties on item with auto-populated values.

Handles `{menuitem}` placeholder substitution in widget path.

#### `_clear_widget_properties`(item, prefix)

Clear all widget properties for a prefix.

***

### Background Properties

#### `_handle_background_property`(prop, item)

Show background picker and auto-populate related properties.

**Handles background types:**

* `STATIC` - Predefined path
* `BROWSE` - Single image browser
* `MULTI` - Folder browser
* `PLAYLIST` / `LIVE_PLAYLIST` - Playlist picker

#### `_set_background_properties`(item, prefix, bg)

Set background properties on item.

**Sets:**

* `{prefix}` - Background name
* `{prefix}Label` - Display label
* `{prefix}Path` - Background path

#### `_set_background_properties_custom`(item, prefix, bg, custom_path, custom_label, playlist_type="")

Set background with user-browsed custom path.

Used for browse, multi, and playlist backgrounds.

**Sets:**

* `{prefix}` - Background name
* `{prefix}Label` - Display label
* `{prefix}Path` - Background path
* `{prefix}PlaylistType` - Playlist type (movies, tvshows, episodes, musicvideos, songs, albums, artists, mixed)

#### `_clear_background_properties`(item, prefix)

Clear all background properties for a prefix.

***

### Playlist Picker

#### `_pick_playlist`(sources, label_prefix, current_path) → tuple[str, str, str] | None

Show picker for available playlists.

**Parameters:**

* `sources` - List of PlaylistSource objects (or defaults to video/music playlists)
* `label_prefix` - Prefix for playlist labels (e.g., "Live Background")
* `current_path` - Current playlist path to preselect (default "")

**Returns:** Tuple of (path, display_label, playlist_type) or None if cancelled

**Behavior:**

* Preselects playlist matching `current_path`
* Uses `scan_playlist_files()` from providers module
* Returns playlist type for artwork decisions (episodes/musicvideos lack posters)

***

### Smart Playlist Parsing

#### `_parse_smart_playlist`(filepath) → tuple[str, str]

Parse a smart playlist (.xsp file) for name and type.

**Parameters:**

* `filepath` - Path to the .xsp file

**Returns:** Tuple of (name, playlist_type)

**Behavior:**

* Uses `_resolve_playlist_path()` to handle multipath URLs
* Parses XML to extract `<name>` element text
* Extracts `type` attribute from root `<smartplaylist>` element
* Returns raw type: movies, tvshows, episodes, musicvideos, songs, albums, artists, mixed

***

### Multipath Resolution

#### `_get_multipath_sources`(multipath_url) → list[str]

Extract real paths from a Kodi multipath:// URL.

**Parameters:**

* `multipath_url` - A multipath:// URL (e.g., `multipath://%2fpath1%2f/%2fpath2%2f/`)

**Returns:** List of decoded paths

**Behavior:**

* Kodi multipaths combine multiple directories into one virtual path
* Format: `multipath://{URL_encoded_path1}/{URL_encoded_path2}/`
* Returns original path if not a multipath URL

#### `_resolve_playlist_path`(filepath) → str | None

Resolve a playlist path to an actual readable file path.

**Parameters:**

* `filepath` - Path to resolve (may use special:// paths)

**Returns:** Resolved filesystem path, or None if file not found

**Behavior:**

* Translates special:// paths using `xbmcvfs.translatePath()`
* Handles `special://videoplaylists/` which is a multipath combining video and mixed playlist directories
* Searches each source directory in the multipath for the file
* Returns the first existing path found

***

### Other Property Types

#### `_handle_toggle_property`(prop, item)

Toggle between "True" and empty (cleared).

#### `_handle_options_property`(prop, item) → bool

Show options list picker.

**Behavior:**

* Filters options by condition
* Shows icons if configured
* Supports "None" option to clear
* Preselects current option value
