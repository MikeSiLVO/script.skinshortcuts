# userdata.py

**Path:** `resources/lib/skinshortcuts/userdata.py`
**Purpose:** User customization storage and merging.

***

## Overview

Stores user modifications to menus and view selections in JSON format. Provides merging logic to combine skin defaults with user overrides.

**Storage:** `special://profile/addon_data/script.skinshortcuts/{skin_dir}.userdata.json`

***

## Public Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `get_userdata_path()` | str | Path to userdata file for current skin |
| `load_userdata(path=None)` | UserData | Load from JSON |
| `save_userdata(userdata, path=None)` | bool | Save to JSON |

***

## Merge Function

### merge_menu(default_menu, override) → Menu

Merge default menu with user overrides.

1. Start with default items, excluding removed ones
2. Apply overrides to existing items
3. Add new user items
4. Reorder based on position values

***

## Dataclasses

### UserData

| Field | Type | Description |
|-------|------|-------------|
| `menus` | dict[str, MenuOverride] | Overrides by menu name |
| `views` | dict[str, dict[str, str]] | View selections: source → content → view_id |

**View Sources:**
- `library` - Library view selections
- `plugins` - Generic plugin view selections
- `plugin.video.X` - Plugin-specific view overrides

**View Methods:**

| Method | Description |
|--------|-------------|
| `get_view(source, content)` | Get selected view ID |
| `set_view(source, content, view_id)` | Set view selection |
| `clear_view(source, content)` | Clear view selection |
| `clear_all_views()` | Clear all view selections |
| `get_plugin_overrides(content)` | Get plugin-specific overrides for content type |

### MenuOverride

| Field | Type | Description |
|-------|------|-------------|
| `items` | list[MenuItemOverride] | Item overrides |
| `removed` | list[str] | Removed item names |

### MenuItemOverride

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Item identifier |
| `label` | str | Override label (optional) |
| `actions` | list[Action] | Override actions (optional) |
| `icon` | str | Override icon (optional) |
| `disabled` | bool | Override disabled (optional) |
| `properties` | dict | Override properties |
| `position` | int | Desired position (optional) |
| `is_new` | bool | True if user-added |
