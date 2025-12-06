# dialog/\_\_init\_\_.py

**Path:** `resources/lib/skinshortcuts/dialog/__init__.py`
**Lines:** 131
**Purpose:** Public API and ManagementDialog class composition.

---

## Overview

This module defines the public API for the dialog package and composes the `ManagementDialog` class from all mixins.

---

## Classes

### ManagementDialog (line 53)

The complete dialog class, composed from all mixins.

**Inheritance:**
```python
class ManagementDialog(
    SubdialogsMixin,
    PropertiesMixin,
    PickersMixin,
    ItemsMixin,
    DialogBaseMixin,  # inherits from xbmcgui.WindowXMLDialog
):
```

---

## Public Functions

### show_management_dialog(menu_id, shortcuts_path) → bool (line 73)

Show the management dialog.

**Parameters:**
- `menu_id` - ID of menu to manage (default: "mainmenu")
- `shortcuts_path` - Path to shortcuts folder (auto-detected if None)

**Returns:** True if changes were saved

**Example:**
```python
from skinshortcuts.dialog import show_management_dialog

# Show dialog for main menu
changes_saved = show_management_dialog()

# Show dialog for specific menu
changes_saved = show_management_dialog(menu_id="submenu")
```

### get_shortcuts_path() → str

Get path to current skin's shortcuts folder.

Imported from `base.py`.

---

## Exported Constants

All control ID constants are re-exported for skin developers:

- `CONTROL_LIST`, `CONTROL_ADD`, `CONTROL_DELETE`
- `CONTROL_MOVE_UP`, `CONTROL_MOVE_DOWN`
- `CONTROL_SET_LABEL`, `CONTROL_SET_ICON`, `CONTROL_SET_ACTION`
- `CONTROL_RESTORE_DELETED`, `CONTROL_RESET_ITEM`, `CONTROL_TOGGLE_DISABLED`
- `CONTROL_CHOOSE_SHORTCUT`, `CONTROL_EDIT_SUBMENU`
- `ACTION_CANCEL`, `ACTION_CONTEXT`

---

## Module Exports (`__all__`)

```python
__all__ = [
    "ManagementDialog",
    "show_management_dialog",
    "get_shortcuts_path",
    # Control IDs...
    # Action IDs...
]
```
