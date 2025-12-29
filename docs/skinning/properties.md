# Property Configuration

The `properties.xml` file defines custom properties, button mappings, and fallback values.

***

## Table of Contents

* [Overview](#overview)
* [File Structure](#file-structure)
* [Property Element](#property-element)
* [Options](#options)
* [Button Mappings](#button-mappings)
* [Fallbacks](#fallbacks)
* [Includes](#includes)
* [Suffix Transforms](#suffix-transforms)

***

## Overview

Properties extend menu items beyond built-in fields (label, icon, action). Common uses:

* Widget style selection (Panel, Wide, Poster)
* Art type selection (Poster, Fanart, Landscape)
* Custom toggle settings
* Any skin-specific metadata

***

## File Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <!-- Reusable option sets -->
  <includes>
    <include name="artOptions">
      <option value="Poster" label="$LOCALIZE[31001]" />
      <option value="Landscape" label="$LOCALIZE[31002]" />
    </include>
  </includes>

  <!-- Property definitions -->
  <property name="widgetStyle" type="options" requires="widget">
    <options>
      <option value="Panel" label="Panel" />
      <option value="Wide" label="Wide" />
    </options>
  </property>

  <!-- Button mappings -->
  <buttons suffix="true">
    <button id="350" property="widgetStyle" title="Widget Style" />
    <group suffix="false">
      <button id="360" property="someProperty" />
    </group>
  </buttons>

  <!-- Fallback values -->
  <fallbacks>
    <fallback property="widgetStyle">
      <when condition="widgetType=movies">Panel</when>
      <default>Wide</default>
    </fallback>
  </fallbacks>
</properties>
```

***

## Property Element

```xml
<property name="widgetStyle" type="options" requires="widget" templateonly="false">
  <options>
    <option value="Panel" label="Panel">
      <icon>panel-icon.png</icon>
      <icon condition="widgetType=movies">movie-panel.png</icon>
    </option>
  </options>
</property>
```

### Attributes

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `name` | Yes | - | Property name (stored in item.properties) |
| `type` | No | `options` | Property type: `options`, `toggle`, `widget`, `background` |
| `requires` | No | - | Property name that must have a value |
| `templateonly` | No | `false` | If `true`, only available in templates, not in dialog |

### Property Types

| Type | Behavior |
|------|----------|
| `options` | Select from defined options list |
| `toggle` | Toggle between `True` and empty (cleared) |
| `widget` | Opens widget picker |
| `background` | Opens background picker |

***

## Options

```xml
<options>
  <option value="Panel" label="$LOCALIZE[31001]" condition="widgetType=movies">
    <icon>panel.png</icon>
    <icon condition="widgetArt=Poster">poster-panel.png</icon>
  </option>
  <option value="Wide" label="$LOCALIZE[31002]">
    <icon>wide.png</icon>
  </option>
  <include content="artOptions" />
</options>
```

### `<option>` Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `value` | Yes | Stored value |
| `label` | Yes | Display label (supports `$LOCALIZE[id]`) |
| `condition` | No | Property condition for visibility |

### `<icon>` Elements

Multiple icons with conditions for dynamic display:

```xml
<option value="Poster" label="Poster">
  <icon condition="widgetType=movies">poster-movie.png</icon>
  <icon condition="widgetType=tvshows">poster-tv.png</icon>
  <icon>poster-default.png</icon>
</option>
```

First matching condition wins. Empty condition is default.

***

## Button Mappings

Map control IDs to properties.

```xml
<buttons suffix="true">
  <button id="350" property="widgetStyle" title="Widget Style"
          showNone="true" showIcons="true" type="options" requires="widget" />

  <group suffix="false">
    <button id="360" property="globalProp" />
  </group>
</buttons>
```

### `<buttons>` Attributes

| Attribute | Default | Description |
|-----------|---------|-------------|
| `suffix` | `false` | Apply property suffix to all children by default |

### `<button>` Attributes

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `id` | Yes | - | Control ID in dialog |
| `property` | Yes | - | Property name to edit |
| `title` | No | - | Dialog title |
| `suffix` | No | parent | Override parent suffix setting |
| `showNone` | No | `true` | Show "None" option |
| `showIcons` | No | `true` | Show icons in select dialog |
| `type` | No | - | Override property type |
| `requires` | No | - | Property that must be set |

### `<group>` Element

Group buttons with shared settings:

```xml
<group suffix="true">
  <button id="351" property="widgetStyle" />
  <button id="352" property="widgetArt" />
</group>
```

***

## Fallbacks

Default values when property is not set:

```xml
<fallbacks>
  <fallback property="widgetStyle">
    <when condition="widgetType=movies">Panel</when>
    <when condition="widgetType=tvshows">Wide</when>
    <default>Panel</default>
  </fallback>
</fallbacks>
```

### `<when>` vs `<default>`

```xml
<fallback property="widgetArt">
  <when condition="widgetType=movies">Poster</when>
  <when condition="widgetType=albums">Cover</when>
  <default>Landscape</default>
</fallback>
```

* `<when condition="...">` - Use this value if condition matches
* `<default>` - Use if no conditions match

Rules are evaluated in order. First match wins.

***

## Includes

Reuse option sets across properties:

```xml
<includes>
  <include name="standardArt">
    <option value="Poster" label="Poster">
      <icon>poster.png</icon>
    </option>
    <option value="Landscape" label="Landscape">
      <icon>landscape.png</icon>
    </option>
    <option value="Fanart" label="Fanart">
      <icon>fanart.png</icon>
    </option>
  </include>
</includes>

<property name="widgetArt">
  <options>
    <include content="standardArt" />
    <option value="Custom" label="Custom" />
  </options>
</property>

<property name="backgroundArt">
  <options>
    <include content="standardArt" suffix=".bg" />
  </options>
</property>
```

### Include Attributes

| Attribute | Description |
|-----------|-------------|
| `content` | Name of include to expand |
| `suffix` | Apply suffix transform to conditions |

***

## Suffix Transforms

Support multiple widget/property slots using suffixes.

### How It Works

With `suffix=".2"`:

```xml
<!-- Original -->
<option value="Panel" condition="widgetType=movies" />

<!-- Transformed -->
<option value="Panel" condition="widgetType.2=movies" />
```

### In Button Mappings

```xml
<buttons>
  <!-- Widget 1 properties (no suffix) -->
  <button id="350" property="widgetStyle" suffix="false" />

  <!-- Widget 2 properties (with suffix) -->
  <button id="351" property="widgetStyle" suffix="true" />
</buttons>
```

When suffix is enabled, the dialog reads/writes `widgetStyle.2` instead of `widgetStyle`.

### In Subdialogs

Subdialogs set suffix via the `suffix` attribute:

```xml
<!-- In menus.xml -->
<subdialog buttonID="801" mode="widget2" suffix=".2" />
```

Button mappings with `suffix="true"` automatically use the dialog's suffix.

***

## Complete Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <includes>
    <include name="artTypes">
      <option value="Poster" label="$LOCALIZE[31050]">
        <icon>art-poster.png</icon>
      </option>
      <option value="Landscape" label="$LOCALIZE[31051]">
        <icon>art-landscape.png</icon>
      </option>
      <option value="Fanart" label="$LOCALIZE[31052]">
        <icon>art-fanart.png</icon>
      </option>
    </include>
  </includes>

  <property name="widgetStyle" type="options" requires="widget">
    <options>
      <option value="Panel" label="Panel" />
      <option value="Wide" label="Wide" />
      <option value="Showcase" label="Showcase" />
    </options>
  </property>

  <property name="widgetArt" type="options" requires="widget">
    <options>
      <include content="artTypes" />
    </options>
  </property>

  <property name="hideLabels" type="toggle" />

  <buttons suffix="true">
    <button id="350" property="widgetStyle" title="Widget Style" requires="widget" />
    <button id="351" property="widgetArt" title="Widget Art" requires="widget" />
    <group suffix="false">
      <button id="360" property="hideLabels" title="Hide Labels" type="toggle" />
    </group>
  </buttons>

  <fallbacks>
    <fallback property="widgetStyle">
      <when condition="widgetType=movies">Panel</when>
      <when condition="widgetType=episodes">Wide</when>
      <default>Panel</default>
    </fallback>
    <fallback property="widgetArt">
      <when condition="widgetType=movies">Poster</when>
      <when condition="widgetType=albums">Cover</when>
      <default>Landscape</default>
    </fallback>
  </fallbacks>
</properties>
```

***

## Quick Navigation

[Back to Top](#property-configuration)

**Sections:** [Overview](#overview) | [File Structure](#file-structure) | [Property Element](#property-element) | [Options](#options) | [Button Mappings](#button-mappings) | [Fallbacks](#fallbacks) | [Includes](#includes) | [Suffix Transforms](#suffix-transforms)

**Related Docs:** [Templates](templates.md) | [Conditions](conditions.md) | [Menus](menus.md) | [Builtin Properties](builtin-properties.md)
