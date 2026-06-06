# models/widget.py

**Path:** `resources/lib/skinshortcuts/models/widget.py`
**Purpose:** Dataclasses for widgets and widget groupings.

***

## Classes

### Widget

| Field | Type | Description |
|-------|------|-------------|
| `name`, `label` | str | Identifier and display |
| `path` | str | Widget content path |
| `type` | str | Widget type (movies, tvshows, custom) |
| `target` | str | Target window (default: videos) |
| `icon`, `condition`, `visible` | str | Display/filtering |
| `sort_by`, `sort_order` | str | Sorting options |
| `limit` | int | Item limit |
| `source` | str | Source type (library, playlist, addon) |
| `slot` | str | For custom widgets: property slot |
| `browse` | bool | Opt-in: allow browse-into during picker |

**Methods:** `to_properties(prefix)` - Convert to property dict (widget, widgetLabel, widgetPath, widgetTarget, widgetSource)

### WidgetGroup

| Field | Type | Description |
|-------|------|-------------|
| `name`, `label` | str | Identifier and display |
| `icon`, `condition`, `visible` | str | Display/filtering |
| `items` | list | Child Widgets, WidgetGroups, or Content |
| `flat` | bool | No folder header; children render at parent level (default: False) |

### WidgetConfig

| Field | Type | Description |
|-------|------|-------------|
| `widgets` | list[Widget] | All defined widgets (flat) |
| `groupings` | list | Picker structure |
