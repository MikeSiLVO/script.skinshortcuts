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

***

## BrowseProvider

Lists directory contents for browse-into functionality.

| Method | Description |
|--------|-------------|
| `list_directory(path)` | List directory contents, returns list of BrowseItem |
| `is_browsable(path)` | Check if path can be browsed |

**BrowseItem fields:** `label`, `path`, `icon`, `is_directory`, `mimetype`

***

## Content Sources

| Source | Target | Method |
|--------|--------|--------|
| `sources` | video, music, pictures | Files.GetSources |
| `playlists` | video, audio | Filesystem scan |
| `addons` | video, audio, image, program | Addons.GetAddons |
| `favourites` | - | Favourites.GetFavourites |
| `pvr` | tv, radio | PVR.GetChannels |
| `commands` | - | Static list |
| `settings` | - | Static list |
| `library` | genres, years, etc. | Database queries |
