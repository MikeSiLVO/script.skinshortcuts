# Template Configuration

The `templates.xml` file defines how the script generates include files. Templates transform menu items into Kodi-compatible XML.

***

## Table of Contents

* [Overview](#overview)
* [File Structure](#file-structure)
* [Template Element](#template-element)
* [Multi-Output Templates](#multi-output-templates)
* [Build Modes](#build-modes)
* [Properties](#properties)
* [Vars](#vars)
* [Controls](#controls)
* [Dynamic Expressions](#dynamic-expressions)
* [Skinshortcuts Tag](#skinshortcuts-tag)
* [Submenu Items Iteration](#submenu-items-iteration)
* [Property Groups](#property-groups)
* [Presets](#presets)
* [Variables](#variables)
* [Expressions](#expressions)
* [Includes](#includes)
* [Submenus](#submenus)
* [Conditions](#conditions)
* [templateonly Attribute](#templateonly-attribute)
* [Complete Example](#complete-example)

***

## Overview

Without `templates.xml`, the script generates basic includes with menu items as `<item>` elements. Templates let you:

* Define custom control structures
* Create property-based visibility conditions
* Generate Kodi variables
* Build conditional includes

***

## File Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <!-- Reusable expressions -->
  <expressions>
    <expression name="HasWidget">widgetPath</expression>
  </expressions>

  <!-- Reusable property groups -->
  <propertyGroups>
    <propertyGroup name="widgetProps">...</propertyGroup>
  </propertyGroups>

  <!-- Presets (lookup tables) -->
  <presets>
    <preset name="aspectRatio">...</preset>
  </presets>

  <!-- Include definitions (for controls) -->
  <includes>
    <include name="MenuItemControl">...</include>
  </includes>

  <!-- Variable definitions and groups -->
  <variables>
    <variable name="MenuVar">...</variable>
    <variableGroup name="widgetVars">...</variableGroup>
  </variables>

  <!-- Template definitions -->
  <template include="MainMenu">...</template>
  <template include="Widgets" build="list">...</template>

  <!-- Submenu templates -->
  <submenu include="Submenu" level="1">...</submenu>
</templates>
```

***

## Template Element

```xml
<template include="MainMenu" idprefix="menu">
  <condition>...</condition>
  <property name="style" from="widgetStyle" />
  <var name="aspect">...</var>
  <propertyGroup name="widgetProps" />
  <preset name="aspectRatio" />
  <variableGroup name="widgetVars" />
  <controls>...</controls>
</template>
```

### Attributes

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `include` | Yes | - | Output include name (`skinshortcuts-template-{include}`) |
| `build` | No | `menu` | Build mode: `menu`, `list`, or `true` |
| `idprefix` | No | - | Prefix for computed control IDs |
| `templateonly` | No | - | Skip include generation: `true` (always) or `auto` (if unassigned) |

***

## Multi-Output Templates

A single template can generate multiple outputs with different ID prefixes and suffixes.

### Basic Multi-Output

```xml
<template>
  <output include="widget1" idprefix="8011" />
  <output include="widget2" idprefix="8021" suffix=".2" />
  <condition>widgetPath</condition>

  <propertyGroup content="widgetProps" />
  <preset content="layoutDimensions" />

  <controls>
    <control type="panel" id="$PROPERTY[id]">
      <top>$PROPERTY[top]</top>
      ...
    </control>
  </controls>
</template>
```

### Output Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `include` | Yes | Output include name (`skinshortcuts-template-{include}`) |
| `idprefix` | No | ID prefix for this output |
| `suffix` | No | Suffix for property transforms (e.g., `.2`) |

### Suffix Transform

When `suffix=".2"` is specified on an output:

1. **Property reads** are transformed: `from="widgetPath"` → `from="widgetPath.2"`
2. **Conditions** are transformed: `condition="widgetType=movies"` → `condition="widgetType.2=movies"`
3. **The `suffix` built-in property** is set and available in conditions

### The `suffix` Built-in Property

Within template controls, you can check the current output's suffix:

```xml
<!-- Include different navigation based on widget slot -->
<skinshortcuts include="HorizontalNavigation1" condition="!suffix" />
<skinshortcuts include="HorizontalNavigation2" condition="suffix=.2" />
```

### Suffix-Based Preset Values

Presets can provide different values per widget slot:

```xml
<presets>
  <preset name="layoutDimensions">
    <!-- Widget 2 (suffix=.2) - positioned higher -->
    <values condition="suffix=.2 + widgetArt=Poster" top="70" />
    <values condition="suffix=.2" top="112" />
    <!-- Widget 1 (default) - positioned lower -->
    <values condition="widgetArt=Poster" top="424" />
    <values top="471" />
  </preset>
</presets>
```

### Code Deduplication

Multi-output eliminates the need for separate templates per widget slot. Instead of:

```xml
<!-- OLD: Duplicate templates -->
<template include="widget1" idprefix="8011">
  <condition>widgetPath</condition>
  <!-- 200 lines of controls -->
</template>

<template include="widget2" idprefix="8021">
  <condition>widgetPath.2</condition>
  <!-- Same 200 lines duplicated -->
</template>
```

Use a single template with multiple outputs:

```xml
<!-- NEW: Single template, multiple outputs -->
<template>
  <output include="widget1" idprefix="8011" />
  <output include="widget2" idprefix="8021" suffix=".2" />
  <condition>widgetPath</condition>
  <!-- 200 lines, only once -->
</template>
```

Differences between slots are handled via `suffix=.2` conditions in presets and conditional includes.

***

## Build Modes

### Menu Mode (Default)

Iterates over menu items:

```xml
<template include="MainMenu">
  <controls>
    <control type="button">
      <label>$PROPERTY[label]</label>
      <onclick>$PROPERTY[path]</onclick>
    </control>
  </controls>
</template>
```

Generates one copy of `<controls>` per menu item, with `$PROPERTY[name]` replaced by item values.

### List Mode

Iterates over explicit list items:

```xml
<template include="WidgetSlots" build="list">
  <list>
    <item slot="" label="Widget 1" />
    <item slot=".2" label="Widget 2" />
    <item slot=".3" label="Widget 3" />
  </list>
  <property name="slotSuffix" from="slot" />
  <controls>
    <control type="group">
      <visible>!String.IsEmpty(ListItem.Property(widgetPath$PROPERTY[slotSuffix]))</visible>
    </control>
  </controls>
</template>
```

### Raw Mode

No iteration, outputs controls once with parameter substitution:

```xml
<template include="UtilityInclude" build="true">
  <param name="id" default="9000" />
  <controls>
    <control type="group" id="$PARAM[id]" />
  </controls>
</template>
```

Use as `<include content="skinshortcuts-UtilityInclude"><param name="id">9001</param></include>`.

***

## Properties

Properties provide values to controls.

### Literal Value

```xml
<property name="left">245</property>
```

### From Menu Item

```xml
<property name="style" from="widgetStyle" />
```

Reads from `item.properties["widgetStyle"]`.

### Conditional

```xml
<property name="aspect" condition="widgetArt=Poster">stretch</property>
<property name="aspect">scale</property>
```

First matching condition wins. Empty condition is default.

### Built-in Sources

These are special values available in `from` attributes and `$PROPERTY[]`:

| Source | Description |
|--------|-------------|
| `index` | Current item index (1-based) |
| `name` | Item name identifier |
| `menu` | Parent menu name |
| `idprefix` | The template's idprefix value |
| `id` | Computed ID: `{idprefix}{index}` |
| `suffix` | Output suffix (e.g., `.2`) or empty string if none |

Standard item properties are also available:

| Property | Description |
|----------|-------------|
| `label` | Item label |
| `label2` | Secondary label |
| `icon` | Item icon |
| `thumb` | Item thumbnail |
| `path` | Primary action |

These come from the menu item's properties, along with any custom properties set in menus.xml or by the user.

***

## Vars

Multi-conditional values resolved during context building:

```xml
<var name="aspectRatio">
  <value condition="widgetArt=Poster">stretch</value>
  <value condition="widgetArt=Landscape">scale</value>
  <value>scale</value>
</var>
```

First matching condition wins. Once resolved, vars become properties accessible via `$PROPERTY[aspectRatio]`.

***

## Controls

XML content output per item:

```xml
<controls>
  <control type="button" id="$PROPERTY[id]">
    <label>$PROPERTY[label]</label>
    <onclick>$PROPERTY[path]</onclick>
    <visible>$EXP[HasWidget]</visible>
  </control>
</controls>
```

### Placeholders

| Placeholder | Description |
|-------------|-------------|
| `$PROPERTY[name]` | Property or var value |
| `$EXP[name]` | Expression value (expanded in conditions) |
| `$PARAM[name]` | Parameter (raw mode only) |

Note: Vars defined with `<var>` are resolved during context building and accessible via `$PROPERTY[name]`.

***

## Dynamic Expressions

Dynamic expressions allow computed values and conditional logic in templates.

### $MATH - Arithmetic Expressions

Compute numeric values using property variables:

```xml
<control type="panel" id="$MATH[mainmenuid * 1000 + 600 + id]">
<posx>$MATH[index * 100 + 50]</posx>
<width>$MATH[(columns - 1) * spacing + itemWidth]</width>
```

#### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `id + 100` |
| `-` | Subtraction | `id - 1` |
| `*` | Multiplication | `mainmenuid * 1000` |
| `/` | Division | `width / 2` |
| `//` | Floor division | `total // count` |
| `%` | Modulo (remainder) | `index % 2` |
| `()` | Grouping | `(id - 1) * 100` |

**Notes:**
- Property values are automatically converted to numbers
- Returns integers when possible, floats otherwise
- Invalid expressions return the original text unchanged

### $IF - Conditional Expressions

Return different values based on conditions:

```xml
$IF[condition THEN trueValue]
$IF[condition THEN trueValue ELSE falseValue]
$IF[cond1 THEN val1 ELIF cond2 THEN val2 ELSE val3]
```

**Examples:**

```xml
<!-- Simple condition -->
<param name="showThumb" value="$IF[widgetArt~Thumb THEN true ELSE false]" />

<!-- URL parameter separator -->
<path>$PROPERTY[widgetPath]$IF[widgetPath~? THEN & ELSE ?]reload=true</path>

<!-- Multiple conditions -->
<layout>$IF[widgetType=movies THEN poster ELIF widgetType=albums THEN square ELSE landscape]</layout>

<!-- Using keyword operators -->
<visible>$IF[widgetPath NOT EMPTY THEN true ELSE false]</visible>
<target>$IF[widgetType IN movies,episodes,tvshows THEN videos ELSE music]</target>
```

#### Condition Operators

Uses the same [condition syntax](conditions.md) as other attributes:

| Symbol | Keyword | Description | Example |
|--------|---------|-------------|---------|
| `=` | `EQUALS` | Equality | `widgetType=movies` |
| `~` | `CONTAINS` | Substring | `widgetPath~videodb://` |
| | `EMPTY` | Empty check | `widgetPath EMPTY` |
| | `IN` | Value in list | `widgetType IN movies,tvshows` |
| `+` | `AND` | Logical and | `widgetType=movies + widgetArt=Poster` |
| `\|` | `OR` | Logical or | `widgetType=movies \| widgetType=tvshows` |
| `!` | `NOT` | Negation | `!widgetPath` or `NOT widgetPath EMPTY` |

### Nesting

Expressions can be nested:

```xml
<!-- $PROPERTY inside $IF -->
<value>$IF[useCustom THEN $PROPERTY[customPath] ELSE $PROPERTY[defaultPath]]</value>

<!-- $MATH inside $IF -->
<id>$IF[isSubmenu THEN $MATH[id + 1000] ELSE $PROPERTY[id]]</id>
```

### Order of Processing

In template text substitution:
1. `$MATH[...]` - arithmetic expressions
2. `$IF[...]` - conditional expressions
3. `$PROPERTY[...]` - property substitution
4. `$INCLUDE[...]` - include conversion

***

## Skinshortcuts Tag

Special `<skinshortcuts>` elements provide dynamic functionality within controls.

### Visibility Condition

Generate a visibility condition that matches the current menu item:

```xml
<controls>
  <control type="image">
    <skinshortcuts>visibility</skinshortcuts>
    <texture>$PROPERTY[backgroundPath]</texture>
  </control>
</controls>
```

Outputs:

```xml
<control type="image">
  <visible>String.IsEqual(Container(9000).ListItem.Property(name),movies)</visible>
  <texture>/path/to/background.jpg</texture>
</control>
```

### Include Expansion

Insert content from an include definition:

```xml
<controls>
  <control type="button">
    <!-- Unwrapped: inserts include contents directly -->
    <skinshortcuts include="FocusAnimation" />
  </control>
</controls>
```

The `<skinshortcuts>` element is replaced with the children of the `FocusAnimation` include definition.

### Wrapped Include

To output as a Kodi `<include>` element (preserving the wrapper):

```xml
<controls>
  <control type="button">
    <!-- Wrapped: outputs as <include name="FocusAnimation">...</include> -->
    <skinshortcuts include="FocusAnimation" wrap="true" />
  </control>
</controls>
```

### Conditional Include

Include content only when a condition is met:

```xml
<controls>
  <control type="group">
    <!-- Include if property has a value -->
    <skinshortcuts include="WidgetControls" condition="widgetPath" />

    <!-- Include based on suffix (multi-output) -->
    <skinshortcuts include="Navigation1" condition="!suffix" />
    <skinshortcuts include="Navigation2" condition="suffix=.2" />

    <!-- Include with complex condition -->
    <skinshortcuts include="PanelLayout" condition="widgetStyle=Panel + widgetPath" />
  </control>
</controls>
```

Supports full condition syntax including:

* `property` - truthy check (has value)
* `!property` - falsy check (empty/not set)
* `property=value` - equality
* `condition1 + condition2` - AND
* `condition1 | condition2` - OR

If the condition evaluates to false, the entire element is removed.

### Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `include` | Yes | Name of include definition to expand |
| `condition` | No | Condition expression (see [Conditions](conditions.md)) |
| `wrap` | No | If `true`, output as Kodi `<include>` element instead of unwrapping |

***

## Submenu Items Iteration

Items templates iterate over submenu items, generating controls for each item. They are defined separately from regular templates and referenced via insert markers.

### Defining Items Templates

Items templates are defined at the root level using `<template items="name">`:

```xml
<templates>
  <!-- Items template definition -->
  <template items="widgets" source="widgets">
    <property name="widget_id" from="index" />
    <property name="widget_path" from="widgetPath" />
    <property name="widget_label" from="label" />

    <controls>
      <control type="group" id="$MATH[$PARENT[index] * 1000 + 600 + widget_id]">
        <include content="WidgetPanel">
          <param name="path">$PROPERTY[widget_path]</param>
          <param name="label">$PROPERTY[widget_label]</param>
          <param name="parent">$PARENT[label]</param>
        </include>
      </control>
    </controls>
  </template>

  <!-- Regular template that uses the items template -->
  <template include="Widgets">
    <condition>widgetType=custom</condition>
    <controls>
      <control type="grouplist">
        <skinshortcuts>visibility</skinshortcuts>

        <!-- Insert widgets here -->
        <skinshortcuts insert="widgets" />
      </control>
    </controls>
  </template>
</templates>
```

### Items Template Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `items` | Yes | Template name for insert marker lookup |
| `source` | No | Submenu suffix to iterate (defaults to `items` value) |
| `filter` | No | Only include submenu items matching this condition |

### Insert Marker

Use `<skinshortcuts insert="name" />` in regular templates to insert the items template output:

```xml
<controls>
  <skinshortcuts insert="widgets" />
</controls>
```

### How It Works

1. The regular template iterates over main menu items
2. For each main menu item, `<skinshortcuts insert="widgets" />` finds the items template
3. The items template looks up submenu `{parent.name}.{source}` (e.g., `movies.widgets`)
4. For each submenu item, the items template controls are generated

### Submenu Naming Convention

The submenu is looked up as `{parent_item.name}.{source}`:

| Parent Item | Source | Submenu Looked Up |
|-------------|--------|-------------------|
| `movies` | `widgets` | `movies.widgets` |
| `tvshows` | `hubWidgets` | `tvshows.hubWidgets` |
| `music` | `widgets` | `music.widgets` |

### Property Contexts

Two property contexts are available within items templates:

| Placeholder | Description |
|-------------|-------------|
| `$PROPERTY[name]` | Submenu item properties (current widget) |
| `$PARENT[name]` | Parent menu item properties (current menu) |

**Submenu item properties (`$PROPERTY`):**

| Property | Description |
|----------|-------------|
| `index` | Submenu item index (1-based) |
| `name` | Submenu item name |
| `label` | Submenu item label |
| `menu` | Submenu name (e.g., `movies.widgets`) |
| *custom* | Any property defined on the submenu item |

**Parent item properties (`$PARENT`):**

| Property | Description |
|----------|-------------|
| `index` | Parent menu item index (1-based) |
| `name` | Parent menu item name |
| `label` | Parent menu item label |
| *custom* | Any property defined on the parent item |

### Condition vs Filter

* `condition` on items template - Evaluated against the **parent** menu item. If false, the entire insert is skipped.
* `filter` on items template - Evaluated against each **submenu** item. Items not matching are skipped.

```xml
<!-- Only include poster-style widgets -->
<template items="poster_widgets" source="widgets" filter="widgetArt=Poster">
  <controls>...</controls>
</template>
```

### Property Transformations

Vars and presets can be defined in items templates:

```xml
<template items="widgets" source="widgets">
  <var name="widgetInclude">
    <value condition="widgetArt=Poster">Widget_Poster</value>
    <value condition="widgetArt=Landscape">Widget_Landscape</value>
    <value>Widget_Default</value>
  </var>

  <preset content="WidgetDimensions" />

  <controls>
    <control type="group">
      <include content="$PROPERTY[widgetInclude]">
        <param name="width">$PROPERTY[width]</param>
        <param name="height">$PROPERTY[height]</param>
      </include>
    </control>
  </controls>
</template>
```

### Supported Transformations

| Element | Description |
|---------|-------------|
| `<var>` | Conditional property value (first match wins) |
| `<preset content="name" />` | Apply preset values as properties |
| `<propertyGroup content="name" />` | Apply property group |

### Dynamic Expressions

All dynamic expressions work within items templates:

```xml
<template items="widgets" source="widgets">
  <property name="idx" from="index" />

  <controls>
    <control type="group" id="$MATH[$PARENT[index] * 1000 + 600 + idx]">
      <visible>String.IsEqual(Container(9000).ListItem.Property(name),$PARENT[name])</visible>
      <limit>$IF[$PROPERTY[widgetLimit] THEN $PROPERTY[widgetLimit] ELSE 25]</limit>
    </control>
  </controls>
</template>
```

### Multiple Insert Points

A template can use multiple insert markers for different items templates:

```xml
<template include="Widgets">
  <condition>widgetType=custom</condition>
  <controls>
    <control type="grouplist">
      <!-- Primary widgets -->
      <skinshortcuts insert="widgets" />

      <!-- Hub widgets -->
      <skinshortcuts insert="hub_widgets" />
    </control>

    <!-- Breadcrumb area -->
    <control type="group">
      <skinshortcuts insert="breadcrumb" />
    </control>
  </controls>
</template>
```

With corresponding items templates:

```xml
<template items="widgets" source="widgets">
  <controls>...</controls>
</template>

<template items="hub_widgets" source="hubWidgets">
  <controls>...</controls>
</template>

<template items="breadcrumb" source="widgets">
  <controls>...</controls>
</template>
```

### Empty Submenus

If a submenu doesn't exist or has no items, the insert marker produces no output. Other sibling elements in the template are unaffected.

### Disabled Items

Submenu items with `<disabled>true</disabled>` are automatically skipped during iteration.

***

## Property Groups

Reusable property sets:

```xml
<propertyGroups>
  <propertyGroup name="widgetProps">
    <property name="widgetPath" from="widgetPath" />
    <property name="widgetType" from="widgetType" />
    <var name="widgetAspect">
      <value condition="widgetType=movies">landscape</value>
      <value>square</value>
    </var>
  </propertyGroup>
</propertyGroups>
```

Reference in template:

```xml
<template include="MainMenu">
  <propertyGroup name="widgetProps" />
</template>
```

### Reference Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Name of property group to apply |
| `suffix` | No | Suffix for property transforms (e.g., `.2`) |
| `condition` | No | Only apply if condition matches item |

```xml
<!-- Only apply widget props if item has a widget -->
<propertyGroup name="widgetProps" condition="widgetPath" />

<!-- Apply with suffix for Widget 2 -->
<propertyGroup name="widgetProps" suffix=".2" condition="widgetPath.2" />
```

### Suffix Transform

Apply suffix for widget slots:

```xml
<propertyGroup name="widgetProps" suffix=".2" />
```

Transforms:

* `from="widgetPath"` → `from="widgetPath.2"`
* `condition="widgetType=movies"` → `condition="widgetType.2=movies"`

***

## Presets

Lookup tables returning multiple values:

```xml
<presets>
  <preset name="widgetLayout">
    <values condition="widgetStyle=Panel" layout="panel" columns="5" rows="1" />
    <values condition="widgetStyle=Wide" layout="wide" columns="4" rows="1" />
    <values layout="default" columns="6" rows="2" />
  </preset>
</presets>
```

Reference:

```xml
<template include="MainMenu">
  <preset name="widgetLayout" />
  <controls>
    <control type="panel" layout="$PROPERTY[layout]" />
  </controls>
</template>
```

All matched attributes become properties.

### Preset Reference Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Name of preset to apply |
| `suffix` | No | Suffix for condition transforms (e.g., `.2`) |
| `condition` | No | Only apply if condition matches item |

```xml
<!-- Apply layout preset for Widget 2 properties -->
<preset name="widgetLayout" suffix=".2" condition="widgetPath.2" />
```

When `suffix` is specified, preset conditions like `widgetStyle=Panel` are transformed to `widgetStyle.2=Panel`.

***

## Variables

Generate Kodi `<variable>` elements:

### Inline Definition

```xml
<template include="MainMenu">
  <variables>
    <variable name="MenuBackground" output="Background-$PROPERTY[name]">
      <value condition="Container(9000).HasFocus($PROPERTY[index])">
        $INFO[Container(9000).ListItem($PROPERTY[index]).Property(backgroundPath)]
      </value>
    </variable>
  </variables>
</template>
```

Generates per menu item:

```xml
<variable name="Background-movies">...</variable>
<variable name="Background-tvshows">...</variable>
```

### Global Definitions

```xml
<variables>
  <variable name="ItemLabel">
    <value condition="Container(9000).HasFocus($PROPERTY[index])">
      $INFO[Container(9000).ListItem($PROPERTY[index]).Label]
    </value>
  </variable>

  <variableGroup name="menuVars">
    <variable name="ItemLabel" />
  </variableGroup>
</variables>
```

Reference in template:

```xml
<template include="MainMenu">
  <variableGroup name="menuVars" />
</template>
```

### Variable Group Reference Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Name of variable group to apply |
| `suffix` | No | Suffix for condition transforms (e.g., `.2`) |
| `condition` | No | Only build if condition matches item |

```xml
<!-- Build widget variables only for items with widgets -->
<variableGroup name="widgetVars" condition="widgetPath" />

<!-- Build Widget 2 variables with suffix transform -->
<variableGroup name="widgetVars" suffix=".2" condition="widgetPath.2" />
```

### Variable Attributes

| Attribute | Description |
|-----------|-------------|
| `name` | Variable name |
| `condition` | Build only when condition matches item |
| `output` | Output name pattern (supports `$PROPERTY[]`) |

***

## Expressions

Named conditions for reuse:

```xml
<expressions>
  <expression name="HasWidget">widgetPath</expression>
  <expression name="IsMovies">widgetType=movies</expression>
  <expression name="IsVideoWidget">widgetType=movies | episodes | tvshows</expression>
</expressions>
```

Use in template conditions:

```xml
<skinshortcuts include="WidgetControls" condition="$EXP[HasWidget]" />
<propertyGroup name="movieProps" condition="$EXP[IsMovies]" />
```

***

## Includes

Reusable control snippets:

```xml
<includes>
  <include name="FocusAnimation">
    <animation effect="zoom" start="90" end="100" time="200">Focus</animation>
  </include>
</includes>
```

Use in controls via the `<skinshortcuts>` tag:

```xml
<controls>
  <control type="button">
    <skinshortcuts include="FocusAnimation" />
  </control>
</controls>
```

See [Skinshortcuts Tag](#skinshortcuts-tag) for details on `include`, `condition`, and `wrap` attributes.

***

## Submenus

Template for submenu generation:

```xml
<submenu include="Submenu" level="1" name="">
  <property name="parent" from="name" />
  <controls>
    <control type="list">
      <content>
        <include>skinshortcuts-$PROPERTY[parent]</include>
      </content>
    </control>
  </controls>
</submenu>
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| `include` | Output include name pattern |
| `level` | Submenu depth (1 = direct child, 2 = grandchild, etc.) |
| `name` | Match specific submenu name (empty = all) |

***

## Conditions

Control when a template builds:

```xml
<template include="MovieWidget">
  <condition>widgetType=movies</condition>
  <condition>widgetPath</condition>
  ...
</template>
```

Multiple `<condition>` elements are ANDed together. The template only builds for items matching all conditions.

### Condition Syntax

See [Conditions](conditions.md) for full syntax reference.

***

## templateonly Attribute

Control include file generation:

```xml
<!-- Never generate this include (internal use only) -->
<template include="InternalHelper" templateonly="true">
  ...
</template>

<!-- Skip if not assigned to any menu item -->
<template include="MovieWidgets" templateonly="auto">
  <condition>widgetType=movies</condition>
  ...
</template>
```

| Value | Behavior |
|-------|----------|
| `true` | Never generate include file |
| `auto` | Skip if template is not assigned to any menu item |

### Template Assignment

The `auto` setting checks if any menu item has a property containing a reference to the template. Use the `$INCLUDE[skinshortcuts-template-{name}]` pattern in widget paths to assign templates:

```xml
<!-- In widgets.xml -->
<widget name="custom-movies" label="Custom Movie Widget" type="custom">
  <path>$INCLUDE[skinshortcuts-template-MovieWidgets]</path>
</widget>
```

When a user assigns this widget to a menu item, the `widgetPath` property contains `$INCLUDE[skinshortcuts-template-MovieWidgets]`. The builder detects this and marks the `MovieWidgets` template as "assigned", so it won't be skipped when `templateonly="auto"` is set.

Templates using this pattern generate custom item lists where the template output becomes the widget content.

### Output Conversion

When `$INCLUDE[...]` appears as text content in an element (e.g., after `$PROPERTY[widgetPath]` substitution), it is automatically converted to a Kodi `<include>` element:

```xml
<!-- Input (after property substitution) -->
<content>$INCLUDE[skinshortcuts-template-MovieWidgets]</content>

<!-- Output -->
<content><include>skinshortcuts-template-MovieWidgets</include></content>
```

***

## Complete Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <expressions>
    <expression name="HasWidget">widgetPath</expression>
  </expressions>

  <propertyGroups>
    <propertyGroup name="widget">
      <property name="path" from="widgetPath" />
      <property name="target" from="widgetTarget" />
      <var name="layout">
        <value condition="widgetStyle=Panel">panel</value>
        <value>list</value>
      </var>
    </propertyGroup>
  </propertyGroups>

  <template include="MainMenu" idprefix="menu">
    <property name="label" from="label" />
    <property name="action" from="path" />
    <propertyGroup name="widget" />

    <controls>
      <control type="button" id="$PROPERTY[id]">
        <label>$PROPERTY[label]</label>
        <onclick>$PROPERTY[action]</onclick>
        <visible>true</visible>
      </control>

      <control type="list" id="$PROPERTY[id]0">
        <visible>$EXP[HasWidget]</visible>
        <content target="$PROPERTY[target]">$PROPERTY[path]</content>
        <itemlayout>
          <include>skinshortcuts-WidgetItem-$VAR[layout]</include>
        </itemlayout>
      </control>
    </controls>
  </template>

  <submenu include="Submenu" level="1">
    <property name="menu" from="name" />
    <controls>
      <content>
        <include>skinshortcuts-$PROPERTY[menu]</include>
      </content>
    </controls>
  </submenu>
</templates>
```

***

## Quick Navigation

[Back to Top](#template-configuration)

**Sections:** [Overview](#overview) | [File Structure](#file-structure) | [Template Element](#template-element) | [Multi-Output](#multi-output-templates) | [Build Modes](#build-modes) | [Properties](#properties) | [Vars](#vars) | [Controls](#controls) | [Dynamic Expressions](#dynamic-expressions) | [Skinshortcuts Tag](#skinshortcuts-tag) | [Items Iteration](#submenu-items-iteration) | [Property Groups](#property-groups) | [Presets](#presets) | [Variables](#variables) | [Expressions](#expressions) | [Includes](#includes) | [Submenus](#submenus) | [Conditions](#conditions) | [templateonly](#templateonly-attribute)

**Related Docs:** [Conditions](conditions.md) | [Properties](properties.md) | [Menus](menus.md) | [Widgets](widgets.md)
