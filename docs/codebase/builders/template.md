# builders/template.py

**Path:** `resources/lib/skinshortcuts/builders/template.py`
**Purpose:** Build Kodi include XML from templates.xml and menu data.

***

## Overview

Processes templates defined in templates.xml, iterating over menu items and generating controls, properties, and variables with substitutions. The most complex part of the build system.

***

## TemplateBuilder Class

### `__init__`(schema, menus, container="9000", property_schema=None)

| Parameter | Description |
|-----------|-------------|
| `schema` | TemplateSchema from templates.xml |
| `menus` | list[Menu] to build from |
| `container` | Container ID for visibility conditions |
| `property_schema` | Optional PropertySchema for fallbacks |

### build() → ET.Element

Build all template includes and variables.

- Templates with same include name are merged
- Variables with same name are merged (children appended)
- Empty includes get `<description>` to avoid Kodi warnings
- `templateonly="true"` templates never output
- `templateonly="auto"` templates skipped if not assigned to any menu item

### write(path, indent=True)

Write template includes to file.

***

## Substitution Patterns

| Pattern | Description |
|---------|-------------|
| `$PROPERTY[name]` | Property/var value from context or item |
| `$PARENT[name]` | Parent item property (items iteration only) |
| `$EXP[name]` | Expression from templates.xml (recursive) |
| `$INCLUDE[name]` | Converted to Kodi `<include>` element |
| `$MATH[expr]` | Arithmetic expression (via expressions.py) |
| `$IF[cond THEN val]` | Conditional expression (via expressions.py) |

Processing order: `$EXP` → `$PARENT` → `$PROPERTY` → `$MATH` → `$IF`

***

## Context Building

Property context built in order (later overrides earlier):

1. Menu defaults + item properties
2. Built-ins: `index`, `name`, `menu`, `idprefix`, `id`, `suffix`
3. Fallback values from PropertySchema
4. Template properties
5. Template vars (first matching condition wins)
6. Preset references
7. Property group references

***

## Skinshortcuts Elements

Special elements processed within `<controls>`:

| Element | Output |
|---------|--------|
| `<skinshortcuts>visibility</skinshortcuts>` | `<visible>` condition matching current item |
| `<skinshortcuts include="name" />` | Unwrapped include contents |
| `<skinshortcuts include="name" wrap="true" />` | Kodi `<include>` element |
| `<skinshortcuts include="name" condition="prop" />` | Conditional include |
| `<skinshortcuts insert="name" />` | Items template insert point |

***

## Items Iteration

Handles `<template items="name">` elements that iterate over submenu items.

- Looks up submenu as `{parent_item.name}.{source}` (e.g., `movies.widgets`)
- `$PROPERTY[...]` references submenu item properties
- `$PARENT[...]` references parent menu item properties
- Skips disabled items
- Applies filter condition to each submenu item
- Supports vars, presets, propertyGroups within items block

***

## Key Internal Methods

| Method | Purpose |
|--------|---------|
| `_build_context` | Build property context for menu item |
| `_apply_fallbacks` | Apply PropertySchema fallbacks with suffix support |
| `_resolve_property` | Resolve property value (from_source or literal) |
| `_resolve_var` | Resolve var (first matching condition) |
| `_apply_property_group` | Apply property group with suffix transforms |
| `_apply_preset` | Apply preset values as properties |
| `_process_controls` | Process controls XML with substitutions |
| `_substitute_text` | Substitute all dynamic expressions in text |
| `_build_variable` | Build Kodi `<variable>` element |
| `_build_variable_group` | Build variables from variableGroup reference |
| `_handle_skinshortcuts_items` | Process items iteration |
| `_eval_condition` | Evaluate condition against item |

***

## Suffix Transforms

When suffix is specified (e.g., `.2` for widget slot 2):

- `from="widgetPath"` → `from="widgetPath.2"`
- `condition="widgetType=movies"` → `condition="widgetType.2=movies"`
- Built-ins (`index`, `name`, `menu`, `id`, `idprefix`) are never suffixed
