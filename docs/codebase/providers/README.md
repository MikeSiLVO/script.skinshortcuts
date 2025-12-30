# providers/ Package

**Path:** `resources/lib/skinshortcuts/providers/`
**Purpose:** Dynamic content resolution via Kodi APIs.

***

## Overview

Resolves `<content>` references to shortcuts at runtime by querying Kodi JSON-RPC API and filesystem.

***

## Modules

| File | Doc | Purpose |
|------|-----|---------|
| `content.py` | [content.md](content.md) | Content resolver |

***

## Public API

| Function | Description |
|----------|-------------|
| `resolve_content(content)` | Resolve Content to shortcuts |
| `scan_playlist_files(directory)` | Scan for playlist files |

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
