# loaders/background.py

**Path:** `resources/lib/skinshortcuts/loaders/background.py`
**Lines:** 162
**Purpose:** Load background configuration from backgrounds.xml.

---

## Overview

Parses the `backgrounds.xml` file which contains background definitions and groups for the background picker dialog. Backgrounds and groups are defined directly at the root level.

---

## Constants

### TYPE_MAP (line 18)
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

### OPTIONAL_PATH_TYPES (line 29)
Background types where `<path>` is optional (user selects at runtime).

Values: `BROWSE`, `MULTI`, `PLAYLIST`, `LIVE_PLAYLIST`

---

## Public Functions

### load_backgrounds(path) (line 37)
Load complete background configuration from XML file.

Parses `<background>` and `<group>` elements directly from root `<backgrounds>` element.
Backgrounds at root level appear flat in picker, groups create nested navigation.

**Parameters:**
- `path` - Path to backgrounds.xml

**Returns:** BackgroundConfig containing:
- `backgrounds` - Flat list of all Background objects (root-level only)
- `groupings` - List of backgrounds and groups for picker (includes both)

**Used by:** config.py (SkinConfig.load), dialog/properties.py

---

## Internal Functions

### _parse_background(elem, path) (line 72)
Parse a background element.

**Required:**
- `name` attribute
- `label` attribute
- `<path>` child (unless type is in OPTIONAL_PATH_TYPES)

**Attributes:**
- `name`, `label` - Required
- `type` - Optional (default: "static")
- `condition`, `visible` - Optional

**Child Elements:**
- `<path>` - Required (except for OPTIONAL_PATH_TYPES)
- `<icon>` - Optional
- `<source>` - Optional (multiple allowed)

**Source parsing depends on type:**
- BROWSE, MULTI → BrowseSource (with condition, icon)
- PLAYLIST, LIVE_PLAYLIST → PlaylistSource (with icon)

**Raises:** BackgroundConfigError if missing required fields

---

### _parse_background_group(elem, path) (line 128)
Parse a background group element.

**Required:**
- `name` attribute
- `label` attribute

**Optional:**
- `condition` attribute - Property condition
- `visible` attribute - Kodi visibility condition
- `icon` attribute - Icon for picker display

**Children parsed in document order:**
- `<background>` → Background
- `<group>` → BackgroundGroup (recursive)
- `<content>` → Content

---

## XML Schema

```xml
<backgrounds>
  <!-- Flat background at root level -->
  <background name="default" label="Default" type="static">
    <path>special://skin/backgrounds/default.jpg</path>
    <icon>special://skin/backgrounds/default_thumb.jpg</icon>
  </background>

  <!-- Browse for single image -->
  <background name="custom" label="Custom Image" type="browse">
    <source label="Pictures" condition="...">special://pictures/</source>
    <source label="Browse...">browse</source>
  </background>

  <!-- Group with nested backgrounds -->
  <group name="library" label="Library Fanart" icon="DefaultVideo.png" visible="Library.HasContent(movies)">
    <background name="movie-fanart" label="Movie Fanart" type="property">
      <path>$INFO[Window(Home).Property(MovieFanart)]</path>
    </background>

    <!-- Nested group -->
    <group name="live" label="Live Backgrounds">
      <background name="random-movies" label="Random Movies" type="live">
        <path>random movies</path>
      </background>
    </group>
  </group>

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

1. `load_backgrounds()` with complete backgrounds.xml
2. `_parse_background()` path validation by type
3. Source parsing for browse vs playlist types
4. TYPE_MAP with unknown type (defaults to STATIC)
5. `_parse_background_group()` with nested groups
6. Mixed groups and backgrounds at root level
