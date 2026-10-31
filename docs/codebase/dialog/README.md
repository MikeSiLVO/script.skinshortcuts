# dialog/

The management dialog, opened by `type=manage`, plus the view selection dialogs. Control IDs, window properties and ListItem properties the skin sees are documented in [skinning/management-dialog.md](../../skinning/management-dialog.md).

## Composition

`ManagementDialog` (in `__init__.py`) is a `WindowXMLDialog` built from mixins:

```
ManagementDialog(SubdialogsMixin, PropertiesMixin, PickersMixin, ItemsMixin, DialogBaseMixin)
```

`DialogBaseMixin` subclasses `xbmcgui.WindowXMLDialog` and declares a stub for every handler another mixin implements; the stubs raise `NotImplementedError` and the mixins before it in the MRO supply the real ones. The other mixins declare the sibling methods they call in `if TYPE_CHECKING:` blocks. Static tools resolve such a call to the local stub, so find the callers of a dialog method by grepping `self.<name>(`.

| Module | Owns |
|--------|------|
| `base.py` | Setup from kwargs, `onInit`, the item list (211) and the edited-item list (212), ListItem and window properties, `onClick` routing, `onAction`, `close` |
| `items.py` | Add, delete, move, label, icon, action, disable, restore, reset, the context menu, and `_set_item_property`, which the property handlers write through |
| `pickers.py` | The shortcut, widget and background pickers, the generic hierarchy picker, content resolution and browse-into; module-level picker helpers the other modules share |
| `properties.py` | Property buttons from properties.xml: the `requires` check, routing by type, widget and background sibling writes, playlist picking |
| `subdialogs.py` | Child dialogs: submenu editing, menus.xml subdialogs, onclose actions, custom widget menu references |
| `views.py` | The view browser and view picker, plain functions built on `picker_select`, called by `entry.view_select` |

## Setup and routing

- `show_management_dialog` opens `script-skinshortcuts.xml` from the skin and returns whether the dialog saved; `entry` then forces a build.
- On `onInit` a root dialog creates its `MenuManager`, which loads `SkinConfig` with userdata, and reads properties.xml for the property schema and menus.xml for icon sources, the context menu and subdialogs. The shortcut picker reads groupings from menus.xml, and the widget picker reads widgets.xml, each time it opens; the background picker uses the manager's config.
- `onClick` sends the built-in control IDs to their handlers, a subdialog's `buttonID` to `_spawn_subdialog`, and any other ID to `_handle_property_button`. The context menu routes the chosen row through `onClick`, so it reaches the same handlers.
- Writes go through the manager, then the list is rebuilt from `items`, which is the manager's working list. See [CONCEPTS.md](../CONCEPTS.md#skin-defaults-the-working-copy-and-the-userdata-diff).

## Child dialogs

A child is another `ManagementDialog` (`_run_child_dialog`) that receives the parent's manager, content provider, property schema, icon sources, context menu and subdialogs.

- `is_child` is true for any dialog given a manager. Only the root saves, on close; a child's edits sit in the shared manager until then.
- While a child is open the parent sets the window property `additionalDialog`, and when the last child closes it mirrors its own dialog mode and suffix back to Home.
- Submenu editing opens the item's per-item submenu, in mode `widgets` when the linked template is a widgets menu.
- A subdialog with a `mode` opens a child on the same menu with that mode, its `suffix` as `property_suffix`, its `setfocus`, and the selected row pinned (`selected_index`), so list 212 shows the item being edited. Deleting that item closes the child. When the child closes, the first `menu` onclose action whose condition holds opens that menu.
- A subdialog with a `menu` and no `mode` opens that menu directly.
- A menu opened by an onclose action or a `menu`-only subdialog runs in mode `custom-` plus the subdialog's mode, or `customwidget` when the subdialog has none.
- Every dialog mirrors its mode and suffix to Home (`skinshortcuts-dialog`, `skinshortcuts-suffix`), so a Kodi dialog opened over it can read them.

## Pickers

- The pickers are built on `_pick_from_hierarchy`, which walks groups with back navigation, filters each level by property condition and Kodi visibility, and resolves `<content>` elements as it reaches them. Returning `False` means the user picked "None".
- `<content>` resolves through one `ContentProvider` per dialog tree: the root creates it on first use and children receive it, so its cache lasts until the root closes ([providers/README.md](../providers/README.md)).
- Browse-into lists paths through `BrowseProvider`. A media source shortcut can instead become a generated smart playlist (`playlists.py`).
- While a picker is open, `skinshortcuts-picker` is set on Home (`picker_context`, `picker_select`) so the skin can tell which picker DialogSelect is showing.
- `skinstring.py` reuses `PickersMixin` outside the dialog through `_StandalonePicker`.
