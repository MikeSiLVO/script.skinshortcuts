# providers/content.py

**Path:** `resources/lib/skinshortcuts/providers/content.py`
**Purpose:** Resolve `<content>` elements to shortcuts via Kodi JSON-RPC API.

***

## Overview

Queries Kodi APIs and filesystem to resolve dynamic content references into shortcuts. Used by the shortcut picker dialog.

**Note:** Requires Kodi runtime (imports xbmc, xbmcvfs).

***

## Public API

### resolve_content(content) → list[ResolvedShortcut]

Module-level convenience function using singleton ContentProvider.

### clear_content_cache()

Clear cached results. Called when opening management dialog to ensure fresh data.

### scan_playlist_files(directory) → list[tuple[str, str]]

Scan directory for playlist files (.xsp, .m3u, .m3u8, .pls). Returns (label, filepath) tuples.

***

## ResolvedShortcut Dataclass

| Field | Type | Description |
|-------|------|-------------|
| `label` | str | Display label |
| `action` | str | Primary action (ActivateWindow) |
| `icon` | str | Icon path |
| `label2` | str | Secondary label |
| `action_play` | str | PlayMedia action (playlists) |
| `action_party` | str | Party mode action (music playlists) |

When `action_play` is set, picker offers choice between display/play/party modes.

***

## ContentProvider Class

### resolve(content) → list[ResolvedShortcut]

Routes by `content.source`:

| Source | Targets | Description |
|--------|---------|-------------|
| `sources` | video, music, pictures | Media sources via Files.GetSources |
| `playlists` | video, audio | Playlist files from configured paths |
| `addons` | video, audio, image, program | Installed addons via Addons.GetAddons |
| `favourites` | - | User favourites via Favourites.GetFavourites |
| `pvr` | tv, radio | PVR channels via PVR.GetChannels |
| `commands` | - | System commands (quit, reboot, etc.) |
| `settings` | - | Settings window shortcuts |
| `library` | genres, years, studios, tags, actors, directors, artists, albums | Library database content |
| `nodes` | video, music | Library navigation nodes from XML |

### clear_cache()

Clear internal cache.

***

## Internal Methods

| Method | Purpose |
|--------|---------|
| `_resolve_sources` | Media sources |
| `_resolve_playlists` | Playlist files with type filtering |
| `_resolve_addons` | Installed addons by type |
| `_resolve_favourites` | User favourites (handles media/window/script/androidapp types) |
| `_resolve_pvr` | PVR channels |
| `_resolve_commands` | Static system commands list |
| `_resolve_settings` | Static settings shortcuts list |
| `_resolve_library` | Library database queries (genres, years, etc.) |
| `_resolve_nodes` | Parse library node XML files |
| `_jsonrpc` | Execute JSON-RPC request with error handling |

***

## Library Target Values

The `library` source supports these targets:

| Target | Aliases | Description |
|--------|---------|-------------|
| `genres` | `moviegenres` | Movie genres |
| `tvgenres` | - | TV show genres |
| `musicgenres` | - | Music genres |
| `years` | `movieyears` | Movie years |
| `tvyears` | - | TV show years |
| `studios` | `moviestudios` | Movie studios |
| `tvstudios` | - | TV studios |
| `tags` | `movietags` | Movie tags |
| `tvtags` | - | TV tags |
| `actors` | `movieactors` | Movie actors |
| `tvactors` | - | TV actors |
| `directors` | `moviedirectors` | Movie directors |
| `tvdirectors` | - | TV directors |
| `artists` | - | Music artists |
| `albums` | - | Music albums |
