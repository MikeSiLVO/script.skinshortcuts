# models/widget.py

**Path:** `resources/lib/skinshortcuts/models/widget.py`
**Lines:** 81
**Purpose:** Dataclass models for widgets and widget groupings.

---

## Overview

Defines the Widget model and related grouping structures for the widget picker system.

---

## Type Alias

```python
WidgetGroupContent = Union[Widget, WidgetGroup, Content]  # line 14
```

Items that can appear in a WidgetGroup's items list.

---

## Classes

### Widget (line 18)
A widget assignable to menu items.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Unique identifier |
| `label` | str | required | Display label |
| `path` | str | required | Widget content path |
| `type` | str | "" | Widget type (movies, tvshows, custom, etc) |
| `target` | str | "videos" | Target window |
| `icon` | str | "" | Icon path |
| `condition` | str | "" | Property condition (evaluated against item properties) |
| `visible` | str | "" | Kodi visibility condition (evaluated at runtime) |
| `sort_by` | str | "" | Sort field |
| `sort_order` | str | "" | Sort order (ascending/descending) |
| `limit` | int\|None | None | Item limit |
| `source` | str | "" | Source type (library, playlist, addon) |
| `slot` | str | "" | For custom widgets: property slot (e.g., "widget.2") |

**Properties:**
- `is_custom` → bool - Returns True if type=="custom"

**Methods:**
- `to_properties(prefix="widget")` → dict[str,str] - Convert to skin property dict

**Property output example:**
```python
{
    "widget": "recentmovies",
    "widgetLabel": "Recent Movies",
    "widgetPath": "videodb://recentlyaddedmovies/",
    "widgetTarget": "videos",
    "widgetSource": "library"  # only if source is set
}
```

**Used by:** config.py, dialog.py (widget picker), builders/includes.py

---

### WidgetGroup (line 61)
A group/category in widget picker.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Unique identifier |
| `label` | str | required | Display label |
| `condition` | str | "" | Property condition (evaluated against item properties) |
| `visible` | str | "" | Kodi visibility condition (evaluated at runtime) |
| `icon` | str | "" | Icon for picker display (default: DefaultFolder.png) |
| `items` | list[WidgetGroupContent] | [] | Child items: Widget, WidgetGroup, or Content |

**Used by:** WidgetConfig, dialog.py (_pick_widget_from_groups), loaders/widget.py

---

### WidgetConfig (line 71)
Top-level widget configuration container.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `widgets` | list[Widget] | [] | All defined widgets (flat list) |
| `groupings` | list[WidgetGroup\|Widget] | [] | Picker structure (can include standalone widgets) |
| `show_get_more` | bool | True | Whether to show "Get More..." option |

**Used by:** config.py (SkinConfig._widget_config), loaders/widget.py

---

## Dead Code Analysis

All classes appear to be in active use.

---

## Test Candidates

1. `Widget.is_custom` property
2. `Widget.to_properties()` with and without source
3. `Widget.to_properties()` with custom prefix
