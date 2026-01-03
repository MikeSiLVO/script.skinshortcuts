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
| `_resolve_menu_reference` | Resolve menu reference with placeholder support |
| `_open_onclose_menu` | Open resolved menu from onclose action |

**Menu reference placeholders:**
- `{customWidget}` → custom widget slot 1 (creates if needed)
- `{customWidget.2}` → custom widget slot 2 (creates if needed)
- `{item}.customwidget` → legacy format, converted to explicit reference

***

## Parent/Child State Sharing

Child dialogs share these objects with parent:
- `manager` - Changes accumulate
- `property_schema` - No reload needed
- `icon_sources`, `subdialogs`, `deleted_items`

Only root dialog saves on close.
