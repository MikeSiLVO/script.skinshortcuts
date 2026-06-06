# models/template.py

**Path:** `resources/lib/skinshortcuts/models/template.py`
**Purpose:** Dataclasses for template system.

***

## BuildMode Enum

| Value | Description |
|-------|-------------|
| `MENU` | Iterate over menu items (default) |
| `RAW` | No iteration (parameterized include). With properties: per-item resolve + deduplication |

***

## Main Classes

### TemplateSchema

Top-level container.

| Field | Type | Description |
|-------|------|-------------|
| `expressions` | dict[str, Expression] | Named expressions (value + nosuffix flag) |
| `property_groups` | dict | PropertyGroup definitions |
| `presets` | dict | Preset lookup tables |
| `preset_groups` | dict | PresetGroup definitions (conditional preset selection) |
| `includes` | dict | IncludeDefinition for control reuse |
| `variable_definitions` | dict | Kodi variable definitions |
| `variable_groups` | dict | Variable group definitions |
| `items_templates` | dict | ItemsDefinition for submenu iteration |
| `templates` | list[Template] | Template definitions |
| `submenus` | list[SubmenuTemplate] | Submenu templates |

### Template

| Field | Type | Description |
|-------|------|-------------|
| `include` | str | Output include name (legacy single-output; superseded by `outputs`) |
| `build` | BuildMode | Build mode |
| `id_prefix` | str | For computed control IDs (legacy single-output; superseded by `outputs`) |
| `template_only` | str | "true"=never build, "auto"=skip if unassigned |
| `menu` | str | Filter to specific menu |
| `outputs` | list[TemplateOutput] | Multi-output configs; when empty, falls back to legacy include/id_prefix |
| `conditions` | list[str] | Build conditions (ANDed) |
| `params` | list[TemplateParam] | Declared parameters for build="true" includes (parsed; not yet consumed by builders) |
| `properties` | list[TemplateProperty] | Properties to set |
| `vars` | list[TemplateVar] | Variables to resolve |
| `property_groups` | list[PropertyGroupReference] | Group references |
| `preset_refs` | list[PresetReference] | Preset references |
| `preset_group_refs` | list[PresetGroupReference] | PresetGroup references |
| `variables` | list[VariableDefinition] | Inline variable definitions |
| `variable_groups` | list[VariableGroupReference] | Variable group references |
| `controls` | ET.Element | Raw XML controls |

**Properties:**

| Property | Returns | Description |
|----------|---------|-------------|
| `has_transformations` | bool | True if any properties, vars, preset refs, preset group refs, or property groups defined |

### SubmenuTemplate

| Field | Type | Description |
|-------|------|-------------|
| `include` | str | Output include name |
| `level` | int | Submenu level |
| `name` | str | Menu name filter |
| `properties`, `vars`, `property_groups`, `controls` | | Same as Template |

***

## Property/Variable Classes

| Class | Purpose |
|-------|---------|
| `TemplateProperty` | Property assignment (literal value or from_source) |
| `TemplateVar` | Multi-conditional property |
| `PropertyGroup` | Reusable property set |
| `PropertyGroupReference` | Reference with suffix/condition |
| `Preset` | Lookup table with condition rows |
| `PresetReference` | Reference with suffix/condition |

***

## Variable Classes

| Class | Purpose |
|-------|---------|
| `VariableDefinition` | Kodi variable definition |
| `VariableReference` | Reference with condition/output override |
| `VariableGroup` | Group of variable references |
| `VariableGroupReference` | Reference with suffix/condition |

***

## Items Iteration

### ItemsDefinition

For `<template items="...">` submenu iteration.

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Insert marker name |
| `source` | str | Submenu suffix |
| `condition` | str | Parent item condition |
| `filter` | str | Submenu item filter |
| `properties`, `vars`, `preset_refs`, `property_groups`, `variable_groups`, `controls` | | Transformations |

See [skinning/templates.md](../../skinning/templates.md) for XML documentation.
