# config.py

**Path:** `resources/lib/skinshortcuts/config.py`
**Purpose:** Skin configuration loader - main entry point for loading all config.

***

## Overview

SkinConfig is the central configuration container. Loads all XML files and userdata, provides unified access to complete configuration.

***

## SkinConfig Class

### Class Method

#### load(shortcuts_path, load_user=True, userdata_path=None) → SkinConfig

Load configuration from shortcuts directory.

**Load order:**
1. menus.xml
2. widgets.xml
3. backgrounds.xml
4. templates.xml
5. properties.xml
6. views.xml
7. Userdata (merges with defaults)
8. Expand per-item submenu instances (`{parent}/{item_name}` keys) for each item linking a `<submenu>` template

### Instance Fields

| Field | Type | Description |
|-------|------|-------------|
| `menus` | list[Menu] | All menus (merged with userdata) |
| `default_menus` | list[Menu] | Original skin defaults (immutable) |
| `userdata` | UserData | Loaded user customizations |
| `templates` | TemplateSchema | Template configuration |
| `property_schema` | PropertySchema | Property schema |
| `subdialogs` | list[SubDialog] | Subdialog definitions |
| `icon_overrides` | dict[str, str] | Icon override map |

### Instance Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_menu(name)` | Menu | Get merged menu by name |
| `get_default_menu(name)` | Menu | Get original skin default |
| `get_widget(name)` | Widget | Get widget by name |
| `get_background(name)` | Background | Get background by name |
| `get_subdialog(button_id)` | SubDialog | Get subdialog definition |
| `build_includes(output_path)` | None | Build and write includes.xml |

### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `widgets` | list[Widget] | All widgets |
| `widget_groupings` | list | Widget picker groupings |
| `backgrounds` | list[Background] | All backgrounds |
