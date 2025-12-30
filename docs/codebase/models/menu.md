# models/menu.py

**Path:** `resources/lib/skinshortcuts/models/menu.py`
**Purpose:** Core dataclasses for menus, items, shortcuts, and groups.

***

## Core Classes

### MenuItem

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Unique identifier |
| `label` | str | Display label |
| `actions` | list[Action] | Actions to execute |
| `icon` | str | Icon path |
| `visible` | str | Kodi condition for includes.xml `<visible>` |
| `dialog_visible` | str | Kodi condition to filter in management dialog |
| `disabled` | bool | Grayed out state |
| `required` | bool | Cannot be deleted |
| `protection` | Protection | Protection rules |
| `properties` | dict | Custom properties (widget, background, etc) |
| `submenu` | str | Submenu reference |

**Properties:** `action` getter/setter for first unconditional action

### Menu

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Unique identifier |
| `items` | list[MenuItem] | Menu items |
| `defaults` | MenuDefaults | Default properties/actions |
| `allow` | MenuAllow | Feature toggles (widgets, backgrounds, submenus) |
| `container` | str | Container ID for visibility |
| `is_submenu` | bool | True if from `<submenu>` tag |

**Methods:** `get_item()`, `add_item()`, `remove_item()`, `move_item()`

***

## Picker Classes

### Shortcut

| Field | Type | Description |
|-------|------|-------------|
| `name`, `label` | str | Identifier and display |
| `action` | str | Direct action string |
| `path`, `browse` | str | Path and target for browse mode |
| `type` | str | Category label (label2) |
| `icon`, `condition`, `visible` | str | Display/filtering |
| `action_play`, `action_party` | str | Playlist alternatives |

**Methods:** `get_action()` - Returns action or constructs from browse+path

### ShortcutGroup

| Field | Type | Description |
|-------|------|-------------|
| `name`, `label` | str | Identifier and display |
| `icon`, `condition`, `visible` | str | Display/filtering |
| `items` | list | Child Shortcuts, ShortcutGroups, or Content |

### Content

Dynamic content reference resolved at runtime.

| Field | Type | Description |
|-------|------|-------------|
| `source` | str | Content type: playlists, addons, library, sources, favourites, pvr |
| `target` | str | Media context: videos, music, pictures |
| `folder` | str | Wrap items in subfolder |

***

## Supporting Classes

| Class | Purpose |
|-------|---------|
| `Action` | Action string with optional condition |
| `Protection` | Protection rule (type, heading, message) |
| `DefaultAction` | Default action with when (before/after) and condition |
| `MenuDefaults` | Default properties and actions for menu |
| `MenuAllow` | Feature toggles (widgets, backgrounds, submenus) |
| `IconSource` | Icon picker source (label, path, condition) |
| `SubDialog` | Subdialog definition (button_id, mode, suffix, onclose) |
| `OnCloseAction` | Action on subdialog close |
| `ActionOverride` | Action replacement rule |
| `MenuConfig` | Top-level container for all menu config |
