# providers/content.py

**Path:** `resources/lib/skinshortcuts/providers/content.py`
**Lines:** 493
**Purpose:** Resolve `<content>` elements to shortcuts via Kodi's JSON-RPC API.

***

## Overview

The ContentProvider queries Kodi's JSON-RPC API and filesystem to resolve dynamic content references (sources, playlists, addons, favourites, PVR channels, commands, settings, library) into usable shortcuts.

**Note:** This module requires Kodi to run (imports xbmc, xbmcvfs).

***

## Constants

### PLAYLIST_EXTENSIONS (line 20)

Tuple of recognized playlist file extensions.

Values: `".xsp"`, `".m3u"`, `".m3u8"`, `".pls"`

**Used by:** `scan_playlist_files()`, `ContentProvider._scan_playlist_directory()`

***

## Module Functions

### scan_playlist_files(directory) → list[tuple[str, str]] (line 33)

Scan directory for playlist files.

**Parameters:**

* `directory` - Path to scan (e.g., "{playlists_base}/video/")

**Returns:** List of (label, filepath) tuples for found playlists.

**Used by:** `dialog.py._pick_playlist()`, `ContentProvider._scan_playlist_directory()`

***

## ResolvedShortcut Dataclass (line 24)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | str | required | Display label |
| `action` | str | required | Kodi action string |
| `icon` | str | "DefaultShortcut.png" | Icon path |
| `label2` | str | "" | Secondary label |

***

## ContentProvider Class (line 58)

### `__init__`() (line 61)

Initialize with empty cache.

### resolve(content) → list[ResolvedShortcut] (line 64)

Main entry point - resolve a Content object to shortcuts.

**Routes by source:**
| Source | Method | Target Values |
|--------|--------|---------------|
| `sources` | `_resolve_sources()` | video, music, pictures |
| `playlists` | `_resolve_playlists()` | video, audio |
| `addons` | `_resolve_addons()` | video, audio, image, program |
| `favourites` | `_resolve_favourites()` | - |
| `pvr` | `_resolve_pvr()` | tv, radio |
| `commands` | `_resolve_commands()` | - |
| `settings` | `_resolve_settings()` | - |
| `library` | `_resolve_library()` | genres, years, studios, tags, actors, directors, artists, albums |
| `nodes` | `_resolve_nodes()` | video, music |

### clear_cache() (line 98)

Clear the content cache.

***

## Resolver Methods

### `_resolve_sources`(target) (line 106)

Resolve media sources via `Files.GetSources`.

**Actions:** `ActivateWindow(Videos|Music|Pictures, path, return)`

**Icons:** DefaultFolder.png

***

### `_get_playlists_base_path`() → str (line 157)

Get the playlist base path from Kodi's `system.playlistspath` setting.

**Returns:** User-configured path or default `special://profile/playlists/`

***

### `_resolve_playlists`(target, custom_path="") (line 175)

Resolve playlists from standard or custom paths.

**Default paths (from Kodi settings):**

* video: `{base}/video/` and `{base}/mixed/`
* audio: `{base}/music/` and `{base}/mixed/`

**File types:** .xsp, .m3u, .m3u8, .pls

**Actions:** `ActivateWindow(Videos|Music, filepath, return)`

***

### `_scan_playlist_directory`(directory, default_window) (line 190)

Convert playlist files to ResolvedShortcut objects.

Uses `scan_playlist_files()` for scanning, then determines correct window for .xsp files.

***

### `_parse_smart_playlist`(filepath) (line 217)

Parse .xsp file to extract playlist type and display name.

**Returns:** Tuple of (type, name) where:

* `type` is the playlist type attribute (video, music, etc.)
* `name` is from the `<name>` element inside the .xsp file (used for display instead of filename)

***

### `_resolve_addons`(target) (line 236)

Resolve installed addons via `Addons.GetAddons`.

**Actions:** `RunAddon(addon_id)`

**Icons:** Addon thumbnail or DefaultAddon.png

***

### `_resolve_favourites`() (line 290)

Resolve user favourites via `Favourites.GetFavourites`.

**Favourite types and actions:**
| Type | Action |
|------|--------|
| media | `PlayMedia(path)` |
| window | `ActivateWindow(window, param, return)` |
| script | `RunScript(path)` |
| androidapp | `StartAndroidActivity(path)` |

***

### `_resolve_pvr`(target) (line 348)

Resolve PVR channels via `PVR.GetChannels`.

**Requires:** `Pvr.HasTVChannels` or `Pvr.HasRadioChannels`

**Actions:** `PlayPvrChannel(channel_id)`

***

### `_resolve_commands`() (line 401)

