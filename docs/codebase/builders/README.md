# builders/

Turn loaded config into the includes file. The builders read nothing from disk; `SkinConfig.build_includes_from_menus` hands them everything.

| Module | Builds |
|--------|--------|
| `includes.py` | `IncludesBuilder`: menu, submenu and custom widget includes; runs the other two builders and writes the file |
| `template.py` | `TemplateBuilder`: includes and variables from templates.xml, see [template.md](template.md) |
| `views.py` | `ViewExpressionBuilder`: view locking expressions from views.xml and the user's choices |

The element names and their order in the file are in [FORMATS.md](../FORMATS.md#generated-includes).

## Inputs

`SkinConfig.build_includes_from_menus` fills derived widget and background properties into the menus in place, applies action overrides to copies, then gives `IncludesBuilder` the menus, the template schema, the property schema, the view config, the userdata, the subdialogs and the `<submenuPath>all</submenuPath>` flag, and calls `write`. `build` returns the tree; `write` builds it, indents it with tabs and writes it.

## Which menus get includes

- Root `<menu>` menus only. A `<submenu>` gets no include of its own; its items reach the output through per-item instances.
- A root menu that a templates.xml `<submenu name>` names is skipped, since that template builds it.
- A `build="auto"` menu is built only when its `action` matches an action of an enabled item in a menu that is not itself `auto`.
- Each built menu gets `skinshortcuts-{menu}`, then `skinshortcuts-{menu}-submenu` unless its `template_only` attribute contains `submenu`, then its custom widget includes.

## Entries

`_build_item` writes one entry per enabled item:

- `id` counts from 1, or from the menu's `id` attribute for a `controltype` menu. Disabled items are skipped but still counted, so ids can have gaps.
- `label`, `label2`, `icon` and `thumb`. `icon` is left out for a `controltype` menu or one with `icons="false"`.
- Include references from the menu defaults and the item, placed before or after the `<onclick>` elements by where they sat relative to the actions in menus.xml.
- `<onclick>` elements in this order: `before` default actions, the item's conditional actions, its unconditional actions, `after` default actions. Each keeps its condition.
- The item's `<visible>` condition.
- For `<item>` output, properties: the built-ins `id`, `name`, `menu`, `action`, `path`, `submenuVisibility`, and `hasSubmenu` when the item's per-item submenu has items; then the menu's default properties under the item's own, and `submenuPath`. `menu` holds the template name for a per-item instance. Properties properties.xml marks `templateonly`, with their numbered slots, stay out of the menu include but still reach the template builder. Empty values are never written.
- A `<control>` entry, for a menu with `controltype`, carries no properties.

Entries in `skinshortcuts-{menu}-submenu` also get a `parent` property, and when the root menu has a `container`, a visibility test against that container's selected item, ANDed with the entry's own `<visible>`.

`submenuPath` is the path of the first enabled widget in the item's widgets submenu, found through the subdialog menu references that use `{item}`; `submenuPath.N` follows for the other widgets when the menu sets `submenuPath="all"` or menus.xml sets `<submenuPath>all</submenuPath>`. Skinner view: [Submenu Widget Path](../../skinning/builtin-properties.md#submenu-widget-path).

## View expressions

`ViewExpressionBuilder` runs when views.xml has content rules. For each content rule it takes the effective library view, generic plugin view and per-plugin overrides (a user choice the rule allows, else the rule's default), then adds the rule's condition, narrowed by `Container.PluginName` where library and plugin choices differ, to each chosen view's list. Each view then gets one expression ORing its list (`False` when empty) and an `_Include` expression that is `True` when the view is used at all. A content rule with plugin overrides also gets `_HasPluginOverride` and `_IsGenericPlugin` helper expressions. Expression names: [Generated Expressions](../../skinning/views.md#generated-expressions).
