# dialog/__init__.py

**Path:** `resources/lib/skinshortcuts/dialog/__init__.py`
**Purpose:** Public API and ManagementDialog class composition.

***

## ManagementDialog Class

Composed from all mixins:

```python
class ManagementDialog(
    SubdialogsMixin,
    PropertiesMixin,
    PickersMixin,
    ItemsMixin,
    DialogBaseMixin,  # inherits from xbmcgui.WindowXMLDialog
):
```

***

## Public Functions

### show_management_dialog(menu_id="mainmenu", shortcuts_path=None) → bool

Show the management dialog. Returns True if changes were saved.

### get_shortcuts_path() → str

Get path to current skin's shortcuts folder.

***

## Exported Constants

Control IDs re-exported for skin developers:
- `CONTROL_LIST`, `CONTROL_ADD`, `CONTROL_DELETE`
- `CONTROL_MOVE_UP`, `CONTROL_MOVE_DOWN`
- `CONTROL_SET_LABEL`, `CONTROL_SET_ICON`, `CONTROL_SET_ACTION`
- `CONTROL_RESTORE_DELETED`, `CONTROL_RESET_ITEM`, `CONTROL_TOGGLE_DISABLED`
- `CONTROL_CHOOSE_SHORTCUT`, `CONTROL_EDIT_SUBMENU`
