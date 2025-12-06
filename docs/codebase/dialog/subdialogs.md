# dialog/subdialogs.py

**Path:** `resources/lib/skinshortcuts/dialog/subdialogs.py`
**Lines:** 267
**Purpose:** Subdialog management - submenu editing, widget slots, onclose handling.

---

## Overview

SubdialogsMixin handles spawning child dialogs for submenu editing, widget slot configuration, and processing onclose actions.

---

## SubdialogsMixin Class (line 24)

### Submenu Editing

#### _edit_submenu() (line 49)

Spawn child dialog to edit submenu for selected item.

**Behavior:**
1. Check if submenus are allowed for this menu
2. Get submenu name (item.submenu or item.name)
3. Hide parent dialog
4. Spawn child with shared manager/schema/sources
5. Show parent again when child closes

---

### Subdialog Management

#### _spawn_subdialog(subdialog) (line 88)

Spawn a child dialog for a subdialog definition.

**Parameters:**
- `subdialog` - SubDialog definition containing mode, suffix, onclose

**Behavior:**
1. Open subdialog with specified mode and suffix
2. After close, evaluate onclose actions

#### _open_subdialog(subdialog) (line 163)

Open the subdialog for widget/property editing.

**Passes to child:**
- Same menu_id (editing same menu)
- Different `dialog_mode` (e.g., "widget1", "widget2")
- Different `property_suffix` (e.g., ".2" for widget slot 2)
- `setfocus` control ID
- Current `selected_index`
- Shared manager, schema, sources, deleted_items

---

### Onclose Handling

#### _handle_onclose(subdialog, item) (line 107)

Handle onclose actions after a subdialog closes.

**Behavior:**
1. Re-fetch item to get updated properties
2. Evaluate each onclose action's condition
3. Execute first matching action

**Onclose action types:**
- `action="menu"` - Open another menu (e.g., custom widget editor)

#### _open_onclose_menu(menu_name, subdialog) (line 131)

Open a menu from an onclose action.

**Used for:**
- Custom widget editing when `widgetType=custom` is set
- The menu is created if it doesn't exist

**Menu name substitution:**
- `{item}` is replaced with current item name
- Example: `{item}.customwidget` → `movies.customwidget`

---

## Parent/Child State Sharing

Child dialogs receive these shared objects:

| Object | Purpose |
|--------|---------|
| `manager` | Same MenuManager - changes accumulate |
| `property_schema` | Same PropertySchema - no reload needed |
| `icon_sources` | Same icon sources list |
| `subdialogs` | Same subdialog definitions |
| `deleted_items` | Same deleted items tracker |

This allows:
- Edits in child to be visible in parent after child closes
- Single save operation when root dialog closes
- Consistent UI behavior across all dialog levels
