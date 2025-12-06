# models/background.py

**Path:** `resources/lib/skinshortcuts/models/background.py`
**Lines:** 62
**Purpose:** Dataclass models for backgrounds and background selection system.

---

## Overview

Defines the Background model and supporting types for the background picker system.

---

## Enums

### BackgroundType (line 9)
Enum defining available background types.

| Value | Description |
|-------|-------------|
| `STATIC` | Single static image path |
| `PLAYLIST` | Slideshow from playlist sources |
| `BROWSE` | User browses for single image |
| `MULTI` | User browses for multiple images |
| `PROPERTY` | Path from a skin property |
| `LIVE` | Live/dynamic background |
| `LIVE_PLAYLIST` | Live background from playlist |

**Used by:** Background.type, loaders/background.py, dialog.py

---

## Classes

### PlaylistSource (line 20)
A source path for playlist scanning.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | str | required | Display label |
| `path` | str | required | Path to scan for images |
| `icon` | str | "DefaultPlaylist.png" | Icon for this source |

**Used by:** Background.sources, dialog.py (_pick_playlist)

---

### BrowseSource (line 29)
A source path for browse dialogs.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | str | required | Display label |
| `path` | str | required | Browse starting path, or "browse" for free browser |
| `condition` | str | "" | Visibility condition |
| `icon` | str | "" | Icon for this source |

**Used by:** Background.browse_sources, dialog.py

---

### Background (line 43)
A background assignable to menu items.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Unique identifier |
| `label` | str | required | Display label |
| `path` | str | "" | Static path (optional for browse/playlist types) |
| `type` | BackgroundType | STATIC | Background type |
| `icon` | str | "" | Icon path |
| `condition` | str | "" | Visibility condition |
| `sources` | list[PlaylistSource] | [] | Sources for playlist types |
| `browse_sources` | list[BrowseSource] | [] | Sources for browse/multi types |

**Methods:**
- `to_properties()` → dict[str,str] - Convert to skin property dict

**Property output example:**
```python
{
    "background": "/path/to/image.jpg",
    "backgroundLabel": "My Background",
    "backgroundType": "static"
}
```

**Used by:** config.py, dialog.py (background picker), loaders/background.py

---

## Dead Code Analysis

All classes appear to be in active use.

---

## Test Candidates

1. `BackgroundType` enum values and names
2. `Background.to_properties()` output format
3. `Background.to_properties()` type name lowercase conversion
