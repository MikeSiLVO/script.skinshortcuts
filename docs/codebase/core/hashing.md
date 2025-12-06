# hashing.py

**Path:** `resources/lib/skinshortcuts/hashing.py`
**Lines:** 152
**Purpose:** Hash utilities for rebuild detection - determines if includes.xml needs regeneration.

---

## Overview

Uses MD5 hashes of configuration files to detect changes and avoid unnecessary rebuilds. Hash file is stored per-skin in addon_data.

---

## Functions

### get_hash_file_path() → str (line 28)
Get path to hash file for current skin.

**Path format:** `special://profile/addon_data/script.skinshortcuts/{skin_dir}.hash`

**Returns:** Empty string if not in Kodi

---

### hash_file(path) → str | None (line 37)
Generate MD5 hash for a file.

**Parameters:**
- `path` - Path to file

**Returns:** MD5 hex digest or None if file doesn't exist

---

### hash_string(value) → str (line 53)
Generate MD5 hash for a string.

**Parameters:**
- `value` - String to hash

**Returns:** MD5 hex digest

---

### generate_config_hashes(shortcuts_path) → dict[str, str | None] (line 58)
Generate hashes for all config files in shortcuts folder.

**Files hashed:**
- menu.xml
- menus.xml
- widgets.xml
- backgrounds.xml
- properties.xml
- templates.xml
- userdata (from addon_data)

**Metadata included:**
- `script_version` - Addon version
- `skin_dir` - Current skin directory
- `kodi_version` - Kodi major version

---

### read_stored_hashes() → dict[str, str | None] (line 92)
Read previously stored hashes from hash file.

**Returns:** Empty dict if file doesn't exist or is invalid

---

### write_hashes(hashes) → bool (line 112)
Write hashes to file.

Creates parent directories if needed.

**Returns:** True on success

---

### needs_rebuild(shortcuts_path, output_paths=None) → bool (line 128)
Check if menu needs to be rebuilt by comparing hashes.

**Returns True if:**
- Any output file (includes.xml) is missing
- No stored hashes exist
- Any config file hash changed
- Any metadata changed (version, skin)

**Parameters:**
- `shortcuts_path` - Path to shortcuts folder
- `output_paths` - Optional list of output directories to check

**Used by:** entry.py (build_includes)

---

## Dead Code Analysis

All functions appear to be in active use.

---

## Test Candidates

1. `hash_file()` with existing and non-existing files
2. `generate_config_hashes()` with various file combinations
3. `needs_rebuild()` with missing output files
4. `needs_rebuild()` with changed config hashes
5. `write_hashes()` / `read_stored_hashes()` round-trip
