# models/template.py

**Path:** `resources/lib/skinshortcuts/models/template.py`
**Lines:** 245
**Purpose:** Dataclass models for the template system (templates.xml).

---

## Overview

The template system is the most complex part of Skin Shortcuts. It allows skins to define how menu items are transformed into Kodi includes with properties, variables, and controls.

---

## Enums

### BuildMode (line 10)
Template build mode determining iteration behavior.

| Value | Description |
|-------|-------------|
| `MENU` | Iterate over menu items (default) |
| `LIST` | Iterate over \<list\> items defined in template |
| `RAW` | Raw output, no iteration (parameterized include) |

**Used by:** Template.build, builders/template.py

---

## Classes

### TemplateParam (line 19)
Parameter for parameterized includes (build="true" templates).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Parameter name |
| `default` | str | "" | Default value if not provided |

**Used by:** Template.params

---

### TemplateProperty (line 27)
Property assignment in a template.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Property name to set |
| `value` | str | "" | Literal value |
| `from_source` | str | "" | Source property name (copies value from item) |
| `condition` | str | "" | Condition for this assignment |

**Modes:**
- Literal: `name="left", value="245"`
- From source: `name="content", from_source="widgetPath"`
- Conditional: `name="aspect", condition="...", value="stretch"`

**Used by:** Template, SubmenuTemplate, PropertyGroup, TemplateVar

---

### TemplateVar (line 43)
Multi-conditional property for internal resolution.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Variable name |
| `values` | list[TemplateProperty] | [] | Conditional values |

**Example XML:**
```xml
<var name="aspect">
    <value condition="widgetArt=Poster">stretch</value>
    <value>scale</value>
</var>
```

**Used by:** Template.vars, SubmenuTemplate.vars, PropertyGroup.vars

---

### PresetValues (line 58)
A single row in a preset lookup table.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `condition` | str | "" | Condition for this row |
| `values` | dict[str,str] | {} | Property values when matched |

**Used by:** Preset.rows

---

### Preset (line 66)
Lookup table returning multiple values based on conditions.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Preset name |
| `rows` | list[PresetValues] | [] | Rows with conditions |

**Used by:** TemplateSchema.presets, builders/template.py

---

### PropertyGroup (line 74)
Reusable property group definition.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Group name |
| `properties` | list[TemplateProperty] | [] | Properties to apply |
| `vars` | list[TemplateVar] | [] | Variables to resolve |

**Used by:** TemplateSchema.property_groups

---

### PropertyGroupReference (line 87)
Reference to a property group.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Property group name |
| `suffix` | str | "" | Suffix for transforms (e.g., ".2") |
| `condition` | str | "" | Condition for applying |

**Used by:** Template.property_groups, SubmenuTemplate.property_groups

---

### PresetReference (line 96)
Reference to a preset for direct property resolution.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Preset name |
| `suffix` | str | "" | Suffix for transforms |
| `condition` | str | "" | Condition for applying |

**Used by:** Template.preset_refs

---

### IncludeDefinition (line 109)
Reusable include definition for controls (like Kodi includes).

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Include name |
| `controls` | ET.Element\|None | None | Raw XML content |

**Used by:** TemplateSchema.includes, builders/template.py

---

### ListItem (line 120)
Item in a \<list\> for build="list" templates.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `attributes` | dict[str,str] | {} | Attribute values |

**Used by:** Template.list_items

---

### VariableDefinition (line 127)
Kodi variable definition.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Variable name (e.g., "PosterVar") |
| `content` | ET.Element\|None | None | Variable XML content |

Output name format: `HomeWidget{id}{name}` (e.g., `HomeWidget80111PosterVar`)

**Used by:** TemplateSchema.variable_definitions

---

### VariableReference (line 139)
Reference to a variable definition.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Variable definition name |
| `condition` | str | "" | Per-item condition |
| `output` | str | "" | Override output name |

**Used by:** VariableGroup.variables

---

### VariableGroupReference (line 151)
Reference to a variable group.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Variable group name |
| `suffix` | str | "" | Suffix for transforms |
| `condition` | str | "" | Condition for applying |

**Used by:** Template.variable_groups, VariableGroup.groups

---

### VariableGroup (line 160)
Reusable group of variable references.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Group name |
| `variables` | list[VariableReference] | [] | Variable references |
| `groups` | list[VariableGroupReference] | [] | Nested group references |

**Used by:** TemplateSchema.variable_groups

---

### Template (line 173)
Main template definition.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `include` | str | required | Output include name |
| `build` | BuildMode | MENU | Build mode |
| `id_prefix` | str | "" | For computed control IDs |
| `template_only` | str | "" | Include generation: "true"=never, "empty"=skip if empty |
| `conditions` | list[str] | [] | Conditions ANDed together |
| `params` | list[TemplateParam] | [] | For build="true" |
| `properties` | list[TemplateProperty] | [] | Properties to set |
| `vars` | list[TemplateVar] | [] | Variables to resolve |
| `property_groups` | list[PropertyGroupReference] | [] | Group references |
| `preset_refs` | list[PresetReference] | [] | Preset references |
| `list_items` | list[ListItem] | [] | For build="list" |
| `controls` | ET.Element\|None | None | Raw XML controls |
| `variable_groups` | list[VariableGroupReference] | [] | Variable groups |

**Used by:** TemplateSchema.templates, builders/template.py

---

### SubmenuTemplate (line 196)
Submenu template definition.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `include` | str | "" | Output include name |
| `level` | int | 0 | Submenu level |
| `name` | str | "" | Menu name filter |
| `properties` | list[TemplateProperty] | [] | Properties to set |
| `vars` | list[TemplateVar] | [] | Variables to resolve |
| `property_groups` | list[PropertyGroupReference] | [] | Group references |
| `controls` | ET.Element\|None | None | Raw XML controls |

**Used by:** TemplateSchema.submenus, builders/template.py

---

### TemplateSchema (line 210)
Complete template schema container.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `expressions` | dict[str,str] | {} | Named expressions |
| `property_groups` | dict[str,PropertyGroup] | {} | Property groups |
| `includes` | dict[str,IncludeDefinition] | {} | Include definitions |
| `presets` | dict[str,Preset] | {} | Presets |
| `variable_definitions` | dict[str,VariableDefinition] | {} | Variable definitions |
| `variable_groups` | dict[str,VariableGroup] | {} | Variable groups |
| `templates` | list[Template] | [] | Templates |
| `submenus` | list[SubmenuTemplate] | [] | Submenu templates |

**Methods:**
- `get_expression(name)` → str\|None
- `get_property_group(name)` → PropertyGroup\|None
- `get_include(name)` → IncludeDefinition\|None
- `get_preset(name)` → Preset\|None
- `get_variable_definition(name)` → VariableDefinition\|None
- `get_variable_group(name)` → VariableGroup\|None

**Used by:** config.py, loaders/template.py, builders/template.py, builders/includes.py

---

## Dead Code Analysis

All classes appear to be in active use.

---

## Test Candidates

1. `BuildMode` enum parsing
2. `TemplateSchema` lookup methods
3. Property group suffix transforms
4. Preset condition matching
