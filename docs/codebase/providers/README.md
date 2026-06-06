# providers/ Package

**Path:** `resources/lib/skinshortcuts/providers/`
**Purpose:** Dynamic content resolution via Kodi APIs.

***

## Overview

Resolves `<content>` references to shortcuts at runtime by querying Kodi JSON-RPC API and filesystem. Also provides directory browsing for addon navigation.

***

## Modules

| File | Doc | Purpose |
|------|-----|---------|
| `content.py` | [content.md](content.md) | Content resolver |
| `browse.py` | - | Directory browsing via Files.GetDirectory |

***

## Public API

| Function | Description |
|----------|-------------|
| `resolve_content(content)` | Resolve Content to shortcuts |
| `scan_playlist_files(directory)` | Scan for playlist files |
| `get_browse_provider()` | Get BrowseProvider instance |
| `clear_content_cache()` | Clear cached content results (call on opening management dialog) |

***

## BrowseProvider

Lists directory contents for browse-into functionality.

| Method | Description |
|--------|-------------|
| `list_directory(path, include_art=False)` | List directory contents; returns list of BrowseItem, empty list for empty dirs, or None if path is not listable |

**BrowseItem fields:** `label`, `path`, `icon`, `is_directory`, `mimetype`

***

## Content Sources

| Source | Target | Method |
|--------|--------|--------|
| `sources` | video, music, pictures, files, programs | Files.GetSources |
| `playlists` | video, music | Filesystem scan |
| `addons` | video, audio, image, executable, game | Addons.GetAddons |
| `favourites` | - | Favourites.GetFavourites |
| `pvr` | tv, radio | PVR.GetChannels |
| `commands` | - | Static list |
| `settings` | - | Static list |
| `library` | genres, years, etc. | Database queries |
| `nodes` | video, music (library/all/empty = both) | Files.GetDirectory (library nodes) |
