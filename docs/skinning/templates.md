# Template Configuration

The `templates.xml` file defines how the script generates include files. Templates transform menu items into Kodi-compatible XML.

---

## Table of Contents

- [Overview](#overview)
- [File Structure](#file-structure)
- [Template Element](#template-element)
- [Build Modes](#build-modes)
- [Properties](#properties)
- [Vars](#vars)
- [Controls](#controls)
- [Skinshortcuts Tag](#skinshortcuts-tag)
- [Property Groups](#property-groups)
- [Presets](#presets)
- [Variables](#variables)
- [Expressions](#expressions)
- [Includes](#includes)
- [Submenus](#submenus)
- [Conditions](#conditions)
- [templateonly Attribute](#templateonly-attribute)
- [Complete Example](#complete-example)

---

## Overview

Without `templates.xml`, the script generates basic includes with menu items as `<item>` elements. Templates let you:

- Define custom control structures
- Create property-based visibility conditions
- Generate Kodi variables
- Build conditional includes

---

## File Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <!-- Reusable expressions -->
  <expressions>
    <expression name="HasWidget">!String.IsEmpty(widgetPath)</expression>
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

---

## Template Element

```xml
<template include="MainMenu" idprefix="menu">
  <condition>...</condition>
  <property name="style" from="widgetStyle"/>
  <var name="aspect">...</var>
  <propertyGroup name="widgetProps"/>
  <preset name="aspectRatio"/>
  <variableGroup name="widgetVars"/>
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

---

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
    <item slot="" label="Widget 1"/>
    <item slot=".2" label="Widget 2"/>
    <item slot=".3" label="Widget 3"/>
  </list>
  <property name="slotSuffix" from="slot"/>
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
  <param name="id" default="9000"/>
  <controls>
    <control type="group" id="$PARAM[id]"/>
  </controls>
</template>
```

Use as `<include content="skinshortcuts-UtilityInclude"><param name="id">9001</param></include>`.

---

## Properties

Properties provide values to controls.

### Literal Value

```xml
<property name="left">245</property>
```

### From Menu Item

```xml
<property name="style" from="widgetStyle"/>
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

Standard item properties are also available:

| Property | Description |
|----------|-------------|
| `label` | Item label |
| `label2` | Secondary label |
| `icon` | Item icon |
| `thumb` | Item thumbnail |
| `path` | Primary action |

These come from the menu item's properties, along with any custom properties set in menus.xml or by the user.

---

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

---

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

---

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
    <skinshortcuts include="FocusAnimation"/>
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
    <skinshortcuts include="FocusAnimation" wrap="true"/>
  </control>
</controls>
```

### Conditional Include

Include content only if a property exists on the menu item:

```xml
<controls>
  <control type="group">
    <skinshortcuts include="WidgetControls" condition="widgetPath"/>
  </control>
</controls>
```

If the item doesn't have the specified property, the entire element is removed.

### Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `include` | Yes | Name of include definition to expand |
| `condition` | No | Property name that must exist on the item |
| `wrap` | No | If `true`, output as Kodi `<include>` element instead of unwrapping |

---

## Property Groups

Reusable property sets:

```xml
<propertyGroups>
  <propertyGroup name="widgetProps">
    <property name="widgetPath" from="widgetPath"/>
    <property name="widgetType" from="widgetType"/>
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
  <propertyGroup name="widgetProps"/>
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
<propertyGroup name="widgetProps" condition="!String.IsEmpty(widgetPath)"/>

<!-- Apply with suffix for Widget 2 -->
<propertyGroup name="widgetProps" suffix=".2" condition="!String.IsEmpty(widgetPath.2)"/>
```

### Suffix Transform

Apply suffix for widget slots:

```xml
<propertyGroup name="widgetProps" suffix=".2"/>
```

Transforms:
- `from="widgetPath"` → `from="widgetPath.2"`
- `condition="widgetType=movies"` → `condition="widgetType.2=movies"`

---

## Presets

Lookup tables returning multiple values:

```xml
<presets>
  <preset name="widgetLayout">
    <values condition="widgetStyle=Panel" layout="panel" columns="5" rows="1"/>
    <values condition="widgetStyle=Wide" layout="wide" columns="4" rows="1"/>
    <values layout="default" columns="6" rows="2"/>
  </preset>
</presets>
```

Reference:

```xml
<template include="MainMenu">
  <preset name="widgetLayout"/>
  <controls>
    <control type="panel" layout="$PROPERTY[layout]"/>
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
<preset name="widgetLayout" suffix=".2" condition="!String.IsEmpty(widgetPath.2)"/>
```

When `suffix` is specified, preset conditions like `widgetStyle=Panel` are transformed to `widgetStyle.2=Panel`.

---

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
    <variable name="ItemLabel"/>
  </variableGroup>
</variables>
```

Reference in template:

```xml
<template include="MainMenu">
  <variableGroup name="menuVars"/>
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
<variableGroup name="widgetVars" condition="!String.IsEmpty(widgetPath)"/>

<!-- Build Widget 2 variables with suffix transform -->
<variableGroup name="widgetVars" suffix=".2" condition="!String.IsEmpty(widgetPath.2)"/>
```

### Variable Attributes

| Attribute | Description |
|-----------|-------------|
| `name` | Variable name |
| `condition` | Build only when condition matches item |
| `output` | Output name pattern (supports `$PROPERTY[]`) |

---

## Expressions

Named conditions for reuse:

```xml
<expressions>
  <expression name="HasWidget">!String.IsEmpty(widgetPath)</expression>
  <expression name="IsMovies">String.IsEqual(widgetType,movies)</expression>
</expressions>
```

Use in controls:

```xml
<visible>$EXP[HasWidget]</visible>
```

---

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
    <skinshortcuts include="FocusAnimation"/>
  </control>
</controls>
```

See [Skinshortcuts Tag](#skinshortcuts-tag) for details on `include`, `condition`, and `wrap` attributes.

---

## Submenus

Template for submenu generation:

```xml
<submenu include="Submenu" level="1" name="">
  <property name="parent" from="name"/>
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

---

## Conditions

Control when a template builds:

```xml
<template include="MovieWidget">
  <condition>widgetType=movies</condition>
  <condition>!String.IsEmpty(widgetPath)</condition>
  ...
</template>
```

Multiple `<condition>` elements are ANDed together. The template only builds for items matching all conditions.

### Condition Syntax

See [Conditions](conditions.md) for full syntax reference.

---

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

This pattern is useful for templates that generate custom item lists - the template output becomes the widget content.

---

## Complete Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<templates>
  <expressions>
    <expression name="HasWidget">!String.IsEmpty(widgetPath)</expression>
  </expressions>

  <propertyGroups>
    <propertyGroup name="widget">
      <property name="path" from="widgetPath"/>
      <property name="target" from="widgetTarget"/>
      <var name="layout">
        <value condition="widgetStyle=Panel">panel</value>
        <value>list</value>
      </var>
    </propertyGroup>
  </propertyGroups>

  <template include="MainMenu" idprefix="menu">
    <property name="label" from="label"/>
    <property name="action" from="path"/>
    <propertyGroup name="widget"/>

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
    <property name="menu" from="name"/>
    <controls>
      <content>
        <include>skinshortcuts-$PROPERTY[menu]</include>
      </content>
    </controls>
  </submenu>
</templates>
```

---

## Quick Navigation

[Back to Top](#template-configuration)

**Sections:** [Overview](#overview) | [File Structure](#file-structure) | [Template Element](#template-element) | [Build Modes](#build-modes) | [Properties](#properties) | [Vars](#vars) | [Controls](#controls) | [Skinshortcuts Tag](#skinshortcuts-tag) | [Property Groups](#property-groups) | [Presets](#presets) | [Variables](#variables) | [Expressions](#expressions) | [Includes](#includes) | [Submenus](#submenus) | [Conditions](#conditions) | [templateonly](#templateonly-attribute)

**Related Docs:** [Conditions](conditions.md) | [Properties](properties.md) | [Menus](menus.md) | [Widgets](widgets.md)
