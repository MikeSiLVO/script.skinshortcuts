# Overview

Skin Shortcuts lets a Kodi skin declare menus, widgets, backgrounds, custom properties, templates and view rules in XML under `special://skin/shortcuts/`. Users customize the menus in a management dialog, the add-on stores their changes as a diff, and every build merges the two and writes `script-skinshortcuts-includes.xml`, which the skin includes. The file map is in [INDEX.md](INDEX.md).

```
default.py -> entry.main -> _dispatch
  buildxml     build_includes -> hashing.needs_rebuild -> SkinConfig.load -> builders/ -> includes file
  manage       dialog/ ManagementDialog -> MenuManager -> userdata file, then a forced build
  viewselect   dialog/views.py -> userdata views, then a forced build
  skinstring   skinstring.py -> PickersMixin -> skin strings
  reset, ...   MenuManager or userdata.py, then a forced build
```

## Entry

`default.py` calls `entry.main`, which parses the RunScript arguments and dispatches on `type`. The action map and the v3 config check are in [core/README.md](core/README.md#entrypy); the skin-facing commands are in [skinning/management-dialog.md](../skinning/management-dialog.md#script-commands).

## Config load

`SkinConfig.load(shortcuts_path)` in `config.py`:

1. The loaders parse menus.xml, widgets.xml, backgrounds.xml, templates.xml, properties.xml and views.xml into models. menus.xml goes first, as backgrounds.xml needs its icon overrides.
2. `load_userdata` reads the user's diff, and `migrations.apply_overrides` rewrites it for any names the skin retired.
3. Each root `<menu>` is merged with its diff (`merge_menu`). Each of its items that links a `<submenu>`, or has a stored submenu diff, gets a per-item submenu instance. A `<submenu>` no item links stays as a flat menu, merged with any diff stored under its name. Menus that exist only in userdata, such as custom widget menus, are built from their diffs.

The result holds the merged `menus`, the untouched `default_menus`, and the widget, background, template, property and view config. The rules behind step 3 are in [CONCEPTS.md](CONCEPTS.md).

## Build pipeline

`entry.build_includes`:

1. Returns at once when the Home property `skinshortcuts-isbuilding` shows a build already running, and sets it otherwise.
2. Checks the skin has v3 config, and finds the output folders from the skin's addon.xml unless `output` is given.
3. Unless forced, asks `hashing.needs_rebuild` and stops when nothing changed.
4. Loads `SkinConfig`, then for each output folder calls `SkinConfig.build_includes`, which:
   - fills derived widget and background properties into the merged menus;
   - applies action overrides to copies of the menus;
   - runs `IncludesBuilder`, which emits the menu, submenu and custom widget includes, then runs `TemplateBuilder` when templates.xml has templates or submenu templates and `ViewExpressionBuilder` when views.xml has content rules;
   - writes the file.
5. Saves the userdata when migrations changed it, then writes the hashes, including one per includes file.
6. Runs `ReloadSkin()` when any includes file changed, after waiting for open modal dialogs to close.

Details per builder: [builders/README.md](builders/README.md) and [builders/template.md](builders/template.md).

## Rebuild detection

A plain `buildxml` builds only when something it hashes changed; every action that writes userdata forces the build instead. The hashes are listed in [FORMATS.md](FORMATS.md#hashes-file).

## Management dialog

`type=manage` opens `ManagementDialog`, a `WindowXMLDialog` composed of mixins, on the skin's `script-skinshortcuts.xml`. The root dialog creates a `MenuManager`, which loads `SkinConfig` and keeps a working copy of the menus. Submenus, widget slots and custom widget menus open in child dialogs that share the root's manager. When the root closes with changes, the manager saves the diff, and `entry` forces a build. See [dialog/README.md](dialog/README.md).

## Pickers and providers

The shortcut picker reads groupings from menus.xml for the open menu; the widget and background pickers use widgets.xml and backgrounds.xml. `<content>` entries resolve at pick time through `providers/content.py`; browse-into lists paths through `providers/browse.py`; a media source can become a generated smart playlist through `playlists.py`. `skinstring.py` reuses the widget picker outside the dialog. See [providers/README.md](providers/README.md).

## View locking

views.xml declares views and content rules, and userdata holds the user's choice per content. The build turns them into Kodi `<expression>` elements in the includes file; `type=viewselect` changes the choices. See [View locking](CONCEPTS.md#view-locking).
