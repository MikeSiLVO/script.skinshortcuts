# dialog/pickers.py

**Path:** `resources/lib/skinshortcuts/dialog/pickers.py`
**Lines:** 523
**Purpose:** Shortcut and widget picker dialogs.

---

## Overview

PickersMixin provides picker dialogs for selecting shortcuts from groupings and widgets from widget groups. Supports hierarchical navigation with back functionality.

---

## PickersMixin Class (line 31)

### Shortcut Picker

#### _choose_shortcut() (line 54)

Choose a shortcut from groupings.

**Behavior:**
1. Load groupings from menus.xml
2. Show group picker
3. Apply selected shortcut to current item (label, action, icon)

#### _pick_from_groups(groups, item_props) → Shortcut | None (line 85)

Show group/shortcut picker dialog with back navigation.

**Parameters:**
- `groups` - List of Group objects to pick from
- `item_props` - Current item properties for condition evaluation

**Returns:** Selected shortcut, or None if cancelled

#### _pick_from_group_items(group, item_props) → Shortcut | None (line 118)

Pick from items within a group with back navigation.

**Handles:**
- Shortcuts - Direct selection
- Groups - Recursive navigation
- Content - Dynamic resolution to shortcuts

---

### Widget Picker

#### _pick_widget_from_groups(items, item_props, slot) → Widget | None | False (line 205)

Show widget picker dialog with back navigation.

**Parameters:**
- `items` - Widget groups and/or widgets to pick from
- `item_props` - Current item properties for condition evaluation
- `slot` - Current widget slot being edited (used to find current widget for preselect)

**Returns:**
- Widget if selected
- None if cancelled completely
- False if "None" chosen (clear widget)

**Behavior:**
- Preselects current widget based on `item_props[slot]`
- Remembers selection when navigating back from sub-dialogs

#### _pick_widget_from_group_items(group, item_props, slot) → Widget | None (line 279)

Pick from items within a widget group with back navigation.

**Behavior:**
- Auto-selects if only one widget in group
- Handles nested groups recursively
- Resolves Content to widgets dynamically
- Remembers selection for back navigation

#### _pick_widget_flat(widgets, item_props, slot) → Widget | None | False (line 352)

Pick from flat widget list (when no groupings defined).

**Parameters:**
- `widgets` - List of (name, label, icon) tuples
- `item_props` - Current item properties for finding current widget (optional)
- `slot` - Widget slot name for preselect lookup (optional)

---

### Content Resolution

#### _resolve_content_to_shortcuts(content) → list[Shortcut] (line 388)

Resolve a Content reference to Shortcut objects.

Uses ContentProvider to query Kodi APIs.

#### _resolve_content_to_widgets(content) → list[Widget] (line 364)

Resolve a Content reference to Widget objects.

Converts resolved shortcuts to widgets with appropriate paths.

---

### Helper Methods

#### _extract_path_from_action(action) → str (line 406)

Extract the path from an action string for widget use.

**Handles:**
- `ActivateWindow(Window,path,return)` → path
- `PlayMedia(path)` → path
- `RunAddon(addonid)` → `plugin://addonid/`

#### _map_target_to_window(target) → str (line 425)

Map content target to widget target window.

Uses TARGET_MAP from constants.

#### _nested_picker(title, items, on_select, show_none, current_value) (line 461)

Generic picker that supports sub-dialogs with back navigation.

**Parameters:**
- `title` - Dialog title
- `items` - List of (id, label, icon) tuples
- `on_select` - Callback when item selected
- `show_none` - Whether to show "None" option (default True)
- `current_value` - Current item ID to preselect (default "")

**Returns:**
- Result from on_select
- "none" if None chosen
- False if cancelled completely

**Behavior:**
- Preselects item matching `current_value`
- Remembers selection when navigating back from sub-dialogs
