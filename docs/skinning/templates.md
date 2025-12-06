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
<template include="MainMenu" idprefix="menu" templateonly="false">
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
| `include` | Yes | - | Output include name (`skinshortcuts-{include}`) |
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

| Source | Description |
|--------|-------------|
| `label` | Item label |
| `label2` | Secondary label |
| `icon` | Item icon |
| `thumb` | Item thumbnail |
| `path` | Primary action |
| `name` | Item name identifier |
| `index` | Current item index (0-based) |
| `id` | Computed ID: `{idprefix}{index}` |

---

## Vars

Multi-conditional properties for internal resolution:

```xml
<var name="aspectRatio">
  <value condition="widgetArt=Poster">stretch</value>
  <value condition="widgetArt=Landscape">scale</value>
  <value>scale</value>
</var>
```

Use in controls as `$VAR[aspectRatio]` or reference in other properties.

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
| `$PROPERTY[name]` | Property value |
| `$VAR[name]` | Var value |
| `$EXP[name]` | Expression value |
| `$PARAM[name]` | Parameter (raw mode only) |
| `$INCLUDE[name]` | Include definition content |

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

Use in controls:

```xml
<controls>
  <control type="button">
    $INCLUDE[FocusAnimation]
  </control>
</controls>
```

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
