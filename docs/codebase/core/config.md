# config.py

**Path:** `resources/lib/skinshortcuts/config.py`
**Lines:** 213
**Purpose:** Skin configuration loader - main entry point for loading all config files.

---

## Overview

SkinConfig is the central configuration container. It loads all configuration files (menus.xml, widgets.xml, backgrounds.xml, properties.xml, templates.xml) and userdata, providing a unified interface for accessing the complete configuration.

---

## SkinConfig Class (line 25)

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `menus` | list[Menu] | [] | All menus (merged with userdata) |
| `default_menus` | list[Menu] | [] | Original skin defaults (immutable, deep copied) |
| `_widget_config` | WidgetConfig | WidgetConfig() | Widget configuration |
| `backgrounds` | list[Background] | [] | All backgrounds |
| `userdata` | UserData | UserData() | Loaded userdata |
| `templates` | TemplateSchema | TemplateSchema() | Template configuration |
| `property_schema` | PropertySchema | PropertySchema() | Property schema |
| `subdialogs` | list[SubDialog] | [] | Subdialog definitions |

### Properties

#### widgets → list[Widget] (line 37)
Get list of widgets from widget config.

#### widget_groupings → list (line 42)
Get widget groupings for picker dialog.

---

## Class Methods

### load(shortcuts_path, load_user=True, userdata_path=None) → SkinConfig (line 47)
Load configuration from shortcuts directory.

**Parameters:**
- `shortcuts_path` - Path to skin's shortcuts folder
- `load_user` - Whether to load and merge user customizations
- `userdata_path` - Optional custom userdata path (for testing)

**Load order:**
1. Menu config (menus.xml)
2. Widgets (widgets.xml)
3. Backgrounds (backgrounds.xml)
4. Templates (templates.xml)
5. Property schema (properties.xml)
6. Userdata (if load_user=True)

**Merge logic:**
1. For each skin menu, merge with userdata override
2. Apply action overrides to fix deprecated actions
3. Add user-created menus that don't exist in skin

---

## Instance Methods

### get_widget(widget_name) → Widget | None (line 100)
Get widget by name.

Searches top-level widgets and widgets within groupings.

### _find_widget_in_groupings(widget_name, groups) → Widget | None (line 113)
Recursively search for a widget within groupings.

### get_background(bg_name) → Background | None (line 130)
Get background by name.

### get_menu(menu_name) → Menu | None (line 137)
Get menu by name (merged with userdata).

### get_default_menu(menu_name) → Menu | None (line 144)
Get original skin default menu by name (before userdata merge).

Used for reset-to-defaults functionality.

### get_subdialog(button_id) → SubDialog | None (line 151)
Get subdialog definition by button ID.

### build_includes(output_path) (line 151)
Build and write includes.xml.

Delegates to `build_includes_from_menus()` with `self.menus`.

### build_includes_from_menus(output_path, menus) (line 155)
Build and write includes.xml from provided menus.

**Process:**
1. Resolve background/widget properties for each menu
2. Create IncludesBuilder with menus, templates, property_schema
3. Write to output path

### _resolve_item_properties(menu) (line 175)
Resolve background and widget names to their full properties.

For each item:
- If has "background" but no "backgroundLabel", look up and add bg properties
- If has "widget" but no "widgetLabel", look up and add widget properties

---

## Module Function

### _apply_action_overrides(menu, overrides) (line 196)
Apply action overrides to all items in a menu.

Replaces deprecated/changed actions with updated versions.
Comparison is case-insensitive.

---

## Dead Code Analysis

All code appears to be in active use.

---

## Test Candidates

1. `load()` with missing optional files
2. `load()` userdata merge behavior
3. `get_widget()` search in groupings
4. `_resolve_item_properties()` property lookup
5. `_apply_action_overrides()` case-insensitive matching
