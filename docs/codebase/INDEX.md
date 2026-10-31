# Codebase Docs

Internal docs for script.skinshortcuts: what the add-on does, where each part lives and how the parts fit together. Every class, function and method has a docstring, and those are the API reference; these pages cover what no single docstring can. Skinner-facing behavior lives in [docs/skinning/](../skinning/index.md).

## Pages

| Page | Covers |
|------|--------|
| [OVERVIEW.md](OVERVIEW.md) | Architecture and data flow: entry, config load, build pipeline, rebuild detection, dialog, pickers |
| [CONCEPTS.md](CONCEPTS.md) | Rules that span modules: the userdata diff, derived properties, hidden items, per-item submenus, custom widget menus, slots, overrides, view locking |
| [FORMATS.md](FORMATS.md) | The per-skin data folder, userdata.json, generated includes, the hashes file |
| [core/README.md](core/README.md) | The top-level modules |
| [builders/README.md](builders/README.md) | Includes and view expression builders |
| [builders/template.md](builders/template.md) | The template builder's stages |
| [dialog/README.md](dialog/README.md) | The management dialog's mixins, child dialogs, pickers |
| [loaders/README.md](loaders/README.md) | Config file loaders |
| [models/README.md](models/README.md) | Config models |
| [providers/README.md](providers/README.md) | Content and browse providers |

## File map

Paths are relative to `resources/lib/skinshortcuts/`, except `default.py` at the add-on root.

| File | Purpose | Docs |
|------|---------|------|
| `default.py` | Add-on script; calls `entry.main` | [OVERVIEW](OVERVIEW.md#entry) |
| `__init__.py` | Package docstring only | |
| `entry.py` | RunScript dispatch; build, reset, clear and view actions; the v3 config check | [core](core/README.md#entrypy) |
| `config.py` | `SkinConfig`: loads every config file, merges userdata, builds the includes file | [core](core/README.md#configpy) |
| `manager.py` | `MenuManager`: the dialog's working copy of the menus, saved as a diff | [core](core/README.md#managerpy) |
| `userdata.py` | Userdata file reading and writing, and the merge of skin defaults with user diffs | [core](core/README.md#userdatapy) |
| `migrations.py` | Rewrites userdata for names the skin retired | [core](core/README.md#migrationspy) |
| `hashing.py` | Hashes for rebuild detection | [core](core/README.md#hashingpy) |
| `conditions.py` | Property condition evaluation, case-insensitive property lookup, suffix rules | [core](core/README.md#conditionspy) |
| `expressions.py` | `$MATH` and `$IF` evaluation | [core](core/README.md#expressionspy) |
| `localize.py` | Label resolution and this add-on's strings | [core](core/README.md#localizepy) |
| `log.py` | Component loggers and skinner-facing notifications | [core](core/README.md#logpy) |
| `constants.py` | File names, the data folder, sibling suffixes, target maps, builtin parameter parsing | [core](core/README.md#constantspy) |
| `exceptions.py` | Config error hierarchy | [core](core/README.md#exceptionspy) |
| `playlists.py` | Smart playlists for source shortcuts, playlist folder helpers | [core](core/README.md#playlistspy) |
| `skinstring.py` | The widget picker outside the dialog, writing skin strings | [core](core/README.md#skinstringpy) |
| `builders/__init__.py` | Package docstring only | |
| `builders/includes.py` | Menu, submenu and custom widget includes; runs the other builders and writes the file | [builders](builders/README.md) |
| `builders/template.py` | Includes and variables from templates.xml | [template](builders/template.md) |
| `builders/views.py` | View locking expressions | [builders](builders/README.md#view-expressions) |
| `dialog/__init__.py` | Composes `ManagementDialog`; `show_management_dialog`; re-exports the control IDs | [dialog](dialog/README.md#composition) |
| `dialog/base.py` | Dialog setup, list controls, ListItem and window properties, event routing | [dialog](dialog/README.md) |
| `dialog/items.py` | Item operations, the context menu, property writes | [dialog](dialog/README.md) |
| `dialog/pickers.py` | Shortcut, widget and background pickers; shared picker helpers | [dialog](dialog/README.md#pickers) |
| `dialog/properties.py` | Property buttons from properties.xml | [dialog](dialog/README.md) |
| `dialog/subdialogs.py` | Child dialogs, onclose actions, custom widget menu references | [dialog](dialog/README.md#child-dialogs) |
| `dialog/views.py` | View browser and view picker | [dialog](dialog/README.md) |
| `loaders/__init__.py` | Package docstring only | |
| `loaders/base.py` | XML helpers the loaders share | [loaders](loaders/README.md#shared-helpers-basepy) |
| `loaders/menu.py` | menus.xml | [loaders](loaders/README.md#per-loader) |
| `loaders/widget.py` | widgets.xml | [loaders](loaders/README.md#per-loader) |
| `loaders/background.py` | backgrounds.xml | [loaders](loaders/README.md#per-loader) |
| `loaders/property.py` | properties.xml | [loaders](loaders/README.md#per-loader) |
| `loaders/template.py` | templates.xml | [loaders](loaders/README.md#per-loader) |
| `loaders/views.py` | views.xml | [loaders](loaders/README.md#per-loader) |
| `models/__init__.py` | Package docstring only | |
| `models/menu.py` | Menus, items, shortcuts and groups, subdialogs, context menu, icon overrides | [models](models/README.md#menus-and-items) |
| `models/widget.py` | Widgets and widget groups | [models](models/README.md) |
| `models/background.py` | Backgrounds, background groups and sources | [models](models/README.md) |
| `models/property.py` | Property schema: properties, buttons, fallbacks | [models](models/README.md#lookups) |
| `models/template.py` | Template schema | [models](models/README.md#lookups) |
| `models/views.py` | Views and content rules | [models](models/README.md) |
| `models/override.py` | `Override`, shared by every `<overrides>` block | [CONCEPTS](CONCEPTS.md#overrides-and-retired-names) |
| `providers/__init__.py` | Package docstring only | |
| `providers/content.py` | Resolves `<content>` elements to shortcuts | [providers](providers/README.md#contentprovider) |
| `providers/browse.py` | Lists paths for browse-into | [providers](providers/README.md#browseprovider) |

## Where to change what

| Change | Start in |
|--------|----------|
| What a config file accepts | Its loader and model, then the matching page in docs/skinning |
| Menu include output | `builders/includes.py` |
| Template output | `builders/template.py` |
| What a dialog button does | `DialogBaseMixin.onClick`, then the mixin that owns the handler |
| What a user edit stores | `MenuManager._diff_item` and `userdata.py` |
| A `<content>` source | `providers/content.py` |
| A skinner-facing error | `log.notify`, plus a row in [troubleshooting.md](../skinning/troubleshooting.md) |
