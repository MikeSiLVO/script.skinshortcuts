# models/menu.py

**Path:** `resources/lib/skinshortcuts/models/menu.py`
**Lines:** 368
**Purpose:** Core dataclass models for menus, menu items, shortcuts, groups, and related structures.

***

## Overview

This is the largest model file, containing all menu-related data structures. These are pure data classes (no business logic except simple accessors).

***

## Classes

### IconSource (line 16)

Source for icon picker browsing.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `label` | str | required | Display label |
| `path` | str | required | Browse path, or "browse" for file browser |
| `condition` | str | "" | Property condition (evaluated against item properties) |
| `visible` | str | "" | Kodi visibility condition (evaluated at runtime) |
| `icon` | str | "" | Icon for this source |

**Used by:** dialog/items.py (icon picker), loaders/menu.py

***

### Content (line 35)

Dynamic content reference resolved at runtime (playlists, addons, sources, etc).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `source` | str | required | Content type: playlists, addons, library, sources, favourites, pvr, commands, settings |
| `target` | str | "" | Media context: videos, music, pictures, programs, tv, radio |
| `path` | str | "" | Custom path override |
| `condition` | str | "" | Property condition (evaluated against item properties) |
| `visible` | str | "" | Kodi visibility condition (evaluated at runtime) |
| `icon` | str | "" | Icon override |
| `label` | str | "" | Label override |
| `folder` | str | "" | If set, wrap items in subfolder with this label |

**Used by:** dialog/pickers.py (shortcut/widget picker)

***

### Action (line 71)

An action with optional condition.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `action` | str | required | The Kodi action string |
| `condition` | str | "" | Condition for this action to execute |

**Used by:** MenuItem, userdata.py, manager.py, dialog.py

***

### Protection (line 82)

Protection rule for menu items preventing accidental changes.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | str | "all" | What to protect: "delete", "action", or "all" |
| `heading` | str | "" | Confirmation dialog heading |
| `message` | str | "" | Confirmation dialog message |

**Methods:**

* `protects_delete()` → bool - Returns True if deletion is protected
* `protects_action()` → bool - Returns True if action changes are protected

**Used by:** dialog.py (delete/action confirmation)

***

### Shortcut (line 111)

A shortcut option in picker groupings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Unique identifier |
| `label` | str | required | Display label |
| `action` | str | "" | Direct action string |
| `path` | str | "" | Path for browse mode |
| `browse` | str | "" | Browse target window (videos, music, etc) |
| `type` | str | "" | Category label (shown as label2) |
| `icon` | str | "DefaultShortcut.png" | Icon path |
| `condition` | str | "" | Property condition (evaluated against item properties) |
| `visible` | str | "" | Kodi visibility condition (evaluated at runtime) |
| `action_play` | str | "" | PlayMedia action (for playlists) |
| `action_party` | str | "" | Party mode action (for music playlists) |

**Methods:**

* `get_action()` → str - Returns action, or constructs ActivateWindow from browse+path

**Playlist Actions:** When `action_play` is set, the picker dialog offers a choice between display/play/party modes (see dialog/pickers.py).

**Used by:** dialog.py (shortcut picker), loaders/menu.py

***

### Group (line 151)

A group/category of shortcuts in picker groupings.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Unique identifier |
| `label` | str | required | Display label |
| `condition` | str | "" | Property condition (evaluated against item properties) |
| `visible` | str | "" | Kodi visibility condition (evaluated at runtime) |
| `icon` | str | "" | Icon for this group |
| `items` | list[GroupContent] | [] | Child items: Shortcut, Group, or Content |

**Used by:** dialog.py (shortcut picker), loaders/menu.py

***

### MenuItem (line 169)

A single item in a menu (the core data structure).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Unique identifier |
| `label` | str | required | Display label |
| `actions` | list[Action] | [] | Actions to execute |
| `label2` | str | "" | Secondary label |
| `icon` | str | "DefaultShortcut.png" | Icon path |
| `thumb` | str | "" | Thumbnail path |
| `visible` | str | "" | Kodi condition output to includes.xml `<visible>` element |
| `dialog_visible` | str | "" | Kodi condition to filter item in management dialog |
| `disabled` | bool | False | If True, item is grayed out |
| `required` | bool | False | If True, cannot be deleted |
| `protection` | Protection|None | None | Protection configuration |
| `properties` | dict[str,str] | {} | Custom properties (widget, background, etc) |
| `submenu` | str|None | None | Submenu reference by name |
| `original_action` | str | "" | Original action for protection matching |

