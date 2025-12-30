# loaders/ Package

**Path:** `resources/lib/skinshortcuts/loaders/`
**Purpose:** XML configuration file parsers.

***

## Overview

Parses skin XML configuration files into model objects. Each loader handles a specific file type.

***

## Modules

| File | Doc | Purpose |
|------|-----|---------|
| `base.py` | [base.md](base.md) | Shared XML utilities |
| `menu.py` | [menu.md](menu.md) | menus.xml parser |
| `widget.py` | [widget.md](widget.md) | widgets.xml parser |
| `background.py` | [background.md](background.md) | backgrounds.xml parser |
| `property.py` | [property.md](property.md) | properties.xml parser |
| `template.py` | [template.md](template.md) | templates.xml parser |

***

## Public Functions

| Function | Module | Purpose |
|----------|--------|---------|
| `load_menus(path)` | menu.py | Load menus.xml |
| `load_groupings(path)` | menu.py | Load shortcut groupings only |
| `load_widgets(path)` | widget.py | Load widgets.xml |
| `load_backgrounds(path)` | background.py | Load backgrounds.xml |
| `load_properties(path)` | property.py | Load properties.xml |
| `load_templates(path)` | template.py | Load templates.xml |

***

## XML File Documentation

For XML file format documentation, see:
- [skinning/menus.md](../../skinning/menus.md)
- [skinning/widgets.md](../../skinning/widgets.md)
- [skinning/backgrounds.md](../../skinning/backgrounds.md)
- [skinning/properties.md](../../skinning/properties.md)
- [skinning/templates.md](../../skinning/templates.md)
