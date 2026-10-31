# Core Modules

The modules at the top of `resources/lib/skinshortcuts/`. Rules that span several of them are in [CONCEPTS.md](../CONCEPTS.md) and file layouts in [FORMATS.md](../FORMATS.md); this page says what each module is responsible for beyond its docstrings.

## entry.py

Every RunScript call lands here; `default.py` calls `main`.

- `main` accepts `key=value` arguments or a single query string, and holds any `prop`/`value` pairs as Home window properties until the action returns ([pass-through](../../skinning/management-dialog.md#window-property-pass-through)).
- `_dispatch` runs the action named by `type`, `buildxml` when it is absent:
  - `buildxml`: `build_includes`
  - `manage`: `dialog.show_management_dialog`, then a forced build when the dialog saved
  - `resetall`, `resetmenus`, `resetviews`: `reset_all`, `reset_menus`, `reset_views`
  - `reset`: `MenuManager.reset_menu`, or `reset_menu_tree` with `submenus=true`
  - `resetsubmenus`: `MenuManager.reset_all_submenus`
  - `clear`: `clear_custom_widget`
  - `viewselect`: `view_select`
  - `skinstring`: `skinstring.pick_widget_skinstring`
  - `playchannel`: `play_channel`
- Every action that changes userdata ends with `build_includes(force=True)`. Only a plain `buildxml` consults the hashes, unless it passes `force=true`.
- `_skin_supported` gates every action on v3 config: menus.xml, or for anything but `manage`, views.xml. A skin without it is taken for a v2 skin; the action stops and a modal offers the skin settings or the add-on browser. For a skin that already has an includes file, the automatic warning from `buildxml` shows once per session, and the user can silence it for that skin, which writes the `.unsupported-ack` marker.
- The build flow is in [OVERVIEW.md](../OVERVIEW.md#build-pipeline).

## config.py

- `SkinConfig.load` is the full config load; the build, `MenuManager` and `view_select` all use it. The steps are in [OVERVIEW.md](../OVERVIEW.md#config-load) and the merge rules in [CONCEPTS.md](../CONCEPTS.md).
- Widgets, backgrounds and their picker groupings are properties over the loaded `WidgetConfig` and `BackgroundConfig`. `get_widget` and `get_background` search the top level first, then nested groups.
- `migrated` counts the userdata changes migrations made during the load.
- Derived widget and background properties and action overrides are applied here at build time ([CONCEPTS.md](../CONCEPTS.md#derived-widget-and-background-properties)).

## manager.py

`MenuManager` is the dialog's model over a working copy of the menus ([CONCEPTS.md](../CONCEPTS.md#skin-defaults-the-working-copy-and-the-userdata-diff)).

- Every mutation sets `_changed`, and `save()` does nothing without it. Setting an item's field or property also clears its `is_placeholder`.
- Reset scope:
  - `reset_menu`: a skin menu goes back to its default; a per-item key is reseeded from its item's template, or emptied when the item has none; any other menu is emptied.
  - `reset_menu_tree`: the menu, then each of its items' per-item submenus, guarding against cycles.
  - `reset_all_submenus`: every menu whose default is a `<submenu>`, per-item instances included. Menus with no skin default, such as custom widget menus, stay.
- After a successful save, `save()` deletes generated source playlists that no remaining action references.

## userdata.py

- Reads and writes the userdata file ([FORMATS.md](../FORMATS.md#userdatajson)) and holds the merge (`merge_items`, `merge_menu`).
- `save_userdata` writes a temp file and renames it over the target, retrying once on an `OSError`, after half a second inside Kodi. `load_userdata` turns a file it cannot parse into empty defaults, copying it to `.bak` first.
- The view helpers on `UserData` treat every `views` key other than `library` and `plugins` as a plugin id.

## migrations.py

Rewrites loaded userdata for names the skin retired; see [Overrides and retired names](../CONCEPTS.md#overrides-and-retired-names).

## hashing.py

Rebuild detection; the keys and the comparison are in [FORMATS.md](../FORMATS.md#hashes-file).

## conditions.py

- The property condition language, used wherever a config file holds a property condition: templates, properties.xml options and fallbacks, picker filters, context menu rows, onclose actions. The syntax is in [skinning/conditions.md](../../skinning/conditions.md).
- `evaluate_condition` normalizes keywords and expands compact OR before evaluating. A `true` or `false` right-hand side compares ignoring case.
- `check_visible` is the separate path for Kodi visibility conditions; it passes outside Kodi.
- The suffix and case rules are in [CONCEPTS.md](../CONCEPTS.md#property-slots-and-suffixes).

## expressions.py

`$MATH[...]` and `$IF[...]` for templates ([syntax](../../skinning/templates.md#dynamic-expressions)). `MathEvaluator` is a recursive descent parser; a property it reads that is missing or not a number counts as 0, and an expression that fails is reported through `notify` and left as written. `$IF` conditions use conditions.py.

## localize.py

- `resolve_label` turns `$LOCALIZE[...]`, `$ADDON[...]`, `$NUMBER[...]`, a bare string id or another `$` info label into display text, and returns the label unchanged outside Kodi. Models and the includes file keep labels unresolved; the dialog resolves them for display.
- `number_label` wraps a digit-only label in `$NUMBER[...]`, since Kodi reads a bare number as a string id.
- `LANGUAGE` reads this add-on's strings.po.

## log.py

- `get_logger(component)` gives one cached `Logger` per component; lines read `script.skinshortcuts: {component} - {msg}`. The add-on's `debug` setting promotes debug lines to info and never suppresses anything. Outside Kodi every line goes to stdout, so modules run under the tests.
- `notify(heading, message, detail)` is the one path for skinner-facing config errors: the detail goes to the log at warning level and a toast ending "(see log)" goes to the screen, each once per identical text per run. The standard form is heading `<Feature> Error`, message led by the offending name in quotes, detail `<file>: <what was written>; <what the script did>; <how to fix>`. These strings are English on purpose, outside strings.po. A new notification gets a row in [skinning/troubleshooting.md](../../skinning/troubleshooting.md).

## constants.py

File names, `DATA_DIR`, the sibling suffix tuples (`WIDGET_SIBLINGS`, `WIDGET_EXTRAS`, `BACKGROUND_SIBLINGS`) that the dialog, migrations and `entry.clear_custom_widget` share, the target and window maps, and the builtin parameter helpers (`split_params`, `extract_window_from_action`, `extract_path_from_action`).

## exceptions.py

`SkinShortcutsError`, then `ConfigError` with one subclass per config file. The loaders raise them; see [loaders/README.md](../loaders/README.md#errors).

## playlists.py

Source shortcuts and smart playlists. When the user picks a media source, `display_options` offers the Files view plus library views for the domain the source's folders hold content in (`detect_domain`, which probes library queries). A library choice builds a path-filtered smart playlist (`build_smartplaylist_xml`), saves it per skin and item (`save_playlist`, [FORMATS.md](../FORMATS.md#per-skin-data-folder)), and the shortcut's action opens it. The module also holds the smart playlist parsing, playlists folder and multipath helpers that `providers/content.py` and the background playlist picker use.

## skinstring.py

`type=skinstring`: the widget picker without the management dialog. `_StandalonePicker` supplies the few dialog methods `PickersMixin` calls; the pick goes into the skin strings named by `skinPath`, `skinLabel`, `skinType` and `skinTarget`, and picking "None" resets them. Skinner view: [Standalone Widget Picker](../../skinning/widgets.md#standalone-widget-picker).
