# models/

Dataclasses for everything the config files describe, plus the `BuildMode` and `BackgroundType` enums. Loaders create them; `config.py`, `manager.py`, the builders and the dialog read them. Models carry little logic: lookups by name, the primary action, protection checks.

| Module | Top-level container | Holds |
|--------|---------------------|-------|
| `menu.py` | `MenuConfig` | Menus and items, shortcut groupings, icon sources, subdialogs, context menu, icon overrides |
| `widget.py` | `WidgetConfig` | Widgets and widget groups |
| `background.py` | `BackgroundConfig` | Backgrounds, background groups and their sources |
| `property.py` | `PropertySchema` | Property definitions, button mappings, fallbacks |
| `template.py` | `TemplateSchema` | Templates, items templates, submenu templates and the named pieces they reference |
| `views.py` | `ViewConfig` | Views and content rules |
| `override.py` | | `Override`, shared by every `<overrides>` block |

`WidgetConfig`, `BackgroundConfig` and `PropertySchema` each carry the retired names their file declares (`overrides`); `MenuConfig` carries `action_overrides`, also as `Override` objects, and `icon_overrides` as an `IconOverrides`.

## Menus and items

- `Menu` covers both a menus.xml `<menu>` and a `<submenu>` (`is_submenu`). Per-item submenu instances and user-created menus are `Menu` objects too: an instance records its template in `template_origin`, and a custom widget menu has `menu_type="widgets"`. `container` names the skin list that shows the menu, which visibility tests in the includes need.
- `MenuItem.properties` holds widget, background and skin properties in one dict, keyed by property name with any slot tail.
- `MenuItem.visible` is the `<visible>` condition written into the includes; `dialog_visible` is the `visible` attribute tested at load ([CONCEPTS.md](../CONCEPTS.md#items-a-visible-condition-hides)).
- `MenuItem.action` is the action shown for display: the last unconditional action, else the first. Every action reaches the output.
- `MenuItem.original_action` holds the skin default's action, which the dialog shows to the skin as `originalAction`.
- `MenuItem.submenu` names the linked `<submenu>` template, and `is_placeholder` marks the stand-in an empty menu shows.

## Picker hierarchies

- A groupings list mixes leaves and groups: `Shortcut`, `ShortcutGroup`, `Input` and `Content` for menus.xml; `Widget`, `WidgetGroup` and `Content` for widgets.xml; `Background` and `BackgroundGroup` for backgrounds.xml. Groups nest, and a `flat` group shows its children at the parent's level.
- `Content` is a `<content>` reference kept unresolved; the picker resolves it into `Shortcut` or `Widget` objects when the user reaches it.
- `Shortcut` is a picker option, not a stored item. Picking one copies its label, actions and icon onto the `MenuItem`, and its `item_visible` (its `<visible>` children) into `MenuItem.visible`.

## Lookups

- `PropertySchema.get_property` matches names ignoring case, and `declared_name` returns the spelling properties.xml uses.
- `TemplateSchema` holds the named pieces (expressions, presets, presetGroups, propertyGroups, includes, variables, variableGroups, items templates) in dicts with a `get_*` per kind, and `templates` and `submenus` as lists.
- `Template.get_outputs` gives the declared outputs, or one output built from `include` and `idprefix`.
- `ViewContent.get_default` gives the plugin default for plugin content when the rule sets one, else the library default.
