# models/background.py

**Path:** `resources/lib/skinshortcuts/models/background.py`
**Purpose:** Dataclasses for backgrounds and background groupings.

***

## BackgroundType Enum

| Value | Description |
|-------|-------------|
| `STATIC` | Single static image |
| `BROWSE` | User browses for single image |
| `MULTI` | User browses for folder |
| `PLAYLIST` | Slideshow from playlist |
| `PROPERTY` | Path from Kodi property |
| `LIVE` | Dynamic library content |
| `LIVE_PLAYLIST` | Dynamic from user-selected playlist |

***

## Classes

### Background

| Field | Type | Description |
|-------|------|-------------|
| `name`, `label` | str | Identifier and display |
| `path` | str | Image path (optional for browse/multi/playlist) |
| `type` | BackgroundType | Background type |
| `icon`, `condition`, `visible` | str | Display/filtering |
| `sources` | list[PlaylistSource] | For playlist types |
| `browse_sources` | list[BrowseSource] | For browse/multi types |

**Methods:** `to_properties()` - Returns dict with background, backgroundPath, backgroundLabel, backgroundType

### BackgroundGroup

| Field | Type | Description |
|-------|------|-------------|
| `name`, `label` | str | Identifier and display |
| `icon`, `condition`, `visible` | str | Display/filtering |
| `items` | list | Child Backgrounds, BackgroundGroups, or Content |

### BackgroundConfig

| Field | Type | Description |
|-------|------|-------------|
| `backgrounds` | list[Background] | All backgrounds (flat) |
| `groupings` | list | Picker structure |

***

## Source Classes

| Class | Fields | Description |
|-------|--------|-------------|
| `PlaylistSource` | label, path, icon | Source for playlist scanning |
| `BrowseSource` | label, path, condition, visible, icon | Source for browse dialogs |
