# Built-in Properties

Properties available on menu items in the generated includes.

***

## Table of Contents

* [Overview](#overview)
* [Core Properties](#core-properties)
* [Widget Properties](#widget-properties)
* [Background Properties](#background-properties)
* [Submenu Properties](#submenu-properties)
* [Custom Properties](#custom-properties)
* [Template Properties](#template-properties)
* [Accessing Properties](#accessing-properties)

***

## Overview

Menu items in the generated includes have properties accessible via `ListItem.Property(name)`. These properties come from:

1. Built-in fields (label, icon, action)
2. Widget/background assignments
3. Custom properties defined in `properties.xml`
4. Template-generated properties

***

## Core Properties

| Property | Source | Description |
|----------|--------|-------------|
| `label` | `<label>` | Display label |
| `label2` | `<label2>` | Secondary label |
| `icon` | `<icon>` | Icon path |
| `path` | `<action>` | Primary action string |
| `name` | `name` attribute | Item identifier |
| `menu` | Parent menu | Menu name containing this item |
| `visible` | `<visible>` | Visibility condition (output to includes) |

### Usage

```xml
<control type="button">
  <label>$INFO[ListItem.Label]</label>
  <label2>$INFO[ListItem.Property(path)]</label2>
  <texturefocus>$INFO[ListItem.Icon]</texturefocus>
  <onclick>$INFO[ListItem.Property(path)]</onclick>
</control>
```

***

## Widget Properties

Set when a widget is assigned to a menu item.

| Property | Source | Description |
|----------|--------|-------------|
| `widget` | Widget name | Widget identifier |
| `widgetLabel` | Widget label | Display label |
| `widgetPath` | Widget path | Content path |
| `widgetTarget` | Widget target | Target window (videos, music, etc.) |
| `widgetType` | Widget type | Content type (movies, episodes, etc.) |
| `widgetSource` | Widget source | Source type (library, playlist, addon) |

### Multiple Widgets

For additional widget slots, use suffixed properties:

| Slot | Properties |
|------|------------|
| Widget 2 | `widget.2`, `widgetPath.2`, `widgetType.2`, `widgetTarget.2`, `widgetLabel.2`, `widgetSource.2` |
| Widget 3 | `widget.3`, `widgetPath.3`, ... |

### Usage

```xml
<!-- Main widget -->
<control type="list" id="3000">
  <content target="$INFO[Container(9000).ListItem.Property(widgetTarget)]">
    $INFO[Container(9000).ListItem.Property(widgetPath)]
  </content>
  <visible>!String.IsEmpty(Container(9000).ListItem.Property(widgetPath))</visible>
</control>

<!-- Second widget -->
<control type="list" id="3001">
  <content target="$INFO[Container(9000).ListItem.Property(widgetTarget.2)]">
    $INFO[Container(9000).ListItem.Property(widgetPath.2)]
  </content>
  <visible>!String.IsEmpty(Container(9000).ListItem.Property(widgetPath.2))</visible>
</control>
```

***

## Background Properties

Set when a background is assigned to a menu item.

| Property | Source | Description |
|----------|--------|-------------|
| `background` | Background name | Background identifier |
| `backgroundLabel` | Background label | Display label |
| `backgroundPath` | Background path | Image path or info label |

### Usage

```xml
<control type="image">
  <texture background="true">
    $INFO[Container(9000).ListItem.Property(backgroundPath)]
  </texture>
  <visible>!String.IsEmpty(Container(9000).ListItem.Property(backgroundPath))</visible>
</control>
```

***

## Submenu Properties

Available when items have linked submenus.

| Property | Description |
|----------|-------------|
| `hasSubmenu` | `True` if item has a submenu |
| `submenuVisibility` | Submenu name (for visibility conditions) |

### Usage

```xml
<!-- Show arrow for items with submenus -->
<control type="image">
  <texture>arrow.png</texture>
  <visible>String.IsEqual(Container(9000).ListItem.Property(hasSubmenu),True)</visible>
</control>
```

***

## Custom Properties

Properties defined in `properties.xml` are stored on items.

### Definition

```xml
<!-- properties.xml -->
<property name="widgetStyle" type="options">
  <options>
    <option value="Panel" label="Panel" />
    <option value="Wide" label="Wide" />
  </options>
</property>
```

### Resulting Properties

| Property | Description |
|----------|-------------|
| `widgetStyle` | The stored value (e.g., "Panel") |
| `widgetStyleLabel` | The resolved label (e.g., "Panel") |

### Usage

```xml
<control type="panel">
  <visible>String.IsEqual(Container(9000).ListItem.Property(widgetStyle),Panel)</visible>
</control>

<control type="label">
  <label>Style: $INFO[Container(9000).ListItem.Property(widgetStyleLabel)]</label>
</control>
```

***

## Template Properties

Templates can define additional properties for output.

### Definition

```xml
<!-- templates.xml -->
<template include="MainMenu" idprefix="menu">
  <property name="id" from="id" />
  <property name="index" from="index" />
  <property name="focusCondition">Container(9000).HasFocus($PROPERTY[index])</property>
  <var name="aspectRatio">
    <value condition="widgetArt=Poster">stretch</value>
    <value>scale</value>
  </var>
</template>
```

### Available Sources

| Source | Description |
|--------|-------------|
| `label` | Item label |
| `label2` | Secondary label |
| `icon` | Icon path |
| `thumb` | Thumbnail path |
| `path` | Primary action |
| `name` | Item name |
| `index` | Zero-based item index |
| `id` | Computed ID (`{idprefix}{index}`) |

### Literal Values

```xml
<property name="fixedValue">static text</property>
```

### Conditional Values

```xml
<property name="layout" condition="widgetStyle=Panel">panel</property>
<property name="layout">default</property>
```

***

## Accessing Properties

### In Skin XML

From the menu list:

```xml
$INFO[Container(9000).ListItem.Property(widgetPath)]
```

For focused item only:

```xml
$INFO[Container(9000).ListItem.Property(backgroundPath)]
```

For specific position:

```xml
$INFO[Container(9000).ListItem(0).Property(widget)]
$INFO[Container(9000).ListItem(1).Property(widget)]
```

### In Templates

Using `$PROPERTY[]` placeholders:

```xml
<controls>
  <control type="button" id="$PROPERTY[id]">
    <label>$PROPERTY[label]</label>
    <onclick>$PROPERTY[path]</onclick>
    <property name="index">$PROPERTY[index]</property>
  </control>
</controls>
```

### Checking Empty Properties

```xml
<visible>!String.IsEmpty(Container(9000).ListItem.Property(widgetPath))</visible>
<visible>String.IsEqual(Container(9000).ListItem.Property(hasSubmenu),true)</visible>
```

***

## Property Inheritance

Properties flow from:

1. **Default values** - From menu's `<defaults>` section
2. **Item values** - From `<item>` definition
3. **User customizations** - From userdata
4. **Fallback values** - From `properties.xml` fallbacks

Fallbacks only apply when a property is empty and the fallback condition matches.

***

## Quick Navigation

[Back to Top](#built-in-properties)

**Sections:** [Overview](#overview) | [Core Properties](#core-properties) | [Widget Properties](#widget-properties) | [Background Properties](#background-properties) | [Submenu Properties](#submenu-properties) | [Custom Properties](#custom-properties) | [Template Properties](#template-properties) | [Accessing Properties](#accessing-properties) | [Property Inheritance](#property-inheritance)

**Related Docs:** [Properties](properties.md) | [Templates](templates.md) | [Management Dialog](management-dialog.md) | [Widgets](widgets.md)
