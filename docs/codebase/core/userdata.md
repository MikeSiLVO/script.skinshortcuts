# userdata.py

**Path:** `resources/lib/skinshortcuts/userdata.py`
**Lines:** 256
**Purpose:** User customization storage and merging with skin defaults.

---

## Overview

Stores user modifications to menus in JSON format. Provides merging logic to combine skin defaults with user overrides, supporting label changes, action changes, property changes, reordering, additions, and deletions.

**Storage format:** JSON file at `special://profile/addon_data/script.skinshortcuts/{skin_dir}.userdata.json`

---

## Functions

### get_userdata_path() → str (line 21)
Get path to userdata file for current skin.

**Returns:** Empty string if not in Kodi

---

### load_userdata(path=None) → UserData (line 94)
Load user data from JSON file.

**Parameters:**
- `path` - Optional custom path (for testing)

**Returns:** UserData object (empty if file doesn't exist)

---

### save_userdata(userdata, path=None) → bool (line 143)
Save user data to JSON file.

Creates parent directories if needed.

**Returns:** True on success

---

## Serialization Helpers

### _menu_override_to_dict(override) → dict (line 52)
Convert MenuOverride to dict, omitting empty values.

Only includes `items` and `removed` if non-empty.

### _item_override_to_dict(item) → dict (line 62)
Convert MenuItemOverride to dict, omitting None/empty values.

Only includes fields that have values set (non-None, non-empty).

---

### merge_menu(default_menu, override) → Menu (line 161)
Merge default menu with user overrides.

**Merge logic:**
1. Start with default items, excluding removed ones
2. Apply overrides to existing items
3. Add new user items
4. Reorder based on position values

**Returns:** New Menu with merged items

**Used by:** config.py (SkinConfig.load), manager.py

---

### _apply_override(item, override) → MenuItem (line 229)
Apply user override to a menu item.

**Applied fields (if not None):**
- label
- actions
- icon
- disabled
- properties (merged, override wins)

**Preserved fields:**
- name, label2, thumb, visible, required, protection, submenu

**Special:** Stores `original_action` for protection matching.

---

### _create_item_from_override(override) → MenuItem (line 248)
Create a new menu item from user override.

**Used for:** is_new=True items (user-added)

**Defaults:**
- actions = [Action(action="noop")] if not specified
- icon = "DefaultShortcut.png" if not specified

---

## Dataclasses

### MenuItemOverride (line 31)
User override for a single menu item.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Item identifier |
| `label` | str\|None | None | Override label |
| `actions` | list[Action]\|None | None | Override actions |
| `icon` | str\|None | None | Override icon |
| `disabled` | bool\|None | None | Override disabled state |
| `properties` | dict[str,str] | {} | Override properties |
| `position` | int\|None | None | Desired position in menu |
| `is_new` | bool | False | True if user-added item |

---

### MenuOverride (line 45)
User overrides for a menu.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `items` | list[MenuItemOverride] | [] | Item overrides |
| `removed` | list[str] | [] | Names of removed items |

---

### UserData (line 53)
All user customizations for a skin.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `menus` | dict[str, MenuOverride] | {} | Overrides by menu name |

**Methods:**
- `to_dict()` → dict - Convert to JSON-serializable dict
- `from_dict(data)` → UserData - Create from dict (classmethod)

---

## JSON Format Example

```json
{
  "menus": {
    "mainmenu": {
      "items": [
        {
          "name": "movies",
          "label": "My Movies",
          "properties": {
            "widget": "recentmovies"
          },
          "position": 0
        },
        {
          "name": "user-abc123",
          "label": "Custom Item",
          "actions": [{"action": "ActivateWindow(Videos)", "condition": ""}],
          "is_new": true
        }
      ],
      "removed": ["weather"]
    }
  }
}
```

---

## Dead Code Analysis

All code appears to be in active use.

---

## Test Candidates

1. `load_userdata()` / `save_userdata()` round-trip
2. `merge_menu()` with removals
3. `merge_menu()` with reordering
4. `merge_menu()` with new items
5. `_apply_override()` property merging
6. `UserData.from_dict()` with legacy action format
