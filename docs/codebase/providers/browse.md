# providers/browse.py

**Path:** `resources/lib/skinshortcuts/providers/browse.py`
**Purpose:** List Kodi directory contents for the browse-into picker.

***

## Overview

Wraps the `Files.GetDirectory` JSON-RPC method to enumerate a path's
contents and classify each entry as browsable (directory) or selectable
(file). Used by the shortcut picker's browse-into flow to let the user
navigate plugin, library, and filesystem paths.

**Note:** Requires Kodi runtime (imports xbmc).

***

## Public API

### get_browse_provider() -> BrowseProvider

Return the module-level singleton, creating it on first call.

***

## BrowseItem Dataclass

One entry from a directory listing.

| Field | Type | Description |
|-------|------|-------------|
| `label` | str | Display label |
| `path` | str | Item path (`file` field from JSON-RPC) |
| `icon` | str | Resolved icon path |
| `is_directory` | bool | True if the entry is a directory |
| `mimetype` | str | MIME type, empty when unknown |

***

## BrowseProvider Class

### __init__(icon_overrides=None)

Store an optional `{icon: replacement}` map. Empty map when omitted.

### set_icon_overrides(overrides)

Replace the override map. Exists so the singleton can be refreshed with
the skin's current overrides before each browse session.

### list_directory(path, include_art=False) -> list[BrowseItem] | None

List the contents of `path` (plugin://, videodb://, library://, source
paths, etc.).

- `include_art` adds `art` to the requested properties so each
  `BrowseItem.icon` reflects the item's specific imagery. Left False
  for large or plain-text listings, since fetching art for tens of
  thousands of library items is slow.

Returns:

- list of `BrowseItem` for a populated directory
- empty list when the result has no `files` key (empty directory)
- `None` when the path is not listable (JSON-RPC returned no result)

Entries with an empty `file` path are skipped.

Icon selection per item:

1. When `include_art` is set, prefer `art.poster`, then `art.thumb`,
   then the item `thumbnail`. `art.icon` is ignored because it is always
   the generic Kodi default.
2. Otherwise (or when no art was found) fall back to
   `_get_icon_for_item`, then apply the override map.

***

## Internal Methods

| Method | Purpose |
|--------|---------|
| `_get_icon_for_item(file_info, filetype)` | Pick a default icon by item type, then directory, then MIME prefix, then `DefaultFile.png` |
| `_jsonrpc(method, params)` | Execute a JSON-RPC request; return `result`, or `None` on error/exception |

### _get_icon_for_item resolution order

1. `file_info["type"]` matched against `_TYPE_DEFAULTS` (movie, tvshow,
   season, episode, musicvideo, album, artist, song, genre).
2. `DefaultFolder.png` when `filetype == "directory"`.
3. MIME prefix: `video/` -> `DefaultVideo.png`, `audio/` ->
   `DefaultAudio.png`, `image/` -> `DefaultPicture.png`.
4. `DefaultFile.png` otherwise.

***

## Data Flow

`dialog/pickers.py` drives the browse-into loop:

1. Calls `get_browse_provider()` and `set_icon_overrides(...)` with the
   skin's icon overrides.
2. Calls `list_directory(current_path, include_art=True)` per level.
3. `None` triggers a "not listable" notification and aborts.
4. Each `BrowseItem` becomes a list entry; `is_directory` items get a
   `>` suffix and navigate deeper, files and "Use this location" return
   `(path, label, icon)`.

The provider is also re-exported from `providers/__init__.py` alongside
`BrowseItem` and `BrowseProvider`.
