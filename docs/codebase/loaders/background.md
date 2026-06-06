# loaders/background.py

**Path:** `resources/lib/skinshortcuts/loaders/background.py`
**Purpose:** Load background configuration from backgrounds.xml.

***

## Overview

Parses backgrounds.xml containing background definitions and groups for the picker dialog. Backgrounds and groups defined at root level.

***

## Background Types

| Type | Path Required | Description |
|------|---------------|-------------|
| `static` | Yes | Fixed image path |
| `property` | Yes | Path from Kodi property |
| `live` | Yes | Live background service |
| `browse` | No | User selects single image |
| `multi` | No | User selects folder for slideshow |
| `playlist` | No | User selects playlist |
| `live-playlist` | No | Live background with playlist |

***

## Public Functions

### load_backgrounds(path, icon_overrides=None) → BackgroundConfig

Load complete background configuration. Returns BackgroundConfig containing:
- `backgrounds` - Flat list of root-level Background objects
- `groupings` - Backgrounds and groups for picker navigation

`icon_overrides` is an optional override map supplied by config.py from `menu_config.icon_overrides`. Its only effect here: when present and a PlaylistSource has no explicit `icon` attribute, the loader uses `overrides.get("DefaultPlaylist.png", ...)` instead of the literal `"DefaultPlaylist.png"` default. Only the `"DefaultPlaylist.png"` key is looked up, so it resolves the default playlist-source icon rather than a general DefaultX.png map.

***

## Internal Parsers

| Function | Parses |
|----------|--------|
| `_parse_background` | Background with name, label, path, type, sources |
| `_parse_background_group` | Group with nested backgrounds/groups/content |

**Source types:** BROWSE/MULTI use BrowseSource; all other background types route `<source>` children to PlaylistSource.

***

## XML Reference

See [skinning/backgrounds.md](../../skinning/backgrounds.md) for full XML documentation.
