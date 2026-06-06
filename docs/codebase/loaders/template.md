# loaders/template.py

**Path:** `resources/lib/skinshortcuts/loaders/template.py`
**Purpose:** Load template schema from templates.xml.

***

## Overview

Parses templates.xml defining how menu items transform into Kodi includes. The most complex loader - supports expressions, property groups, presets, variables, and template definitions.

***

## Public Functions

### load_templates(path) → TemplateSchema

Load template schema. Returns TemplateSchema with all parsed definitions.

***

## TemplateLoader Class

### load() → TemplateSchema

Parse template schema. Sections parsed in order:
1. `<expressions>` - Named expression strings
2. `<presets>` - Lookup tables
3. `<presetGroups>` - Conditional preset selection groups
4. `<propertyGroups>` - Reusable property sets
5. `<variables>` - Variable definitions and groups
6. `<includes>` - Control XML snippets
7. `<template>` elements - Regular and items templates
8. `<submenu>` elements - Submenu templates

**Template type detection:** `items="..."` → ItemsDefinition, `include="..."` → Template

***

## Internal Parsers

### Section Parsers

| Function | Parses |
|----------|--------|
| `_parse_expressions_section` | `<expression name="...">` |
| `_parse_presets_section` | `<preset name="...">` |
| `_parse_preset_groups_section` | `<presetGroup name="...">` |
| `_parse_property_groups_section` | `<propertyGroup name="...">` |
| `_parse_variables_section` | `<variable>` and `<variableGroup>` |
| `_parse_includes_section` | `<include name="...">` control snippets |

### Element Parsers

| Function | Parses |
|----------|--------|
| `_parse_template` | Main template with conditions, properties, controls |
| `_parse_submenu` | Submenu template |
| `_parse_items_template` | Items template for submenu iteration |
| `_parse_property` | Property assignment (with suffix transform) |
| `_parse_var` | Multi-value variable |
| `_parse_preset` | Preset lookup table |
| `_parse_preset_group` | `<presetGroup>` definition (preset/values children) |
| `_parse_variable_definition` | Kodi variable definition |
| `_parse_variable_group` | Variable group with references |
| `_parse_param` | `<param name="..." default="...">` |

### Reference Parsers

| Function | Parses |
|----------|--------|
| `_parse_property_group_ref` | `<propertyGroup content="...">` |
| `_parse_preset_ref` | `<preset content="...">` |
| `_parse_preset_group_ref` | `<presetGroup content="...">` |
| `_parse_variable_group_ref` | `<variableGroup content="...">` |

***

## XML Reference

See [skinning/templates.md](../../skinning/templates.md) for full XML documentation.
