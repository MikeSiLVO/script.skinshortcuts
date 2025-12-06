# dialog/ Package

**Path:** `resources/lib/skinshortcuts/dialog/`
**Total Lines:** 2485
**Purpose:** Management dialog for skin shortcuts - the main UI for editing menus.

---

## Overview

The dialog package implements the WindowXMLDialog that allows users to edit menus, items, widgets, backgrounds, and custom properties. It uses a mixin pattern to separate concerns into focused modules.

---

## Modules

| File | Doc | Lines | Purpose |
|------|-----|-------|---------|
| `__init__.py` | [dialog-init.md](dialog-init.md) | 131 | Public API, ManagementDialog class |
| `base.py` | [dialog-base.md](dialog-base.md) | 637 | Core initialization, list management, events |
| `items.py` | [dialog-items.md](dialog-items.md) | 438 | Item operations (add, delete, move, etc.) |
| `pickers.py` | [dialog-pickers.md](dialog-pickers.md) | 478 | Shortcut and widget picker dialogs |
| `properties.py` | [dialog-properties.md](dialog-properties.md) | 534 | Property management (widget, background) |
| `subdialogs.py` | [dialog-subdialogs.md](dialog-subdialogs.md) | 267 | Subdialog and submenu handling |

---

## Architecture

### Mixin Pattern

The `ManagementDialog` class is composed from multiple mixins:

```
ManagementDialog
    ← SubdialogsMixin      (subdialogs.py)
    ← PropertiesMixin      (properties.py)
    ← PickersMixin         (pickers.py)
    ← ItemsMixin           (items.py)
    ← DialogBaseMixin      (base.py)
        ← xbmcgui.WindowXMLDialog
```

Each mixin provides specific functionality:
- **DialogBaseMixin** - Core initialization, list management, event routing
- **ItemsMixin** - Item operations (add, delete, move, label, icon, action)
- **PickersMixin** - Shortcut and widget picker dialogs
- **PropertiesMixin** - Property management (widget, background, toggle, options)
- **SubdialogsMixin** - Subdialog management (submenu editing, onclose handling)

### Mixin Type Stubs Pattern

Mixins need type hints for methods they call from other mixins. These must be
inside `TYPE_CHECKING` blocks to avoid overriding real implementations at runtime:

```python
from typing import TYPE_CHECKING

class SomeMixin:
    # Attribute type hints (OK outside TYPE_CHECKING)
    menu_id: str
    manager: MenuManager | None

    if TYPE_CHECKING:
        # Method stubs MUST be inside TYPE_CHECKING
        def _log(self, msg: str) -> None: ...
        def _get_selected_item(self) -> MenuItem | None: ...
```

**Warning:** Method stubs outside `TYPE_CHECKING` will override real implementations
due to Python MRO, causing silent failures.

### Parent/Child Dialog Architecture

The dialog supports spawning child dialogs for:
1. **Submenu editing** - Edit a different menu
2. **Widget slots** - Edit widget properties with different suffix
3. **Custom widget menus** - Edit custom widget items

Child dialogs share state with parent:
- `manager` - Same MenuManager instance
- `property_schema` - Same PropertySchema
- `icon_sources` - Same icon sources
- `subdialogs` - Same subdialog definitions
- `deleted_items` - Same deleted items tracker

Only the root dialog saves changes on close.

---

## Public API

```python
from skinshortcuts.dialog import show_management_dialog, get_shortcuts_path

# Show the management dialog
changes_saved = show_management_dialog(menu_id="mainmenu")

# Get skin's shortcuts path
path = get_shortcuts_path()
```

---

## Control IDs

For skin XML integration, these control IDs are used:

| Constant | ID | Purpose |
|----------|-----|---------|
| `CONTROL_LIST` | 211 | Menu items list |
| `CONTROL_ADD` | 301 | Add item button |
| `CONTROL_DELETE` | 302 | Delete item button |
| `CONTROL_MOVE_UP` | 303 | Move up button |
| `CONTROL_MOVE_DOWN` | 304 | Move down button |
| `CONTROL_SET_LABEL` | 305 | Change label button |
| `CONTROL_SET_ICON` | 306 | Change icon button |
| `CONTROL_SET_ACTION` | 307 | Change action button |
| `CONTROL_RESTORE_DELETED` | 311 | Restore deleted item |
| `CONTROL_RESET_ITEM` | 312 | Reset item to defaults |
| `CONTROL_TOGGLE_DISABLED` | 313 | Enable/disable item |
| `CONTROL_CHOOSE_SHORTCUT` | 401 | Choose from groupings |
| `CONTROL_EDIT_SUBMENU` | 405 | Edit submenu |

---

## ListItem Properties

Properties set on each item in the list (control 211):

| Property | Description |
|----------|-------------|
| `name` | Item's internal name |
| `path` | Item's action |
| `originalAction` | Original action before overrides |
| `skinshortcuts-disabled` | "True" if item is disabled |
| `widget` | Widget name |
| `widgetLabel` | Widget display label |
| `widgetPath` | Widget content path |
| `widgetType` | Widget type |
| `widgetTarget` | Widget target window |
| `background` | Background name |
| `backgroundLabel` | Background display label |
| `backgroundPath` | Background image path |
| `hasSubmenu` | "true" if item has submenu items |
| `submenu` | Submenu name |
| `isResettable` | "true" if item is modified from skin defaults |

### Visibility Example

To show reset button only when item can be reset:

```xml
<control type="button" id="312">
    <visible>Container(211).ListItem.Property(isResettable)</visible>
    ...
</control>
```
