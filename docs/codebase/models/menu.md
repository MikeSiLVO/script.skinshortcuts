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
| `label2` | str | Secondary label (label2 element) |
| `icon` | str | Icon path |
| `thumb` | str | Thumb path |
| `visible` | str | Kodi condition for includes.xml `<visible>` |
| `dialog_visible` | str | Kodi condition to filter in management dialog |
| `disabled` | bool | Grayed out state |
| `required` | bool | Cannot be deleted |
| `protection` | Protection | Protection rules |
| `properties` | dict | Custom properties (widget, background, etc) |
| `submenu` | str | Submenu reference |
| `original_action` | str | Set from defaults, not saved to userdata |
| `includes` | list[IncludeRef] | Include references for controltype output (before/after onclick) |
| `is_placeholder` | bool | Empty placeholder, dropped from save until edited |

**Properties:** `action` getter/setter for last unconditional action (the destination action for display)

### Menu

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Unique identifier |
| `items` | list[MenuItem] | Menu items |
| `defaults` | MenuDefaults | Default properties/actions |
| `allow` | MenuAllow | Feature toggles (widgets, backgrounds, submenus) |
| `container` | str | Container ID for visibility |
| `is_submenu` | bool | True if from `<submenu>` tag |
| `menu_type` | str \| None | `"widgets"` for widget submenus |
| `controltype` | str | Output as `<control type="X">` instead of `<item>` |
| `startid` | int | Starting control ID for `controltype` menus |
| `template_only` | str | Contains `"submenu"` to skip combined submenu include |
| `template_origin` | str | For per-item submenu instances: the template they were seeded from |
| `standalone` | bool | When False (from `<submenu standalone="false">`), skip the per-template `skinshortcuts-{name}` include |
| `build` | str | Build mode: `"true"` (default) or `"auto"` |
| `action` | str | Action to match for `build="auto"` |
| `submenu_path` | str | `"all"` (from `submenuPath="all"` on the parent `<menu>`) emits the numbered `submenuPath.N` tail; the global form is `MenuConfig.submenu_path_all` |

**Methods:** `get_item()`, `add_item()`, `remove_item()`, `move_item()`

***

## Picker Classes

### Shortcut

| Field | Type | Description |
|-------|------|-------------|
| `name`, `label` | str | Identifier and display |
| `actions` | list[str] | Action strings (supports multiple) |
| `primary_action` | str | Action marked `primary="true"` for display properties |
| `path`, `browse` | str | Path and target for browse mode |
| `type` | str | Category label (label2) |
| `icon`, `condition`, `visible` | str | Display/filtering |
| `item_visible` | str | Visibility condition baked into the resulting menu item when picked (vs `visible` which only hides from picker) |
| `action_play`, `action_party` | str | Playlist alternatives |

**Properties:** `action` - Returns `primary_action` if set, otherwise last action in list

**Methods:** `get_action()` - Returns primary action or constructs from browse+path

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
| `path` | str | Custom path override |
| `folder` | str | Wrap items in subfolder |
| `label` | str | Result label for addons placeholder |
| `icon` | str | Icon override |
| `condition` | str | Property condition |
| `visible` | str | Kodi visibility condition |

### Input

User input prompt for custom values.

| Field | Type | Description |
|-------|------|-------------|
| `label` | str | Display label in picker |
| `type` | str | Input method: text, numeric, ipaddress, password |
| `for_` | str | What value becomes: action, label, path |
| `icon`, `condition`, `visible` | str | Display/filtering |

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
| `SubDialog` | Subdialog definition (button_id, mode, menu, setfocus, suffix, onclose) |
| `OnCloseAction` | Action on subdialog close |
| `ActionOverride` | Action replacement rule |
| `MenuConfig` | Top-level container for all menu config |
