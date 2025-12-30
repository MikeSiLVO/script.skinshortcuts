# dialog/properties.py

**Path:** `resources/lib/skinshortcuts/dialog/properties.py`
**Purpose:** Property management - widget, background, toggle, options.

***

## Overview

PropertiesMixin handles property button clicks from schema and manages widget, background, toggle, and options properties.

***

## PropertiesMixin Class

### `_handle_property_button`(button_id) → bool

Route property button click to appropriate handler based on property type from schema.

***

## Widget Properties

| Method | Purpose |
|--------|---------|
| `_handle_widget_property` | Show picker, set widget + related properties |
| `_set_widget_properties` | Set widget, widgetLabel, widgetPath, widgetType, widgetTarget, widgetSource |
| `_clear_widget_properties` | Clear all widget properties for prefix |

**Custom widgets:** Sets `widgetType=custom` which triggers onclose action for custom widget menu.

***

## Background Properties

| Method | Purpose |
|--------|---------|
| `_handle_background_property` | Show picker based on background type |
| `_set_background_properties` | Set background, backgroundLabel, backgroundPath |
| `_set_background_properties_custom` | Set with user-browsed path + playlist type |
| `_clear_background_properties` | Clear all background properties for prefix |

**Background types:** STATIC (predefined), BROWSE (single image), MULTI (folder), PLAYLIST/LIVE_PLAYLIST (playlist picker)

***

## Playlist Picker

| Method | Purpose |
|--------|---------|
| `_pick_playlist` | Show picker for playlists, returns (path, label, type) |
| `_parse_smart_playlist` | Parse .xsp for name and type |
| `_get_multipath_sources` | Extract paths from multipath:// URL |
| `_resolve_playlist_path` | Resolve special:// paths to filesystem |

***

## Other Property Types

| Method | Purpose |
|--------|---------|
| `_handle_toggle_property` | Toggle between "True" and cleared |
| `_handle_options_property` | Show options picker with condition filtering |
