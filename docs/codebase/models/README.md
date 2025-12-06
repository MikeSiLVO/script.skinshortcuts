# models/ Package

**Path:** `resources/lib/skinshortcuts/models/`
**Purpose:** Data models and dataclasses for skin shortcuts configuration.

---

## Overview

The models package contains dataclass definitions for all configuration objects. These are pure data containers with minimal logic - parsing is done by loaders, business logic by other modules.

---

## Modules

| File | Doc | Lines | Purpose |
|------|-----|-------|---------|
| `__init__.py` | | ~50 | Re-exports all models |
| `menu.py` | [models-menu.md](models-menu.md) | 359 | Menu, MenuItem, Shortcut, Group, Content |
| `widget.py` | [models-widget.md](models-widget.md) | 81 | Widget, WidgetGroup, WidgetConfig |
| `background.py` | [models-background.md](models-background.md) | 62 | Background, BackgroundType |
| `property.py` | [models-property.md](models-property.md) | 81 | PropertySchema, Property, PropertyOption |
| `template.py` | [models-template.md](models-template.md) | 245 | TemplateSchema, Template, TemplateElement |

---

## Key Models

### Menu System (`menu.py`)
- **Menu** - A menu container with items and configuration
- **MenuItem** - Individual menu item with label, icon, action, properties
- **Shortcut** - A shortcut definition for the picker
- **Group** - A grouping of shortcuts for hierarchical picker
- **Content** - Dynamic content reference (resolved at runtime)

### Widgets (`widget.py`)
- **Widget** - Widget definition with path, type, target
- **WidgetGroup** - Grouping for widget picker
- **WidgetConfig** - Complete widget configuration

### Backgrounds (`background.py`)
- **Background** - Background definition with type and path
- **BackgroundType** - Enum: STATIC, BROWSE, MULTI, PLAYLIST, LIVE_PLAYLIST

### Properties (`property.py`)
- **PropertySchema** - Complete property schema with buttons and fallbacks
- **Property** - Single property definition with options
- **PropertyOption** - An option value for a property

### Templates (`template.py`)
- **TemplateSchema** - Complete template configuration
- **Template** - A template definition
- **TemplateElement** - Element within a template

---

## Usage Pattern

```python
from skinshortcuts.models import Menu, MenuItem, Widget, Background

# Models are typically created by loaders
menu = Menu(name="mainmenu", items=[...])

# Or accessed via config
item = config.get_menu("mainmenu").get_item("movies")
widget = config.get_widget("recentmovies")
```
