# loaders/template.py

**Path:** `resources/lib/skinshortcuts/loaders/template.py`
**Purpose:** Load template schema from templates.xml with expression, preset, and variable support.

***

## Overview

Parses the `templates.xml` file which defines how menu items are transformed into Kodi includes. This is the most complex loader, supporting expressions, property groups, presets, variables, and template definitions.

***

## TemplateLoader Class

### `__init__`(path)

Initialize with path to templates.xml.

**Instance attributes:**

* `_expressions` - Named expression strings
* `_presets` - Parsed Preset definitions
* `_property_groups` - Parsed PropertyGroup definitions
* `_variable_definitions` - VariableDefinition objects
* `_variable_groups` - VariableGroup objects
* `_includes` - Parsed IncludeDefinition objects

### load() → TemplateSchema

Load and parse the template schema.

**Parse order (sectioned structure):**

1. `<expressions>` section
2. `<presets>` section
3. `<propertyGroups>` section
4. `<variables>` section (definitions + groups)
5. `<includes>` section
6. `<template>` elements at root
7. `<submenu>` elements at root

**Returns:** TemplateSchema

**Raises:** TemplateConfigError on parse errors

***

## Section Parsing Methods

### `_parse_expressions_section`(root)

Parse `<expressions>` section containing `<expression>` elements.

***

### `_parse_presets_section`(root)

Parse `<presets>` section containing `<preset>` elements.

***

### `_parse_property_groups_section`(root)

Parse `<propertyGroups>` section containing `<propertyGroup>` elements.

**Children:** `<property>`, `<var>`

***

### `_parse_variables_section`(root)

Parse `<variables>` section containing:

* `<variable name="...">` definitions (global)
* `<variableGroup name="...">` groups

***

### `_parse_variable_group`(elem)

Parse a variableGroup element.

**Contains:**

* `<variable name="..." condition="..." />` references
* `<variableGroup content="..." />` nested group refs

***

### `_parse_variable_reference`(elem)

Parse variable reference inside variableGroup.

**Attributes:** name, condition

***

### `_parse_includes_section`(root)

Parse `<includes>` section containing `<include>` definitions for control XML reuse.

***

### `_parse_param`(elem)

Parse `<param name="..." default="..." />` for raw templates.

***

### `_parse_property`(elem, suffix="")

Parse `<property name="..." from="..." condition="...">value</property>`.

Applies suffix transforms to `from` and `condition` if suffix provided.

***

### `_parse_var`(elem, suffix="")

Parse `<var name="..."><value condition="...">value</value></var>`.

Applies suffix transforms to conditions if suffix provided.

***

### `_parse_preset`(elem)

Parse `<preset name="..."><values condition="..." attr="val" /></preset>`.

***

### `_parse_template`(elem)

Parse main template element.

**Attributes:**

* `include` (required) - Output include name
* `build` - "list", "true" (raw), or default (menu)
* `idprefix` - For computed control IDs
* `templateonly` - "true" to never build, "auto" to skip if unassigned
* `menu` - Filter to specific menu (e.g., "mainmenu")

**Children:**

* `<condition>` - Build conditions (ANDed)
* `<param>` - Parameters for raw templates
* `<property>` - Property assignments
* `<var>` - Internal variables
* `<propertyGroup>` - Group references
* `<preset>` - Preset references
* `<variableGroup>` - Variable group references
* `<list><item .../></list>` - For build="list"
* `<controls>` - Raw XML controls
* `<variables>` - Inline variable definitions

***

### `_parse_submenu`(elem)

Parse submenu template element.

**Attributes:** include, level, name

**Children:** `<property>`, `<var>`, `<propertyGroup>`, `<controls>`

***

### `_parse_property_group_ref`(elem)

Parse property group reference.

**Attributes:** content, suffix, condition

***

### `_parse_preset_ref`(elem)

Parse preset reference for direct property resolution.

**Attributes:** content, suffix, condition

***

### `_parse_variable_group_ref`(elem)

Parse variableGroup reference in a template.

**Attributes:** content, suffix, condition

***

### `_parse_variable_definition`(elem)

Parse a variable definition (global or inline).

**Attributes:** name, condition, output
**Content:** Full `<variable>` XML with `<value>` children

***

## Module Function

### load_templates(path)

Convenience function to load template schema.

**Parameters:**

* `path` - Path to templates.xml

**Returns:** TemplateSchema

**Used by:** config.py (SkinConfig.load)

***

## XML Schema Example

```xml
<templates>
  <!-- Expressions section -->
  <expressions>
    <expression name="hasWidget">!String.IsEmpty(widgetPath)</expression>
    <expression name="square">widgetArt=Square Poster</expression>
  </expressions>

  <!-- Presets section -->
  <presets>
    <preset name="dimensions">
      <values condition="widgetLayout=list" width="100" height="50" />
      <values width="200" height="100" />
    </preset>
  </presets>

  <!-- Property groups section -->
  <propertyGroups>
    <propertyGroup name="widgetProps">
      <property name="content" from="widgetPath" />
      <var name="aspect">
        <value condition="widgetType=poster">stretch</value>
        <value>scale</value>
      </var>
    </propertyGroup>
  </propertyGroups>

  <!-- Variables section (global definitions + groups) -->
  <variables>
    <variable name="PosterVar">
      <value condition="!String.IsEmpty(...)">...</value>
      <value>fallback</value>
    </variable>
    <variableGroup name="artworkVars">
      <variable name="PosterVar" condition="widgetArt=Poster" />
    </variableGroup>
    <variableGroup name="allVars">
      <variableGroup content="artworkVars" />  <!-- nested reference -->
    </variableGroup>
  </variables>

  <!-- Includes section (reusable control XML) -->
  <includes>
    <include name="panelInfo">
      <control type="group">...</control>
    </include>
  </includes>

  <!-- Templates at root level -->
  <template include="HomeWidgets">
    <condition>hasWidget</condition>
    <propertyGroup content="widgetProps" />
    <preset content="dimensions" />
    <variableGroup content="allVars" />
    <controls>...</controls>
  </template>

  <!-- Template with menu filter and inline variables -->
  <template include="BackgroundVars" menu="mainmenu" templateonly="true">
    <condition>backgroundPath</condition>
    <property name="backgroundPath" from="backgroundPath" />
    <variables>
      <variable name="MainMenu_BackgroundPath">
        <value condition="...">$PROPERTY[backgroundPath]</value>
      </variable>
    </variables>
  </template>

  <!-- Submenu templates at root level -->
  <submenu include="Submenu" level="1">
    <property name="items" from="submenu" />
  </submenu>
</templates>
```

***

## Test Candidates

1. `load()` with complete templates.xml
2. Suffix transforms in `_parse_property()` and `_parse_var()`
3. BuildMode parsing (list, true, default)
4. Preset parsing with conditions
5. Variable group nesting
6. Menu attribute filtering
7. Inline variables parsing
