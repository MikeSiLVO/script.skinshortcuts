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
| `_choose_shortcut` | Choose shortcut from groupings, apply all actions to item |
| `_get_shortcut_actions` | Get all actions from shortcut (handles browse/playlist modes) |
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

### Input Handling

| Method | Purpose |
|--------|---------|
| `_handle_input_selection` | Show keyboard for Input item, return Shortcut |

### Browse Into

| Method | Purpose |
|--------|---------|
| `_browse_path` | Browse directory with "Create menu item to here" option |
| `_is_browsable` | Object opted-in via `browse` + `<path>` (Widget bool, Shortcut window name) |
| `_get_browse_info_from_shortcut` | Extract path and window from opted-in shortcut |
| `_get_browse_placeholder_for_content` | Create placeholder shortcut for addon content |

### Addon Placeholder Behavior

For `source="addons"` content, `_get_browse_placeholder_for_content` creates a placeholder shortcut that:

1. Displays "Create menu item to here" in the picker (uses `label` field)
2. Stores `content.label` in the `type` field for use as the result label
3. When selected, `_choose_shortcut` uses `type` as the menu item label if set

This allows users to create shortcuts to addon categories even when empty, with proper labeling.

### Helpers

| Method | Purpose |
|--------|---------|
| `_map_target_to_window` | Map content target to window |
