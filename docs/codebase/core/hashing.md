# hashing.py

**Path:** `resources/lib/skinshortcuts/hashing.py`
**Purpose:** Hash utilities for rebuild detection.

***

## Overview

Uses MD5 hashes of configuration files to detect changes and avoid unnecessary rebuilds.

**Storage:** `special://profile/addon_data/script.skinshortcuts/{skin_dir}.hash`

***

## Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `get_hash_file_path()` | str | Path to hash file for current skin |
| `hash_file(path)` | str | MD5 hash of file |
| `hash_string(value)` | str | MD5 hash of string |
| `generate_config_hashes(shortcuts_path)` | dict | Hashes for all config files + metadata |
| `read_stored_hashes()` | dict | Load stored hashes |
| `write_hashes(hashes)` | bool | Save hashes |
| `needs_rebuild(shortcuts_path, output_paths)` | bool | Check if rebuild needed |

### needs_rebuild()

Returns True if:
- Any output file (includes.xml) is missing
- No stored hashes exist
- Any config file hash changed
- Metadata changed (version, skin)
