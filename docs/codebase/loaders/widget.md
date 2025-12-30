# loaders/widget.py

**Path:** `resources/lib/skinshortcuts/loaders/widget.py`
**Purpose:** Load widget configuration from widgets.xml.

***

## Overview

Parses widgets.xml containing widget definitions and groups for the picker dialog. Widgets and groups defined at root level.

***

## Public Functions

### load_widgets(path) → WidgetConfig

Load complete widget configuration. Returns WidgetConfig containing:
- `widgets` - Flat list of root-level Widget objects
- `groupings` - Widgets and groups for picker navigation
- `show_get_more` - Whether to show "Get More..." option

***

## Internal Parsers

| Function | Parses |
|----------|--------|
| `_parse_widget` | Widget with name, label, path, type, target, icon |
| `_parse_widget_group` | Group with nested widgets/groups/content |

**Source inheritance:** Groups pass their `source` attribute to child widgets.

**Custom widgets:** `type="custom"` widgets don't require `<path>`.

***

## XML Reference

See [skinning/widgets.md](../../skinning/widgets.md) for full XML documentation.
