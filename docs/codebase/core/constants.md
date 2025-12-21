# constants.py

**Path:** `resources/lib/skinshortcuts/constants.py`
**Lines:** 86
**Purpose:** Central location for all constant values used throughout the addon.

***

## File Name Constants (lines 5-11)

| Constant | Value | Used By |
|----------|-------|---------|
| `MENU_FILE` | `"menu.xml"` | hashing.py, loaders/menu.py |
| `MENUS_FILE` | `"menus.xml"` | hashing.py, loaders/menu.py, entry.py |
| `WIDGETS_FILE` | `"widgets.xml"` | hashing.py, config.py |
| `BACKGROUNDS_FILE` | `"backgrounds.xml"` | hashing.py, config.py |
| `PROPERTIES_FILE` | `"properties.xml"` | hashing.py, config.py |
| `TEMPLATES_FILE` | `"templates.xml"` | hashing.py, config.py |
| `INCLUDES_FILE` | `"script-skinshortcuts-includes.xml"` | hashing.py, entry.py |

***

## Default Values (lines 13-14)

| Constant | Value | Used By |
|----------|-------|---------|
| `DEFAULT_ICON` | `"DefaultShortcut.png"` | models/menu.py, providers/content.py |
| `DEFAULT_TARGET` | `"videos"` | models/widget.py |

***

## Type Sets (lines 16-54)

### WIDGET_TYPES (line 16)

Valid widget content types. Frozen set for immutability and O(1) lookup.

Values: `movies`, `tvshows`, `episodes`, `musicvideos`, `artists`, `albums`, `songs`, `pvr`, `pictures`, `programs`, `addons`, `files`, `custom`

**Used by:** loaders/widget.py for validation

### WIDGET_TARGETS (line 34)

Valid widget target windows.

Values: `videos`, `music`, `pictures`, `programs`, `pvr`, `files`

**Used by:** loaders/widget.py for validation

### PROPERTY_TYPES (line 45)

Valid property editor types for custom properties.

Values: `select`, `text`, `number`, `bool`, `image`, `path`

**Used by:** loaders/property.py for validation

***

## Mapping Dictionaries (lines 57-85)

### WINDOW_MAP (line 59)

Maps various content type aliases to canonical Kodi window names.

| Input Aliases | Output |
|---------------|--------|
| `video`, `videos` | `Videos` |
| `music`, `audio` | `Music` |
| `pictures`, `images` | `Pictures` |
| `programs`, `executable` | `Programs` |
| `pvr`, `tv`, `livetv` | `TVChannels` |
| `radio`, `liveradio` | `RadioChannels` |

**Used by:** providers/content.py

### TARGET_MAP (line 76)

Normalizes content target strings to lowercase canonical form.

| Input Aliases | Output |
|---------------|--------|
| `video`, `videos` | `videos` |
| `music`, `audio` | `music` |
| `pictures`, `images` | `pictures` |
| `programs`, `executable` | `programs` |

**Used by:** loaders/widget.py, providers/content.py

***

## Test Candidates

1. Verify all file constants match actual files in skin shortcuts folder
2. Verify `WIDGET_TYPES`/`WIDGET_TARGETS` contain all valid Kodi content types
3. Verify `WINDOW_MAP`/`TARGET_MAP` produce correct Kodi window names
