# models/background.py

**Path:** `resources/lib/skinshortcuts/models/background.py`

Dataclass models for backgrounds and background groupings.

***

## Overview

Defines the Background model and related grouping structures for the background picker system.

***

## Type Alias

```python
BackgroundGroupContent = Union[Background, BackgroundGroup, Content]
```

Items that can appear in a BackgroundGroup's items list.

***

## Enums

### BackgroundType

Enum defining available background types.

| Value | Description |
|-------|-------------|
| `STATIC` | Single static image path |
| `PLAYLIST` | Slideshow from playlist sources |
| `BROWSE` | User browses for single image |
| `MULTI` | User browses for multiple images (folder) |
| `PROPERTY` | Path from Kodi info label |
| `LIVE` | Dynamic content from library |
| `LIVE_PLAYLIST` | Dynamic content from user-selected playlist |

**Used by:** Background.type, loaders/background.py, dialog/properties.py

***

## Classes

### PlaylistSource

A source path for playlist scanning.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | str | required | Display label |
| `path` | str | required | Path to scan for images |
| `icon` | str | `"DefaultPlaylist.png"` | Icon for this source |

**Used by:** Background.sources, dialog/properties.py

***

### BrowseSource

A source path for browse dialogs.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | str | required | Display label |
| `path` | str | required | Browse starting path, or `"browse"` for free browser |
| `condition` | str | `""` | Property condition (evaluated against item properties) |
| `visible` | str | `""` | Kodi visibility condition (evaluated at runtime) |
| `icon` | str | `""` | Icon for this source |

**Used by:** Background.browse_sources, dialog/properties.py

***

### Background

A background assignable to menu items.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Unique identifier |
| `label` | str | required | Display label |
| `path` | str | `""` | Image path (optional for browse/multi/playlist types) |
| `type` | BackgroundType | `STATIC` | Background type |
| `icon` | str | `""` | Icon path |
| `condition` | str | `""` | Property condition (evaluated against item properties) |
| `visible` | str | `""` | Kodi visibility condition (evaluated at runtime) |
| `sources` | list[PlaylistSource] | `[]` | Sources for playlist types |
| `browse_sources` | list[BrowseSource] | `[]` | Sources for browse/multi types |

**Properties:**

| Property | Returns | Description |
|----------|---------|-------------|
| `type_name` | str | Normalized type name (e.g., `"live-playlist"` not `"live_playlist"`) |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `to_properties()` | dict[str, str] | Convert to skin property dict |

**Property output from `to_properties()`:**

```python
{
    "background": "my-background",
    "backgroundPath": "/path/to/image.jpg",
    "backgroundLabel": "My Background",
    "backgroundType": "live-playlist"  # normalized with hyphen
}
```

**Used by:** config.py, dialog/properties.py

***

### BackgroundGroup

A group/category in background picker.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Unique identifier |
| `label` | str | required | Display label |
| `condition` | str | `""` | Property condition (evaluated against item properties) |
| `visible` | str | `""` | Kodi visibility condition (evaluated at runtime) |
| `icon` | str | `""` | Icon for picker display |
| `items` | list[BackgroundGroupContent] | `[]` | Child items: Background, BackgroundGroup, or Content |

**Used by:** BackgroundConfig, dialog/properties.py, loaders/background.py

***

### BackgroundConfig

Top-level background configuration container.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `backgrounds` | list[Background] | `[]` | All defined backgrounds (flat list) |
| `groupings` | list[BackgroundGroup \| Background] | `[]` | Picker structure (can include standalone backgrounds) |

**Used by:** config.py, loaders/background.py

***

## Test Candidates

1. `BackgroundType` enum values and names
2. `Background.type_name` property normalization
3. `Background.to_properties()` output format
