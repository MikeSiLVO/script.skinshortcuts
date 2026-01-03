# entry.py

**Path:** `resources/lib/skinshortcuts/entry.py`
**Purpose:** Entry point for RunScript invocations.

***

## main()

Main entry point. Parses arguments and routes to appropriate action.

### Actions (type parameter)

| Type | Description |
|------|-------------|
| `buildxml` | Build includes.xml (default) |
| `manage` | Open management dialog |
| `viewselect` | Open view selection dialog |
| `resetall` | Reset everything to skin defaults |
| `resetmenus` | Reset menus only (preserves views) |
| `resetviews` | Reset view selections only |
| `resetsubmenus` | Reset all submenus (menus defined with `<submenu>` tag) |
| `reset` | Reset specific menu (follows submenu references if `submenus=true`) |
| `clear` | Clear custom widget menu |

### Parameters

**buildxml:** `path`, `output`, `force`

**manage:** `menu` (default: mainmenu), `path`

**viewselect:** `content`, `plugin`, `path`

**reset:** `menu`, `submenus`, `path`

**clear:** `menu`, `item`, `suffix`, `property`, `path`

***

## Action Functions

### build_includes(shortcuts_path, output_path, force) → bool

Build includes.xml. Uses hash-based skip unless force=True. Writes to all skin resolution folders.

### clear_custom_widget(menu, item, suffix, property_name, shortcuts_path) → bool

Clear custom widget menu for an item. Removes the menu contents and optionally clears related properties.

### reset_all_menus(shortcuts_path) → bool

Reset all menus and views to skin defaults (deletes userdata). Shows confirmation dialog.

### reset_menus(shortcuts_path) → bool

Reset menus to skin defaults, preserving view selections. Shows confirmation dialog.

### reset_views(shortcuts_path) → bool

Reset all view selections to defaults, preserving menus. Shows confirmation dialog.

### view_select(content, plugin, shortcuts_path) → bool

Open view selection dialog. If `content` provided, opens direct picker. If `plugin` also provided, sets plugin-specific override.

***

## Helper Functions

| Function | Description |
|----------|-------------|
| `get_skin_path()` | Get `special://skin/shortcuts/` path |
| `get_output_paths()` | Get resolution folder paths from addon.xml |
