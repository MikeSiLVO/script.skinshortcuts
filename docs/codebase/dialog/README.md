# dialog/ Package

**Path:** `resources/lib/skinshortcuts/dialog/`
**Purpose:** Management dialog for skin shortcuts - the main UI for editing menus.

***

## Overview

Implements WindowXMLDialog for editing menus, items, widgets, backgrounds, and custom properties. Uses mixin pattern to separate concerns.

***

## Modules

| File | Doc | Purpose |
|------|-----|---------|
| `__init__.py` | [init.md](init.md) | Public API, ManagementDialog class |
| `base.py` | [base.md](base.md) | Core initialization, list management, events |
| `items.py` | [items.md](items.md) | Item operations (add, delete, move) |
| `pickers.py` | [pickers.md](pickers.md) | Shortcut and widget picker dialogs |
| `properties.py` | [properties.md](properties.md) | Property management (widget, background) |
| `subdialogs.py` | [subdialogs.md](subdialogs.md) | Subdialog and submenu handling |

***

## Architecture

```
ManagementDialog
    ← SubdialogsMixin      (subdialogs.py)
    ← PropertiesMixin      (properties.py)
    ← PickersMixin         (pickers.py)
    ← ItemsMixin           (items.py)
    ← DialogBaseMixin      (base.py)
        ← xbmcgui.WindowXMLDialog
```

***

## Control IDs

| ID | Purpose |
|----|---------|
| 211 | Menu items list |
| 301-307 | Add, Delete, Move Up/Down, Set Label/Icon/Action |
| 311-313 | Restore Deleted, Reset Item, Toggle Disabled |
| 401 | Choose Shortcut |
| 405 | Edit Submenu |

***

## ListItem Properties

Properties set on items in list control 211:

| Property | Description |
|----------|-------------|
| `name` | Item's internal name |
| `path` | Item's action |
| `widget`, `widgetLabel`, `widgetPath`, `widgetType`, `widgetTarget` | Widget properties |
| `background`, `backgroundLabel`, `backgroundPath` | Background properties |
| `hasSubmenu`, `submenu` | Submenu info |
| `isResettable` | True if modified from defaults |
| `skinshortcuts-disabled` | True if disabled |
