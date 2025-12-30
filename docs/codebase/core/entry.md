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
| `resetall` | Reset to skin defaults |
| `clear` | Clear custom widget menu |

### Parameters

**buildxml:** `path`, `output`, `force`

**manage:** `menu` (default: mainmenu), `path`

**clear:** `menu`, `property`

***

## Action Functions

### build_includes(shortcuts_path, output_path, force) → bool

Build includes.xml. Uses hash-based skip unless force=True. Writes to all skin resolution folders.

### clear_custom_menu(menu, property_name, shortcuts_path) → bool

Clear custom widget menu and optionally reset parent property.

### reset_all_menus(shortcuts_path) → bool

Reset all menus to skin defaults (deletes userdata). Shows confirmation dialog.

***

## Helper Functions

| Function | Description |
|----------|-------------|
| `get_skin_path()` | Get `special://skin/shortcuts/` path |
| `get_output_paths()` | Get resolution folder paths from addon.xml |
