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

### load_backgrounds(path) → BackgroundConfig

Load complete background configuration. Returns BackgroundConfig containing:
- `backgrounds` - Flat list of root-level Background objects
- `groupings` - Backgrounds and groups for picker navigation

***

## Internal Parsers

| Function | Parses |
|----------|--------|
| `_parse_background` | Background with name, label, path, type, sources |
| `_parse_background_group` | Group with nested backgrounds/groups/content |

**Source types:** BROWSE/MULTI use BrowseSource, PLAYLIST types use PlaylistSource.

***

## XML Reference

See [skinning/backgrounds.md](../../skinning/backgrounds.md) for full XML documentation.