Return static list of system commands.

| Label | Action |
|-------|--------|
| $LOCALIZE[13012] (Quit) | `Quit()` |
| $LOCALIZE[13005] (Reboot) | `Reboot()` |
| $LOCALIZE[13009] (Power off) | `Powerdown()` |
| $LOCALIZE[13014] (Suspend) | `Suspend()` |
| $LOCALIZE[13015] (Hibernate) | `Hibernate()` |
| $LOCALIZE[13016] (Restart) | `RestartApp()` |
| $LOCALIZE[20183] (Reload skin) | `ReloadSkin()` |

***

### `_resolve_settings`() (line 457)

Return static list of settings shortcuts.

| Label | Action |
|-------|--------|
| $LOCALIZE[10004] (Settings) | `ActivateWindow(Settings)` |
| $LOCALIZE[10035] (Skin Settings) | `ActivateWindow(SkinSettings)` |
| $LOCALIZE[14201] (Player settings) | `ActivateWindow(PlayerSettings)` |
| $LOCALIZE[14212] (Media settings) | `ActivateWindow(MediaSettings)` |
| $LOCALIZE[14205] (PVR & Live TV settings) | `ActivateWindow(PVRSettings)` |
| $LOCALIZE[14208] (Service settings) | `ActivateWindow(ServiceSettings)` |
| $LOCALIZE[10022] (Settings - Games) | `ActivateWindow(GameSettings)` |
| $LOCALIZE[14207] (Interface settings) | `ActivateWindow(InterfaceSettings)` |
| $LOCALIZE[14210] (Profile settings) | `ActivateWindow(Profiles)` |
| $LOCALIZE[14209] (System settings) | `ActivateWindow(SystemSettings)` |
| $LOCALIZE[10040] (Add-on browser) | `ActivateWindow(AddonBrowser)` |
| $LOCALIZE[10003] (File manager) | `ActivateWindow(FileManager)` |

***

### `_resolve_nodes`(target) (line 456)

Resolve library navigation nodes from XML files in `special://xbmc/system/library/{type}/`.

**Parses:** `index.xml` files for label, icon, and order attributes.

**Actions:** `ActivateWindow(Videos|Music, library://{type}/{node}/, return)`

***

### `_parse_library_node`(filepath) (line 490)

Parse a library node index.xml file to extract label, icon, and order.

**Returns:** Tuple of (label, icon, order) or (None, None, 999) on error.

***

### `_resolve_library`(target) (line 510)

Resolve library database content (genres, years, studios, tags, actors, etc.).

**Target values:**
| Target | Method | Description |
|--------|--------|-------------|
| `genres`, `moviegenres` | `_get_video_genres("movie")` | Movie genres |
| `tvgenres` | `_get_video_genres("tvshow")` | TV show genres |
| `musicgenres` | `_get_music_genres()` | Music genres |
| `years`, `movieyears` | `_get_video_years("movie")` | Movie years |
| `tvyears` | `_get_video_years("tvshow")` | TV show years |
| `studios`, `moviestudios` | `_get_video_property("movie", "studio")` | Movie studios |
| `tvstudios` | `_get_video_property("tvshow", "studio")` | TV studios |
| `tags`, `movietags` | `_get_video_property("movie", "tag")` | Movie tags |
| `tvtags` | `_get_video_property("tvshow", "tag")` | TV tags |
| `actors`, `movieactors` | `_get_video_actors("movie")` | Movie actors |
| `tvactors` | `_get_video_actors("tvshow")` | TV actors |
| `directors`, `moviedirectors` | `_get_video_directors("movie")` | Movie directors |
| `tvdirectors` | `_get_video_directors("tvshow")` | TV directors |
| `artists` | `_get_music_artists()` | Music artists |
| `albums` | `_get_music_albums()` | Music albums |

***

### `_jsonrpc`(method, params=None) (line 773)

Execute a JSON-RPC request to Kodi.

Logs warnings/errors on failure.

***

### resolve_content(content) (line 484)

Convenience function using module-level singleton.

**Used by:** dialog.py (shortcut picker)

***

### clear_content_cache() (line 495)

Clear the content provider cache.

Called when opening the management dialog to ensure fresh data (e.g., newly added favourites are visible in the picker).

**Used by:** dialog/base.py (onInit)

***

## Dead Code Analysis

All code appears to be in active use.

***

## Test Candidates

1. `resolve()` routing by source type
2. `_resolve_playlists()` with custom path
3. `_get_smart_playlist_type()` XML parsing
4. `_resolve_favourites()` action building for each type
5. `_jsonrpc()` error handling

**Note:** Most tests require mocking Kodi APIs.
