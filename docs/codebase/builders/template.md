# Template Builder

`builders/template.py` turns templates.xml, parsed into a `TemplateSchema` by `loaders/template.py`, and the merged menus into Kodi includes and variables. `IncludesBuilder` runs it when the schema has at least one `<template>` or `<submenu>` and appends everything it builds to the includes file. The XML syntax is in [skinning/templates.md](../../skinning/templates.md); this page covers how the builder processes it.

## Pass order

`TemplateBuilder.build`:

1. For each `<template>` and each of its outputs (`Template.get_outputs`: the declared outputs, else one from `include` and `idPrefix`), it gets or creates the include `skinshortcuts-template-{include}`. Outputs that share a name build into the same include.
2. A raw template (`build="true"`) builds through `_build_raw_template`, every other one through `_build_template_into`.
3. Each templates.xml `<submenu>` builds into `skinshortcuts-{include}` (`_build_submenu_template`).
4. Every fixed variable name a template declares, directly or through a variableGroup, gets an empty placeholder variable when no item built it (`_add_placeholder_variables`), so a skin naming it still resolves.
5. Variables are emitted first, then includes. Includes from a `templateOnly="true"` template are left out, as are `templateOnly="auto"` ones no menu item property assigns with `$INCLUDE[skinshortcuts-template-{include}]`. An include that ends up empty gets a `<description>` saying no items matched.

## Menu templates

`_build_template_into` runs once per output:

- It walks every menu, or only the one named by `menu`, and every enabled item in it.
- It skips items that fail the template's conditions, after `$EXP` expansion and the output's suffix. When the controls hold `<skinshortcuts insert>` markers, it also skips items for which none of the inserted submenus has items (`_has_required_submenus`).
- For each remaining item it builds the item context, processes a copy of the controls against it, and builds the template's variables and variableGroups into the shared variable map.

## The item context

`_build_context` builds the dict of values the substitutions read, in this order:

1. The menu's default properties under the item's own properties.
2. Built-ins: `index`, `name`, `menu`, `idprefix`, `id`, `suffix`, `label`, `label2`, `icon`, `visible`, `action`, `path`, `submenuVisibility`. These overwrite item properties of the same name.
3. properties.xml fallbacks, for each property still unset in each slot the item uses.
4. The template's `<property>` elements, first match per name.
5. The template's `<var>` elements, first matching value.
6. Preset references, presetGroup references and propertyGroup references, each gated by its own condition.

Template properties and vars overwrite earlier values. Fallbacks, presets and presetGroups only fill names still unset. In a propertyGroup, entries with `from` overwrite and literal values only fill unset names.

Every condition and `from` source in steps 4 to 6 takes the output's suffix, or the reference's own suffix when it sets one (`_combine_suffixes`). See [Property slots and suffixes](../CONCEPTS.md#property-slots-and-suffixes).

## Processing controls

`_process_element` walks the copy of the controls:

- `<skinshortcuts>visibility</skinshortcuts>` becomes a `<visible>` that tests the menu's container for this item; with no container it is dropped and a warning is raised.
- `<skinshortcuts>onclick</skinshortcuts>` becomes the item's `<onclick>` elements, in the same order as menu includes ([Entries](README.md#entries)).
- `<skinshortcuts include="X">` is replaced by the controls of templates.xml include `X`, processed in the same context, inline or inside a Kodi `<include name="X">` with `wrap="true"`. It is dropped when its `condition` fails; a loop is reported and cut.
- `<skinshortcuts insert="X">` expands an items template, below.
- Text, tails and attribute values go through `_substitute_text`, which replaces `$EXP`, `$PARENT`, `$PROPERTY`, `$MATH` and `$IF` in that order. `$INCLUDE[X]` in text becomes an `<include>` child.
- Leaf elements left with no text and no attributes are removed (`_remove_empty_elements`).

## Items templates

`<skinshortcuts insert="X">` inside a menu template expands `<template items="X">` (an `ItemsDefinition`) once per enabled item of the flat menu `{item}.{source}`, where `source` defaults to the items template's name.

- The items template's `condition` is tested against the parent item, and its `filter` against each submenu item.
- Each submenu item gets its own context (`_build_items_context`: menu defaults, its properties, built-ins, fallbacks), then the items template's properties, vars, presets and propertyGroups, without a suffix.
- In its controls `$PROPERTY[...]` reads the submenu item and `$PARENT[...]` reads the parent item's context.
- Its variableGroups build into the same variable map as the parent template's.

## Raw templates

A raw template emits its controls once rather than once per item. `_collect_raw_matching_items` gathers the enabled items that pass the conditions, from menus that have a container (`menu` limits it to one).

- With no properties, vars, presets, presetGroups or propertyGroups, the controls are copied once and each `<skinshortcuts>visibility</skinshortcuts>` becomes an OR over every matching item.
- Otherwise each item's context is resolved, items whose substituted controls come out identical are grouped, and one copy is emitted per group with visibility over that group.

Raw templates build no variables and expand no `<skinshortcuts include>`; the loader reports either and drops the include markers.

## Variables

- A template's `<variable>` definitions, and those of the variableGroups it references, build once per matching item. A name holding `$PROPERTY[...]` gives each item its own variable; a fixed name collects every item's `<value>` elements in one variable (`_add_variable`).
- `<value iterate="..." as="x">` expands before substitution into one value per slot, by count or by the slots the item holds, filling `$PROPERTY[xIndex]` and `$PROPERTY[xSuffix]` and suffixing the other property names (`_expand_iterate_values`).
- The `output` and `condition` attributes control the build and are stripped from the emitted variable.

## Submenu templates

A templates.xml `<submenu include="X">` builds into `skinshortcuts-X`, applying only its properties and vars:

- With `name`, it builds once against that menu, with a context holding only `menu`. An insert expands its items template over that menu's items.
- With a `level` above 0, it builds once per enabled item of the menu named `mainmenu` that has a per-item submenu, with a context from the main item. An insert expands over that item's per-item submenu.

The submenu's own controls get `$PROPERTY`, `$EXP` and `$MATH` substitution; inserted items get the full set. Content a submenu template cannot build is reported by the loader and ignored.

`IncludesBuilder` gives no menu include to a root menu that a templates.xml `<submenu name>` names, since the template builds it.

## Warnings

Problems a skinner can fix (an include or insert that names nothing, a circular reference, a menu with no container, unsupported submenu content) go through `log.notify`, and the builder carries on without the offending piece. The notifications are listed in [skinning/troubleshooting.md](../../skinning/troubleshooting.md).
