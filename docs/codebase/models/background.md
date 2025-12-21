# models/background.py

**Path:** `resources/lib/skinshortcuts/models/background.py`
**Lines:** 96
**Purpose:** Dataclass models for backgrounds and background groupings.

***

## Overview

Defines the Background model and related grouping structures for the background picker system.

***

## Type Alias

```python
BackgroundGroupContent = Union[Background, BackgroundGroup, Content]  # line 15
```

Items that can appear in a BackgroundGroup's items list.

***

## Enums

### BackgroundType (line 18)

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

**Used by:** Background.type, loaders/background.py, dialog.py

***

## Classes

### PlaylistSource (line 28)

A source path for playlist scanning.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | str | required | Display label |
| `path` | str | required | Path to scan for images |
| `icon` | str | "DefaultPlaylist.png" | Icon for this source |

**Used by:** Background.sources, dialog.py (_pick_playlist)

***

### BrowseSource (line 37)

A source path for browse dialogs.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | str | required | Display label |
| `path` | str | required | Browse starting path, or "browse" for free browser |
| `condition` | str | "" | Property condition (evaluated against item properties) |
| `visible` | str | "" | Kodi visibility condition (evaluated at runtime) |
| `icon` | str | "" | Icon for this source |

**Used by:** Background.browse_sources, dialog/items.py, dialog/properties.py

***

### Background (line 51)

A background assignable to menu items.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Unique identifier |
| `label` | str | required | Display label |
| `path` | str | "" | Image path (optional for browse/multi/playlist types) |
| `type` | BackgroundType | STATIC | Background type |
| `icon` | str | "" | Icon path |
| `condition` | str | "" | Property condition (evaluated against item properties) |
| `visible` | str | "" | Kodi visibility condition (evaluated at runtime) |
| `sources` | list[PlaylistSource] | [] | Sources for playlist types |
| `browse_sources` | list[BrowseSource] | [] | Sources for browse/multi types |

**Methods:**

* `to_properties()` → dict[str,str] - Convert to skin property dict

**Property output:**

```python
{
    "background": "my-background",
    "backgroundPath": "/path/to/image.jpg",
    "backgroundLabel": "My Background",
    "backgroundType": "static"
}
```

**Used by:** config.py, dialog.py (background picker), builders/includes.py

***

### BackgroundGroup (line 74)

A group/category in background picker.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Unique identifier |
| `label` | str | required | Display label |
| `condition` | str | "" | Property condition (evaluated against item properties) |
| `visible` | str | "" | Kodi visibility condition (evaluated at runtime) |
| `icon` | str | "" | Icon for picker display |
| `items` | list[BackgroundGroupContent] | [] | Child items: Background, BackgroundGroup, or Content |

**Used by:** BackgroundConfig, dialog.py (_pick_background_from_groups), loaders/background.py

***

### BackgroundConfig (line 86)

Top-level background configuration container.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `backgrounds` | list[Background] | [] | All defined backgrounds (flat list) |
| `groupings` | list[BackgroundGroup|Background] | [] | Picker structure (can include standalone backgrounds) |

**Used by:** config.py (SkinConfig._background_config), loaders/background.py

***

## Dead Code Analysis

All classes appear to be in active use.

***

## Test Candidates

1. `BackgroundType` enum values and names
2. `Background.to_properties()` output format
3. `Background.to_properties()` type name lowercase conversion
