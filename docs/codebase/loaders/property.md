# loaders/property.py

**Path:** `resources/lib/skinshortcuts/loaders/property.py`
**Lines:** 284
**Purpose:** Load property schema from properties.xml with include expansion.

***

## Overview

Parses the `properties.xml` file which defines custom properties that can be set on menu items, along with fallback rules and button mappings.

**Note:** Condition evaluation functions have been moved to `conditions.py`. See [conditions.md](../core/conditions.md).

***

## PropertyLoader Class (line 26)

Loads property schema from properties.xml with include expansion.

### `__init__`(path) (line 29)

Initialize with path to properties.xml.

### load() → PropertySchema

Load and parse the property schema.

**Returns:** PropertySchema containing:

* `properties` - dict of SchemaProperty by name
* `fallbacks` - dict of PropertyFallback by property name
* `buttons` - dict of ButtonMapping by button ID

**Raises:** PropertyConfigError on parse errors

***

### Internal parsing methods

#### `_parse_includes`(root)

Parse `<include name="...">` definitions for reuse.

#### `_expand_include`(include_elem, suffix="")

Expand an `<include content="..."/>` reference.

Supports suffix transform via `suffix` attribute.

#### `_copy_element_with_suffix`(elem, suffix)

Deep copy element, applying suffix transform to condition attributes.

#### `_parse_property`(elem)

Parse a `<property>` element.

**Parses:**

* `name` attribute (required)
* `templateonly` attribute
* `type` attribute ("widget", "background", "toggle", or "options")
* `requires` attribute (property dependency)
* `<options>` child

#### `_parse_button`(elem, default_suffix=False)

Parse a `<button>` element from the buttons section.

**Parameters:**

* `elem` - The button XML element
* `default_suffix` - Default suffix value inherited from parent `<buttons>` or `<group>` element

**Parses:**

* `id` attribute (required) - button control ID
* `property` attribute (required) - property name to act on
* `suffix` attribute - if present, overrides default_suffix; if "true", append property_suffix at runtime
* `title` attribute - dialog title
* `showNone` attribute - show "None" option (default true)
* `showIcons` attribute - show icons (default true)
* `type` attribute - "widget", "background", "toggle", "options" (overrides property type)
* `requires` attribute - property that must be set first (overrides property requires)

#### `_parse_options`(options_elem)

Parse options element, expanding includes.

#### `_parse_option`(elem)

Parse a single option element.

**Parses:**

* `value`, `label`, `condition` attributes
* `<icon>` children with optional condition

#### `_parse_fallback`(elem)

Parse a fallback element.

**Parses:**

* `property` attribute (required)
* `<when condition="...">value</when>` children
* `<default>value</default>` child

***

## Module Function

### load_properties(path) (line 281)

Convenience function to load property schema.

**Parameters:**

* `path` - Path to properties.xml

**Returns:** PropertySchema

**Used by:** config.py (SkinConfig.load)

***

## XML Schema

```xml
<properties>
  <!-- Includes section for reusable option sets -->
  <includes>
    <include name="styleOptions">
      <option value="List" label="List"/>
      <option value="Panel" label="Panel"/>
    </include>
  </includes>

  <!-- Property definitions (data schema) -->
  <property name="widget" type="widget"/>
  <property name="widgetStyle" requires="widgetPath">
    <options>
      <include content="styleOptions"/>
      <option value="custom" label="Custom" condition="widgetType=custom">
        <icon>special://skin/icons/custom.png</icon>
      </option>
    </options>
  </property>
  <property name="background" type="background"/>

  <!-- Button mappings -->
  <buttons>
    <!-- Group with suffix for widget buttons -->
    <group suffix="true">
      <button id="309" property="widget" title="Select Widget"/>
      <button id="1001" property="widgetStyle" title="Widget Style" showNone="false"/>
      <!-- Toggle with type/requires on button (no property definition needed) -->
      <button id="1022" property="widgetHide" type="toggle" requires="widgetStyle" title="Hide Widget"/>
    </group>
    <!-- Non-widget buttons outside group (no suffix) -->
    <button id="310" property="background" type="background" title="Background"/>
  </buttons>

  <!-- Fallbacks -->
  <fallbacks>
    <fallback property="widgetLabel">
      <when condition="widgetType=movies">Movies</when>
      <when condition="widgetType=tvshows">TV Shows</when>
      <default>Widget</default>
    </fallback>
  </fallbacks>
</properties>
```

***

## Dead Code Analysis

All code appears to be in active use.

***

## Test Candidates

1. Include expansion with suffix transforms
2. Property parsing with all optional fields
3. Button parsing with suffix inheritance
4. Fallback rule parsing with conditions
