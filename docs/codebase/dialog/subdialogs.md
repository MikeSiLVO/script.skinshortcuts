# dialog/subdialogs.py

**Path:** `resources/lib/skinshortcuts/dialog/subdialogs.py`
**Purpose:** Subdialog management - submenu editing, widget slots, onclose handling.

***

## Overview

SubdialogsMixin handles spawning child dialogs for submenu editing, widget slot configuration, and processing onclose actions.

***

## SubdialogsMixin Class

### Submenu Editing

#### `_edit_submenu`()

Spawn child dialog to edit submenu. Hides parent, spawns child with shared state, shows parent when child closes.

### Subdialog Management

| Method | Purpose |
|--------|---------|
| `_spawn_subdialog` | Spawn child for subdialog definition |
| `_open_subdialog` | Open subdialog with mode/suffix for widget editing |

**Child receives:** Same manager, schema, sources, deleted_items. Different dialog_mode and property_suffix.

### Onclose Handling

| Method | Purpose |
|--------|---------|
| `_handle_onclose` | Evaluate and execute onclose actions |
| `_open_onclose_menu` | Open menu from onclose action (e.g., custom widget) |

**Menu name substitution:** `{item}` → current item name (e.g., `movies.customwidget`)

***

## Parent/Child State Sharing

Child dialogs share these objects with parent:
- `manager` - Changes accumulate
- `property_schema` - No reload needed
- `icon_sources`, `subdialogs`, `deleted_items`

Only root dialog saves on close.
