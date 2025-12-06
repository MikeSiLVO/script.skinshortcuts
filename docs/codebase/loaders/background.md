# loaders/background.py

**Path:** `resources/lib/skinshortcuts/loaders/background.py`
**Lines:** 99
**Purpose:** Load background configuration from backgrounds.xml.

---

## Overview

Parses the `backgrounds.xml` file which contains background definitions for the background picker dialog.

---

## Constants

### TYPE_MAP (line 11)
Maps string type names to BackgroundType enum values.

| String | Enum |
|--------|------|
| `"static"` | STATIC |
| `"playlist"` | PLAYLIST |
| `"browse"` | BROWSE |
| `"multi"` | MULTI |
| `"property"` | PROPERTY |
| `"live"` | LIVE |
| `"live-playlist"` | LIVE_PLAYLIST |

---

### OPTIONAL_PATH_TYPES (line 22)
Background types where `<path>` is optional (user selects at runtime).

Values: `BROWSE`, `MULTI`, `PLAYLIST`, `LIVE_PLAYLIST`

---

## Public Functions

### load_backgrounds(path) (line 30)
Load backgrounds from XML file.

**Parameters:**
- `path` - Path to backgrounds.xml

**Returns:** list[Background]

**Used by:** config.py (SkinConfig.load)

---

## Internal Functions

### _parse_background(elem, path) (line 46)
Parse a background element.

**Required:**
- `name` attribute
- `label` attribute
- `<path>` child (unless type is in OPTIONAL_PATH_TYPES)

**Optional:**
- `type` attribute (default: "static")
- `<icon>`, `<condition>` children
- `<source>` children

**Source parsing depends on type:**
- BROWSE, MULTI → BrowseSource (with condition)
- PLAYLIST, LIVE_PLAYLIST → PlaylistSource

**Raises:** BackgroundConfigError if missing required fields

---

## XML Schema

```xml
<backgrounds>
  <!-- Static background -->
  <background name="default" label="Default" type="static">
    <path>special://skin/backgrounds/default.jpg</path>
    <icon>special://skin/backgrounds/default_thumb.jpg</icon>
  </background>

  <!-- Browse for single image -->
  <background name="custom" label="Custom Image" type="browse">
    <source label="Pictures" condition="...">special://pictures/</source>
    <source label="Browse...">browse</source>
  </background>

  <!-- Playlist slideshow -->
  <background name="slideshow" label="Slideshow" type="playlist">
    <source label="Pictures">special://pictures/</source>
    <source label="Skin Images">special://skin/backgrounds/</source>
  </background>
</backgrounds>
```

---

## Dead Code Analysis

All code appears to be in active use.

---

## Test Candidates

1. `load_backgrounds()` with various background types
2. `_parse_background()` path validation by type
3. Source parsing for browse vs playlist types
4. TYPE_MAP with unknown type (defaults to STATIC)
