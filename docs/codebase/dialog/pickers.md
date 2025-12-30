# dialog/pickers.py

**Path:** `resources/lib/skinshortcuts/dialog/pickers.py`
**Purpose:** Shortcut and widget picker dialogs.

***

## Overview

PickersMixin provides picker dialogs for selecting shortcuts and widgets with hierarchical navigation.

***

## PickersMixin Class

### Shortcut Picker

| Method | Purpose |
|--------|---------|
| `_choose_shortcut` | Choose shortcut from groupings, apply to item |
| `_pick_from_groups` | Show group picker with back navigation |
| `_pick_from_group_items` | Pick from items within a group |

### Widget Picker

| Method | Purpose |
|--------|---------|
| `_pick_widget_from_groups` | Show widget picker, returns Widget/None/False |
| `_pick_widget_from_group_items` | Pick from widget group items |
| `_pick_widget_flat` | Pick from flat widget list |

**Returns:** Widget if selected, None if cancelled, False if "None" chosen (clear widget)

### Content Resolution

| Method | Purpose |
|--------|---------|
| `_resolve_content_to_shortcuts` | Resolve Content to Shortcut objects |
| `_resolve_content_to_widgets` | Resolve Content to Widget objects |

### Helpers

| Method | Purpose |
|--------|---------|
| `_extract_path_from_action` | Extract path for widget use |
| `_map_target_to_window` | Map content target to window |
| `_nested_picker` | Generic picker with back navigation |
