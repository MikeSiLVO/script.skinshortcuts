# File Formats

What the add-on writes to disk and how each file is keyed. The skin-facing summary is in [skinning/files.md](../skinning/files.md); this page carries the detail a maintainer needs.

## Per-skin data folder

Everything the add-on keeps lives in `special://profile/addon_data/script.skinshortcuts/` (`constants.DATA_DIR`). The folder is shared by every skin, so each file carries the active skin's add-on id (`xbmc.getSkinDir()`, written `<skin>` below).

| File | Written by | Holds |
|------|------------|-------|
| `<skin>.userdata.json` | `userdata.save_userdata` | The user's menu changes and view selections |
| `<skin>.userdata.json.tmp` | `userdata.save_userdata` | A save in progress, renamed over the userdata file once written |
| `<skin>.userdata.json.bak` | `userdata.load_userdata` | A copy of a userdata file that could not be parsed |
| `<skin>.hashes` | `hashing.write_hashes` | Hashes for rebuild detection |
| `<skin>.unsupported-ack` | `entry._warn_unsupported` | Marker: the user chose to ignore the warning for a skin with no v3 config |
| `playlists/<skin>/source-<menu>-<item>.xsp` | `playlists.save_playlist` | Smart playlists generated for source shortcuts, characters outside `A-Za-z0-9_-` replaced by `_` |

The includes file is `script-skinshortcuts-includes.xml`, written into every resolution folder the skin's addon.xml lists under its `xbmc.gui.skin` extension (`entry.get_output_paths`), or into the folder passed as `output` to `buildxml`. It is written through a binary handle so line endings stay LF.

## userdata.json

A diff against the skin's menus.xml, plus view selections. Loaded into `userdata.UserData`. `MenuManager.save` writes menu changes, the view and reset actions in entry.py write their own changes, and `build_includes` writes it back after migrations rewrite it.

```json
{
  "menus": {
    "mainmenu": {
      "items": [
        {"name": "movies", "label": "My Movies", "properties": {"customWidget": "custom-3f9a1c2e"}, "position": 0},
        {"name": "user-1a2b3c4d", "label": "Weather", "actions": [{"action": "ActivateWindow(Weather)"}], "icon": "DefaultShortcut.png", "is_new": true, "position": 3}
      ],
      "removed": ["tvshows"]
    },
    "mainmenu/movies": {
      "items": [{"name": "movies-sets", "disabled": true, "position": 2}],
      "removed": ["movies-genres"]
    },
    "custom-3f9a1c2e": {
      "items": [{"name": "random-movies", "label": "Random Movies", "actions": [], "icon": "DefaultMovies.png", "properties": {"widgetPath": "special://skin/playlists/random.xsp", "widgetType": "movies"}, "is_new": true, "position": 0}]
    }
  },
  "views": {
    "library": {"movies": "51"},
    "plugins": {"movies": "50"},
    "plugin.video.example": {"movies": "52"}
  }
}
```

### Menu keys

| Key | Menu |
|-----|------|
| A menu name from menus.xml | A root `<menu>`, or a `<submenu>` no item links to |
| `{menu}/{item}` | The per-item submenu of root item `item` in `menu` |
| `custom-` plus 8 hex characters | A custom widget menu |
| Any other name | A menu the dialog opened from a subdialog `menu` reference, such as `{item}.1` resolved to `movies.1` |

See [CONCEPTS.md](CONCEPTS.md) for how each kind is created and merged.

### Item keys

`name` and `position` are always present; every other key appears when it differs from the skin default. A user-added item (`is_new`) is stored in full.

- `actions`: a list of `{"action", "condition"}` objects, `condition` left out when empty. A plain string in the list reads as an unconditional action.
- `properties`: changed or added properties, keys spelled as properties.xml declares them. Widget and background siblings appear only when the skin cannot derive them (see [Derived widget and background properties](CONCEPTS.md#derived-widget-and-background-properties)).
- `removed_properties`: default properties the user cleared.
- `position`: the item's index in the merged menu, counting items a visible= condition hides.
- `submenu`: the `<submenu>` template the item links; an empty string clears a link the default has.
- `visible`: a `<visible>` condition copied from a picked shortcut.

### Views

Each key of `views` is a source: `library`, `plugins` for every plugin without its own selection, or a plugin id. Each source maps a views.xml content name to a view id. A selection the content rule does not list is ignored at build time.

A file that does not parse loads as empty defaults after a `.bak` copy is made, and stays on disk until the next save replaces it.

## Generated includes

The includes file has an `<includes>` root holding, in this order:

| Element | Source | Content |
|---------|--------|---------|
| `skinshortcuts-{menu}` | `IncludesBuilder` | One entry per enabled item of a root menu, an `<item>` or a `<control>` when the menu sets `controltype` |
| `skinshortcuts-{menu}-submenu` | `IncludesBuilder` | Every enabled item of the menu's per-item submenus, each with a `parent` property |
| `skinshortcuts-{item}-customwidget`, `skinshortcuts-{item}-customwidget{N}` | `IncludesBuilder` | The custom widget menu in the item's base slot or slot N |
| `skinshortcuts-{template}` | `IncludesBuilder` | Items of a menus.xml `<submenu>` template, taken from the first non-empty per-item instance seeded from it; left out with `standalone="false"` |
| `<variable>` | `TemplateBuilder` | Variables templates build, merged by name |
| `skinshortcuts-template-{include}` | `TemplateBuilder` | One per templates.xml `<template>` output, merged by name |
| `skinshortcuts-{include}` | `TemplateBuilder` | One per templates.xml `<submenu>` template |
| `<expression>` | `ViewExpressionBuilder` | View locking expressions |

Menu includes come in groups per root menu: the menu, its submenu include, then its custom widget includes. [builders/README.md](builders/README.md) says which menus get includes and what an entry holds.

## Hashes file

A JSON object of strings, `null` where a file is missing.

| Key | Value |
|-----|-------|
| `menus.xml`, `widgets.xml`, `backgrounds.xml`, `properties.xml`, `templates.xml`, `views.xml` | MD5 of each config file |
| `visible` | MD5 over every distinct visible= condition on menus.xml items with its current result; `null` when there are none |
| `userdata` | MD5 of the userdata file |
| `script_version` | The add-on's version |
| `skin_dir` | The skin's add-on id |
| `kodi_version` | Kodi's major version |
| `includes:{output folder}` | MD5 of the includes file written to that folder |

`needs_rebuild` asks for a build when no hashes are stored, an includes file is missing or differs from its stored hash, or any other key differs. Nothing hashes the add-on's code, so a code change without a version bump matches every hash; a test build after editing code needs `force=true`.
