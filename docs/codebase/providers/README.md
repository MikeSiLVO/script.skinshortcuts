# providers/ Package

**Path:** `resources/lib/skinshortcuts/providers/`
**Purpose:** Dynamic content resolution via Kodi APIs.

***

## Overview

The providers package resolves `<content>` references in configuration files to actual shortcuts and widgets at runtime. It queries Kodi's JSON-RPC API and filesystem to get current sources, playlists, addons, favourites, etc.

***

## Modules

| File | Doc | Lines | Purpose |
|------|-----|-------|---------|
| `__init__.py` | | ~10 | Re-exports public API |
| `content.py` | [providers-content.md](providers-content.md) | 493 | Content resolver |

***

## Public API

### Functions

* `resolve_content(content)` - Resolve a Content object to shortcuts (uses singleton)
* `scan_playlist_files(directory)` - Scan directory for playlist files

### Classes

* `ContentProvider` - Main resolver class
* `ResolvedShortcut` - Dataclass for resolved shortcut data

***

## Content Sources

The ContentProvider resolves these source types:

| Source | Target | Method |
|--------|--------|--------|
| `sources` | video, music, pictures | JSON-RPC `Files.GetSources` |
| `playlists` | video, audio | Filesystem scan |
| `addons` | video, audio, image, program | JSON-RPC `Addons.GetAddons` |
| `favourites` | - | JSON-RPC `Favourites.GetFavourites` |
| `pvr` | tv, radio | JSON-RPC `PVR.GetChannels` |
| `commands` | - | Static list (Quit, Reboot, etc.) |
| `settings` | - | Static list (Settings windows) |

***

## Usage Pattern

```python
from skinshortcuts.providers import resolve_content, scan_playlist_files
from skinshortcuts.models import Content

# Resolve dynamic content
content = Content(source="addons", target="videos")
shortcuts = resolve_content(content)

# Scan for playlists (from profile playlists folder)
playlists = scan_playlist_files("special://profile/playlists/video/")
for label, path in playlists:
    print(f"{label}: {path}")
```

***

## Caching

ContentProvider maintains an internal cache to avoid repeated API calls. Use `provider.clear_cache()` if fresh data is needed.
