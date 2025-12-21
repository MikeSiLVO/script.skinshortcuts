# loaders/ Package

**Path:** `resources/lib/skinshortcuts/loaders/`
**Purpose:** XML configuration file parsers.

***

## Overview

The loaders package parses skin XML configuration files (menus.xml, widgets.xml, backgrounds.xml, properties.xml, templates.xml) into model objects. Each loader handles a specific file type.

***

## Modules

| File | Doc | Lines | Purpose |
|------|-----|-------|---------|
| `__init__.py` | | ~30 | Re-exports public functions |
| `base.py` | [loaders-base.md](loaders-base.md) | 152 | Shared XML utilities |
| `menu.py` | [loaders-menu.md](loaders-menu.md) | 476 | menus.xml parser |
| `widget.py` | [loaders-widget.md](loaders-widget.md) | 149 | widgets.xml parser |
| `background.py` | [loaders-background.md](loaders-background.md) | 99 | backgrounds.xml parser |
| `property.py` | [loaders-property.md](loaders-property.md) | 284 | properties.xml parser |
| `template.py` | [loaders-template.md](loaders-template.md) | 454 | templates.xml parser |

***

## Public Functions

### Menu Loading (`menu.py`)

* `load_menu_config(path)` - Load complete menu config from menus.xml
* `load_groupings(path)` - Load shortcut groupings only

### Widget Loading (`widget.py`)

* `load_widgets(path)` - Load widget config from widgets.xml
* `load_widget_groupings(path)` - Load widget groupings only

### Background Loading (`background.py`)

* `load_backgrounds(path)` - Load backgrounds from backgrounds.xml

### Property Loading (`property.py`)

* `load_properties(path)` - Load property schema from properties.xml
* `evaluate_condition(condition, props)` - Re-exported from `conditions.py` for convenience

### Template Loading (`template.py`)

* `load_templates(path)` - Load template schema from templates.xml

### Base Utilities (`base.py`)

* `apply_suffix_transform(text, suffix)` - Apply suffix to property references
* `apply_suffix_to_from(text, suffix)` - Apply suffix in template from attributes

***

## Usage Pattern

```python
from skinshortcuts.loaders import load_menu_config, load_widgets

# Load configurations
menu_config = load_menu_config(Path("shortcuts/menus.xml"))
widget_config = load_widgets(Path("shortcuts/widgets.xml"))

# Access parsed data
menus = menu_config.menus
groupings = menu_config.groupings
widgets = widget_config.widgets
```

***

## File Format Reference

Each loader expects specific XML structure. See individual module docs for schema details:

* [menus.xml schema](loaders-menu.md)
* [widgets.xml schema](loaders-widget.md)
* [backgrounds.xml schema](loaders-background.md)
* [properties.xml schema](loaders-property.md)
* [templates.xml schema](loaders-template.md)
