# loaders/menu.py

**Path:** `resources/lib/skinshortcuts/loaders/menu.py`
**Purpose:** Load menus, groupings, and related configuration from menus.xml.

***

## Overview

Primary loader for menu configuration. Parses menus.xml containing menu definitions, shortcut groupings, icon sources, subdialog definitions, and action overrides.

***

## Public Functions

### load_menus(path) → MenuConfig

Load complete menu configuration. Returns MenuConfig containing:
- `menus` - All Menu objects
- `groupings` - Shortcut picker groups
- `icon_sources` - Icon picker sources
- `subdialogs` - Subdialog definitions
- `action_overrides` - Action replacement rules
- `show_context_menu` - Context menu visibility

### load_groupings(path) → list[ShortcutGroup]

Load just the shortcut groupings (for picker without full reload).

***

## Internal Parsers

| Function | Parses |
|----------|--------|
| `_parse_menus` | `<menu>` and `<submenu>` elements |
| `_parse_menu` | Single menu with items, defaults, allow |
| `_parse_item` | Menu item with label, actions, properties, protection |
| `_parse_defaults` | Menu-wide default properties and actions |
| `_parse_allow` | Feature toggles (widgets, backgrounds, submenus) |
| `_parse_groupings` | `<groupings>` element with groups/shortcuts |
| `_parse_shortcut_group` | Group with nested groups, shortcuts, content |
| `_parse_shortcut` | Shortcut in action or browse mode |
| `_parse_icons` | Icon sources (simple path or advanced with conditions) |
| `_parse_dialogs` | Subdialog definitions |
| `_parse_overrides` | Action replacement rules |

***

## XML Reference

See [skinning/menus.md](../../skinning/menus.md) for full XML documentation.
