# loaders/

One loader per skin config file, each turning the XML into the models in `models/`. The XML syntax is documented for skinners in [skinning/](../../skinning/index.md); this page covers how the loaders behave.

| Module | File | Model |
|--------|------|---------|
| `menu.py` | menus.xml | `MenuConfig` |
| `widget.py` | widgets.xml | `WidgetConfig` |
| `background.py` | backgrounds.xml | `BackgroundConfig` |
| `property.py` | properties.xml | `PropertySchema` |
| `template.py` | templates.xml | `TemplateSchema` |
| `views.py` | views.xml | `ViewConfig` |
| `base.py` | | Helpers the loaders share |

## Errors

- A missing file loads as an empty config, so a skin can leave out any file it does not use.
- A file the loader cannot use (bad XML, wrong root element, a required name, label or path missing) raises the `ConfigError` subclass for that file, with the path and, for a parse error, the line. Nothing catches these by type: the action stops, and `build_includes` and the `manage` handler log the error.
- Smaller problems are reported and the element skipped: duplicate names (`base.warn_duplicate_names`), a group with no name, content a file does not support. Reports a skinner should see go through `log.notify`.

## Shared helpers (base.py)

- `parse_xml` validates the root element; `get_text`, `get_attr`, `get_int` and `get_bool` read values with defaults. `get_bool` accepts only `true` and `false`, in any case.
- `parse_content` reads a `<content>` element into `Content`, which stays unresolved until a picker opens.
- `parse_name_overrides` reads the retired-name `<overrides>` block of widgets.xml, backgrounds.xml and properties.xml (see [Overrides and retired names](../CONCEPTS.md#overrides-and-retired-names)).
- `iter_nested` walks a picker hierarchy, nested groups included.

## Per loader

- **menu.py**: `load_menus` reads menus, `<submenu>` templates, icon sources, subdialogs, action and icon overrides, the context menu and `<submenuPath>`. Icon overrides are read first, since menu items with no icon get the override of their default icon. Several `<visible>` children on an item join with ` + `. An item's `<skinshortcuts include>` records whether it came before or after the first `<action>`. `load_groupings` reads the groupings and is what the shortcut picker calls: a `<groupings menu="X">` replaces the default `<groupings>` for menu X, and shortcuts and inputs with no icon get the same icon overrides.
- **widget.py**: a group passes its `source` down to its widgets. A target in `constants.TARGET_MAP` is normalized; any other target passes through, as skins use it as their own vocabulary. `WidgetConfig.widgets` holds root-level widgets only; nested ones are reached through `groupings`.
- **background.py**: `load_backgrounds` takes the icon overrides from menus.xml, so `SkinConfig.load` parses menus.xml first. `<source>` children become `BrowseSource` for browse and multi backgrounds and `PlaylistSource` for the rest.
- **property.py**: `<include>` definitions are expanded where `<options>` or a `<fallback>` reference them, with any suffix applied to their `condition` attributes. Buttons inherit `suffix` from `<buttons>` or their `<group>`. A `rename="true"` on a button that is not a widget button is logged and ignored.
- **template.py**: sections parse in order: expressions, presets, presetGroups, propertyGroups, variables, includes, then `<template>` elements and `<submenu>` templates. A `<template items="X">` becomes an `ItemsDefinition`; every other `<template>` a `Template`. The loader reports and drops what the builder would mishandle: a `<var>` or `<property>` that clashes with a `<var>` of the same name (several `<property>` elements may share one), include markers in raw templates, and content submenu templates do not build.
- **views.py**: every view needs an id and label, every content rule a name, label, library default, `<visible>` and `<views>`; default view ids must exist. A failure raises `ViewConfigError`.
