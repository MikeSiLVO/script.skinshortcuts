# Skin Shortcuts v3 - Codebase Overview

For detailed docs, see [INDEX.md](INDEX.md).

***

## Architecture

```
entry.py (RunScript entry point)
    │
    ├── build_includes() ──► config.py ──► loaders/ ──► models/
    │                                          │
    │                                          ▼
    │                                     builders/ ──► includes.xml
    │
    ├── show_management_dialog() ──► dialog/ ──► manager.py ──► userdata.py
    │
    └── reset_all_menus() / clear_custom_menu()
```

***

## Package Summary

| Package | Purpose | Key Files |
|---------|---------|-----------|
| `dialog/` | Management UI | `base.py` (init/events), `items.py` (CRUD), `pickers.py` (selection), `properties.py` (widget/bg), `subdialogs.py` (child dialogs) |
| `models/` | Data classes | `menu.py` (Menu, MenuItem), `widget.py` (Widget), `background.py` (Background), `property.py` (PropertySchema), `template.py` (Template) |
| `loaders/` | XML parsers | `menu.py` (menus.xml), `widget.py` (widgets.xml), `property.py` (properties.xml), `template.py` (templates.xml) |
| `builders/` | XML output | `includes.py` (main builder), `template.py` (template processor) |
| `providers/` | Dynamic content | `content.py` (JSON-RPC resolver for sources, addons, favourites, etc.) |

***

## Core Modules

| File | Purpose |
|------|---------|
| `entry.py` | RunScript entry point, dispatches to build/manage/reset |
| `config.py` | SkinConfig loader, merges skin defaults with userdata |
| `manager.py` | MenuManager API for dialog, tracks changes |
| `userdata.py` | User customizations (JSON), merge with skin defaults |
| `hashing.py` | Rebuild detection via config hashes |
| `localize.py` | Label resolution ($LOCALIZE, $INFO, etc.) |
| `conditions.py` | Condition evaluation (=, ~, AND, OR, NOT, EMPTY, IN) |
| `expressions.py` | Dynamic expressions ($MATH, $IF) for templates |
| `constants.py` | Shared constants (file names, target maps) |
| `exceptions.py` | Custom exception hierarchy |

***

## Key Entry Points

```python
# Build includes.xml
RunScript(script.skinshortcuts,type=buildxml)
    → entry.build_includes() → SkinConfig.load() → IncludesBuilder.write()

# Show management dialog
RunScript(script.skinshortcuts,type=manage,menu=mainmenu)
    → entry.show_management_dialog() → ManagementDialog.doModal()

# Reset all menus
RunScript(script.skinshortcuts,type=resetall)
    → entry.reset_all_menus() → delete userdata → rebuild

# Clear custom widget menu
RunScript(script.skinshortcuts,type=clear,menu=movies.customwidget)
    → entry.clear_custom_menu() → clear menu items → rebuild
```

***

## Data Flow

### Configuration Loading

```
menus.xml ──► load_menus() ──► MenuConfig (menus, groupings, subdialogs)
widgets.xml ──► load_widgets() ──► WidgetConfig (widgets, groups)
backgrounds.xml ──► load_backgrounds() ──► BackgroundConfig
properties.xml ──► load_properties() ──► PropertySchema
templates.xml ──► load_templates() ──► TemplateSchema (templates, items_templates, presets, etc.)
userdata.json ──► load_userdata() ──► merge into menus
```

### Dialog State

```
ManagementDialog (root)
    ├── MenuManager (shared) ──► tracks all changes
    ├── PropertySchema (shared)
    ├── icon_sources, subdialogs (shared)
    │
    └── Child dialogs (submenu/widget slot)
            └── Same shared state, different menu_id/suffix

Only root dialog saves on close.
```

***

## File Locations

| Type | Path |
|------|------|
| Skin config | `special://skin/shortcuts/` |
| User data | `special://profile/addon_data/script.skinshortcuts/{skin_id}.json` |
| Output | `special://skin/{resolution}/script-skinshortcuts-includes.xml` |
| Hashes | `special://profile/addon_data/script.skinshortcuts/{skin_id}.hash` |

***

## Common Patterns

### Condition Evaluation

```python
from loaders import evaluate_condition
if evaluate_condition("widgetType=custom", item_props):
    ...
```

### Property Suffix (Widget Slots)

```python
# Widget slot 2 uses suffix ".2"
widget.2, widgetPath.2, widgetType.2, etc.
```

### Content Resolution

```python
from providers import resolve_content
shortcuts = resolve_content(Content(source="addons", target="videos"))
```

***

## Quick Reference: "I need to..."

| Task | Location |
|------|----------|
| Add menu item property | `models/menu.py` MenuItem, `dialog/properties.py` |
| Add new widget type | `models/widget.py`, `loaders/widget.py` |
| Change includes output | `builders/includes.py`, `builders/template.py` |
| Add items template | `loaders/template.py`, `models/template.py` (ItemsDefinition) |
| Add dynamic content source | `providers/content.py` |
| Modify dialog behavior | `dialog/` (see package README) |
| Add skin config option | `loaders/menu.py` (menus.xml parsing) |
