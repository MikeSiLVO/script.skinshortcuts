# entry.py

**Path:** `resources/lib/skinshortcuts/entry.py`
**Lines:** 338
**Purpose:** Entry point for RunScript - handles all script invocations.

---

## Overview

This is the main entry point when the addon is invoked via `RunScript(script.skinshortcuts,...)`. It parses arguments and routes to the appropriate action.

---

## Helper Functions

### log(msg, level=0) (line 25)
Log message to Kodi log or stdout.

Uses `xbmc.log()` in Kodi, `print()` outside.

### get_skin_path() → str (line 33)
Get current skin's shortcuts folder path.

**Path:** `special://skin/shortcuts/`

### get_output_paths() → list[str] (line 41)
Get paths for includes.xml output by parsing skin's addon.xml.

Parses `<res folder="...">` elements to find all resolution folders.

---

## Action Functions

### build_includes(shortcuts_path=None, output_path=None, force=False) → bool (line 72)
Build includes.xml from skin config files.

**Parameters:**
- `shortcuts_path` - Path to shortcuts folder (auto-detected if None)
- `output_path` - Path to write includes.xml (auto-detected if None)
- `force` - Force rebuild even if hashes match

**Process:**
1. Check if menu.xml or menus.xml exists
2. Check if rebuild is needed (unless force=True)
3. Load SkinConfig (with userdata)
4. Build includes.xml to all resolution folders
5. Save config hashes
6. Reload skin

**Returns:** True if built successfully

---

### clear_custom_menu(menu, property_name="", shortcuts_path=None) → bool (line 159)
Clear a custom widget menu and optionally reset a property.

**Parameters:**
- `menu` - Custom menu name (e.g., "movies.customwidget")
- `property_name` - Optional property to clear on parent item
- `shortcuts_path` - Path to shortcuts folder

**Behavior:**
1. Clear all items from the custom menu
2. If property_name specified, clear widget properties on parent item
3. Save changes and rebuild includes

**Used by:** RunScript action type="clear"

---

### reset_all_menus(shortcuts_path=None) → bool (line 244)
Reset all menus to skin defaults by deleting skin's userdata.

Shows confirmation dialog before proceeding.

**Used by:** RunScript action type="resetall"

---

## Main Entry Point

### main() (line 285)
Main entry point for RunScript.

**Argument parsing:**
- Accepts `?param=value` or `param=value` format
- Parses with `urllib.parse.parse_qs()`

**Actions (type parameter):**

| Type | Description |
|------|-------------|
| `buildxml` (default) | Build includes.xml |
| `manage` | Open management dialog |
| `resetall` | Reset to skin defaults |
| `clear` | Clear custom widget menu |

**Parameters by action:**

**buildxml:**
- `path` - Shortcuts path
- `output` - Output path
- `force` - Force rebuild

**manage:**
- `menu` - Menu ID (default: "mainmenu")
- `path` - Shortcuts path

**clear:**
- `menu` - Custom menu name
- `property` - Property to clear

---

## Dead Code Analysis

All code appears to be in active use.

---

## Test Candidates

1. `build_includes()` hash-based skip logic
2. `build_includes()` multi-resolution output
3. `clear_custom_menu()` parent property clearing
4. `main()` argument parsing
5. `get_output_paths()` addon.xml parsing

**Note:** Most tests require mocking Kodi APIs.
