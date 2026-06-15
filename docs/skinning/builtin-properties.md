# Built-in Properties

Properties available on menu items in the generated includes.

---

## Table of Contents

* [Overview](#overview)
* [Core Properties](#core-properties)
* [Widget Properties](#widget-properties)
* [Background Properties](#background-properties)
* [Submenu Properties](#submenu-properties)
* [Custom Properties](#custom-properties)
* [Template Properties](#template-properties)
* [Accessing Properties](#accessing-properties)

---

## Overview

Menu items in the generated includes have properties accessible via `ListItem.Property(name)`. These properties come from:

1. Built-in fields (label, icon, action)
2. Widget/background assignments
3. Custom properties defined in `properties.xml`
4. Template-generated properties

---

## Core Properties

| Property | Source | Description |
|----------|--------|-------------|
| `label` | `<label>` | Display label |
| `label2` | `<label2>` | Secondary label |
| `icon` | `<icon>` | Icon path |
| `action` | `<action>` | Full action string (e.g. `ActivateWindow(videos,plugin://...,return)`) |
| `path` | `<action>` | Bare content path extracted from action |
| `name` | `name` attribute | Item identifier |
| `menu` | Parent menu | Menu name containing this item |
| `visible` | `<visible>` | Visibility condition (output to includes) |
| `id` | Item position | 1-based position of the item within its menu. Emitted as a `<property name="id">` only for standard `<item>` menus (not control-type menus). The element's `id` attribute is set separately on every item to the same position value (or offset from the menu's `id` attribute for control-type menus). |

### Usage

```xml
<control type="button">
  <label>$INFO[ListItem.Label]</label>
  <label2>$INFO[ListItem.Property(action)]</label2>
  <texturefocus>$INFO[ListItem.Icon]</texturefocus>
  <onclick>$INFO[ListItem.Property(action)]</onclick>
</control>
```

---

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

### Submenu Widget Path

When a menu item has a per-item widget submenu (opened via a `{item}.X` subdialog, with items carrying `widgetPath`), the item carries `submenuPath` — the `widgetPath` of its first enabled widget. The submenu is recognized by its widget content, so submenus added at runtime work without a `type="widgets"` definition.

| Property | Description |
|----------|-------------|
| `submenuPath` | First widget path of the item's widgets submenu (empty when the submenu has no widgets) |
| `submenuPath.2`, `.3`, … | Remaining widget paths, in submenu order. Emitted only when `submenuPath="all"` is set (see below) |

This lets the parent menu item answer "which widget is on this item" and "does it have any widgets" without a hidden counter container:

```xml
<!-- Drive a panel from the focused item's first widget -->
<control type="group">
  <visible>String.IsEqual(Container(9000).ListItem.Property(submenuPath),Settings)</visible>
</control>

<!-- Item has no widgets -->
<visible>String.IsEmpty(Container(9000).ListItem.Property(submenuPath))</visible>
```

With `submenuPath="all"`, the widget count is the highest filled slot: an item with `submenuPath.3` set and `submenuPath.4` empty has three widgets.

`submenuPath="all"` lives on the parent `<menu>`; the global form is a `<submenuPath>all</submenuPath>` element under `<menus>` that covers every menu. It belongs on the menu rather than the submenu because `submenuPath` is a property of the menu item, and the menu scope reaches submenus built entirely at runtime, which have no `<submenu>` element of their own to carry an attribute:

```xml
<menus>
  <submenuPath>all</submenuPath>             <!-- every widget submenu -->
  <menu name="mainmenu" submenuPath="all">   <!-- every widget submenu under this menu -->
```

Custom widget content submenus do not produce `submenuPath`. To drop the property, declare it `templateonly` in `properties.xml`:

```xml
<property name="submenuPath" templateonly="true" />
```

---

## Background Properties

Set when a background is assigned to a menu item.

| Property | Source | Description |
|----------|--------|-------------|
| `background` | Background name | Background identifier (path for browse/multi types) |
| `backgroundLabel` | Background label | Display label (path for browse/multi types) |
| `backgroundPath` | Background path | Image path or info label |
| `backgroundType` | Background type | Normalized type name: static, playlist, browse, multi, property, live, live-playlist |
| `backgroundPlaylistType` | Playlist content type | For playlist/live-playlist backgrounds only: raw smart-playlist type (movies, tvshows, episodes, musicvideos, songs, albums, artists) |

### Usage

```xml
<control type="image">
  <texture background="true">
    $INFO[Container(9000).ListItem.Property(backgroundPath)]
  </texture>
  <visible>!String.IsEmpty(Container(9000).ListItem.Property(backgroundPath))</visible>
</control>
```

---

## Submenu Properties

Available when items have linked submenus.

| Property | Description |
|----------|-------------|
| `hasSubmenu` | `True` if item has a submenu |
| `submenuVisibility` | The item's own name (used to build a submenu visibility condition matching this item) |
| `parent` | Name of the parent menu item (set on items in the combined `skinshortcuts-{menu}-submenu` include) |

### Usage

```xml
<!-- Show arrow for items with submenus -->
<control type="image">
  <texture>arrow.png</texture>
  <visible>String.IsEqual(Container(9000).ListItem.Property(hasSubmenu),True)</visible>
</control>
```

---

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
| `widgetStyle` | The stored value (e.g., "Panel"), emitted in the generated includes |

> Note: For `options`-type properties only the stored value is emitted into the generated menu includes. The resolved option label (`widgetStyleLabel`) exists only on the management dialog list items; `ListItem.Property(widgetStyleLabel)` is empty in the generated includes. Widget and background labels (`widgetLabel`/`backgroundLabel`) are stored on the item itself and are emitted normally.

### Usage

```xml
<control type="panel">
  <visible>String.IsEqual(Container(9000).ListItem.Property(widgetStyle),Panel)</visible>
</control>
```

> **See also:** [Properties](properties.md) for defining custom properties

---

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
| `action` | Full action string |
| `path` | Bare content path |
| `name` | Item name |
| `index` | One-based item index |
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

> **See also:** [Templates](templates.md) for full template system reference

---

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
    <onclick>$PROPERTY[action]</onclick>
    <property name="index">$PROPERTY[index]</property>
  </control>
</controls>
```

### Checking Empty Properties

```xml
<visible>!String.IsEmpty(Container(9000).ListItem.Property(widgetPath))</visible>
<visible>String.IsEqual(Container(9000).ListItem.Property(hasSubmenu),True)</visible>
```

---

## Property Inheritance

Properties flow from:

1. **Default values** - From menu's `<defaults>` section
2. **Item values** - From `<item>` definition
3. **User customizations** - From userdata
4. **Fallback values** - From `properties.xml` fallbacks

Fallbacks only apply when a property is empty and the fallback condition matches.

---

[↑ Top](#built-in-properties) · [Skinning Docs](index.md)