**Dual Visibility Fields:**
MenuItem has two visibility fields serving different purposes:

* `visible` - From `<visible>` child element. Output to generated includes.xml for Kodi runtime evaluation.
* `dialog_visible` - From `visible=` attribute on `<item>`. Evaluated in Python when loading the management dialog to hide items (e.g., hide "Play Disc" when no disc drive).

**Properties:**

* `action` (getter) → str - Returns first unconditional action
* `action` (setter) - Sets first unconditional action

**Used by:** Menu, manager.py, userdata.py, dialog.py, builders/includes.py

***

### DefaultAction (line 213)

A default action applied to all items in a menu.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `action` | str | required | Action to execute |
| `when` | str | "before" | When to run: "before" or "after" item actions |
| `condition` | str | "" | Visibility condition |

**Used by:** MenuDefaults, builders/includes.py

***

### MenuDefaults (line 228)

Default properties and actions for items in a menu.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `properties` | dict[str,str] | {} | Default property values |
| `actions` | list[DefaultAction] | [] | Default actions |

**Used by:** Menu, loaders/menu.py

***

### MenuAllow (line 236)

Configuration for what features are allowed in a menu.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `widgets` | bool | True | Allow widget selection |
| `backgrounds` | bool | True | Allow background selection |
| `submenus` | bool | True | Allow submenu navigation |

**Used by:** Menu, dialog.py (button visibility)

***

### Menu (line 245)

A menu containing menu items.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Unique identifier (e.g., "mainmenu") |
| `items` | list[MenuItem] | [] | Menu items |
| `defaults` | MenuDefaults | MenuDefaults() | Default properties/actions |
| `allow` | MenuAllow | MenuAllow() | Feature toggles |
| `container` | str|None | None | Container ID for submenu visibility |
| `is_submenu` | bool | False | True if defined with \<submenu\> tag |

**Methods:**

* `get_item(item_name)` → MenuItem|None - Find item by name
* `add_item(item, position=None)` - Add item at position or end
* `remove_item(item_name)` → bool - Remove item, return True if found
* `move_item(item_name, direction)` → bool - Move item up (-1) or down (+1)

**Used by:** config.py, manager.py, userdata.py, builders/includes.py

***

### OnCloseAction (line 291)

Action to execute when a subdialog closes.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `action` | str | required | Action type (currently only "menu") |
| `menu` | str | "" | Menu name for action="menu" (supports {item} placeholder) |
| `condition` | str | "" | Condition evaluated against current item properties |

**Used by:** SubDialog, dialog.py (_handle_onclose)

***

### SubDialog (line 310)

Subdialog definition for management dialog.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `button_id` | int | required | Button ID that triggers this subdialog |
| `mode` | str | required | Mode name for Window(Home).Property(skinshortcuts-dialog) |
| `setfocus` | int|None | None | Control ID to focus on open |
| `suffix` | str | "" | Property suffix for widget slots (e.g., ".2"). Set in Window(Home).Property(skinshortcuts-suffix) |
| `onclose` | list[OnCloseAction] | [] | Actions to run on close |

**Used by:** config.py, dialog.py (_spawn_subdialog, _open_subdialog)

***

### ActionOverride (line 336)

Replaces deprecated actions with updated versions.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `replace` | str | required | Action string to find |
| `action` | str | required | Replacement action string |

**Used by:** config.py (_apply_action_overrides)

***

### MenuConfig (line 352)

Top-level menu configuration container.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `menus` | list[Menu] | [] | All menus |
| `groupings` | list[Group] | [] | Shortcut picker groupings |
| `icon_sources` | list[IconSource] | [] | Icon picker sources |
| `subdialogs` | list[SubDialog] | [] | Subdialog definitions |
| `action_overrides` | list[ActionOverride] | [] | Action overrides |
| `show_context_menu` | bool | True | Whether to show context menu on items |

**Used by:** loaders/menu.py, config.py

***

## Type Alias

```python
GroupContent = Union[Shortcut, Group, Content]  # line 12
```

Items that can appear in a Group's items list.

***

## Dead Code Analysis

All classes appear to be in active use.

***

## Test Candidates

1. `Shortcut.get_action()` - test browse mode action construction
2. `MenuItem.action` property getter/setter
3. `Protection.protects_delete()` and `protects_action()`
4. `Menu.get_item()`, `add_item()`, `remove_item()`, `move_item()`
