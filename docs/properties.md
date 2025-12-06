# Properties

Defines property schemas for the management dialog - what properties are available, their options, button mappings, fallbacks, and navigation.

## Table of Contents

- [Structure](#structure)
- [Include Definitions](#include-definitions)
- [Property Element](#property-element)
- [Property Types](#property-types)
- [Buttons Section](#buttons-section)
- [Suffix-Aware Buttons](#suffix-aware-buttons)
- [Dependencies](#dependencies)
- [Fallbacks](#fallbacks)
- [Navigation](#navigation)
- [Condition Syntax](#condition-syntax)

## Structure

`shortcuts/properties.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <!-- Reusable includes -->
  <include name="StyleOptions">
    <option value="List" label="$LOCALIZE[535]"/>
    <option value="Panel" label="$LOCALIZE[31712]"/>
  </include>

  <!-- Property definitions (data schema) -->
  <property name="widgetStyle" requires="widgetPath">
    <options>
      <include content="StyleOptions"/>
      <option value="Custom" label="Custom" condition="widgetType=custom"/>
    </options>
  </property>

  <property name="widget" type="widget"/>
  <property name="background" type="background"/>
  <property name="widgetHide" type="toggle" requires="widgetStyle"/>

  <!-- Button mappings (UI controls) -->
  <buttons>
    <button id="309" property="widget" suffix="true" title="$LOCALIZE[31000]"/>
    <button id="310" property="background" title="$LOCALIZE[31053]"/>
    <button id="1001" property="widgetStyle" suffix="true" title="$LOCALIZE[31701]" showNone="false"/>
    <button id="1022" property="widgetHide" suffix="true"/>
  </buttons>

  <!-- Fallbacks -->
  <fallbacks>
    <fallback property="widgetArt">
      <when condition="widgetType=albums | songs">Square Poster</when>
      <default>Poster</default>
    </fallback>
  </fallbacks>

  <!-- Navigation -->
  <navigation>
    <onback from="1001,1002,1003" to="800"/>
  </navigation>
</properties>
```

## Include Definitions

Reusable content that can be referenced in property options.

```xml
<include name="ArtOptions">
  <option value="Poster" label="Poster" condition="!widgetType=weather"/>
  <option value="FanArt" label="FanArt"/>
  <option value="Landscape" label="Landscape"/>
</include>
```

### Reference with Suffix Transform

When referencing includes, you can apply a suffix transform to condition property names:

```xml
<options>
  <include content="ArtOptions" suffix=".2"/>
  <!-- Expands: condition="!widgetType=weather" -> condition="!widgetType.2=weather" -->
</options>
```

## Property Element

```xml
<property name="widgetStyle" type="..." templateonly="true" requires="widgetPath">
  <options>...</options>
</property>
```

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Property name (e.g., `widgetStyle`) |
| `type` | No | Special type: `widget`, `background`, or `toggle` |
| `templateonly` | No | If `true`, property is excluded from menu item output (used only by templates) |
| `requires` | No | Property name that must have a value first |

## Property Types

### Standard (Options List)

Shows a picker dialog with predefined options:

```xml
<property name="widgetStyle" requires="widgetPath">
  <options>
    <option value="List" label="List"/>
    <option value="Panel" label="Panel">
      <icon>special://skin/icons/panel.png</icon>
    </option>
    <option value="Custom" label="Custom" condition="widgetType=custom"/>
  </options>
</property>
```

#### Options with Conditional Icons

```xml
<option value="Glass" label="Glass Case">
  <icon condition="widgetArt=Poster">cases/glass/portrait.png</icon>
  <icon condition="widgetArt=Banner">cases/glass/banner.png</icon>
  <icon>cases/glass/landscape.png</icon>  <!-- default -->
</option>
```

### Widget Type

Opens the widget picker dialog. Auto-populates related properties.

```xml
<property name="widget" type="widget"/>
```

Auto-populated properties:
- `widgetPath` - Content path
- `widgetType` - Widget type (e.g., `movies`, `episodes`)
- `widgetTarget` - Target window
- `widgetLabel` - Display name

### Background Type

Opens the background picker dialog. Auto-populates related properties.

```xml
<property name="background" type="background"/>
```

Auto-populated properties:
- `backgroundPath` - Background image path
- `backgroundName` - Display name

### Toggle Type

Boolean toggle that sets `True` when enabled, empty when disabled.

```xml
<property name="widgetHide" type="toggle" requires="widgetStyle"/>
```

## Buttons Section

Maps skin button IDs to property actions. Separates UI controls from property definitions.

```xml
<buttons>
  <button id="309" property="widget" suffix="true" title="$LOCALIZE[31000]"/>
  <button id="310" property="background" title="$LOCALIZE[31053]"/>
  <button id="1001" property="widgetStyle" suffix="true" title="$LOCALIZE[31701]" showNone="false"/>
  <button id="1022" property="widgetHide" suffix="true"/>
</buttons>
```

### Buttons Element Attributes

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `suffix` | No | `false` | Default suffix value for all child buttons |

### Button Element Attributes

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `id` | Yes | - | Skin button ID that triggers this property |
| `property` | Yes | - | Property name to act on |
| `suffix` | No | parent | If `true`, applies property_suffix for multi-widget support |
| `title` | No | - | Dialog title (supports `$LOCALIZE[id]`) |
| `showNone` | No | `true` | Show "None" option to clear value |
| `showIcons` | No | `true` | Show icons in picker dialog |

## Suffix-Aware Buttons

When `suffix="true"`, a single button can handle multiple widget slots based on the current subdialog context.

### Parent Default

Set the default `suffix` on the `<buttons>` element, then override per-button as needed:

```xml
<!-- Default suffix="true" for all widget buttons -->
<buttons suffix="true">
  <button id="309" property="widget"/>
  <button id="1001" property="widgetStyle"/>
  <button id="1002" property="widgetBack"/>
  <!-- ... all inherit suffix="true" -->

  <!-- Override for non-widget buttons -->
  <button id="310" property="background" suffix="false"/>
  <button id="510" property="InfoLine" suffix="false"/>
</buttons>
```

### How It Works

When in widget2 subdialog mode (property_suffix=".2"):
- Button 309 acts on `widget.2` instead of `widget`
- Button 1001 acts on `widgetStyle.2` instead of `widgetStyle`
- The `requires` attribute is also suffixed automatically

**Without suffix support (old way):**
```xml
<!-- Required separate buttons for each widget slot -->
<buttons>
  <button id="309" property="widget"/>
  <button id="2050" property="widget.2"/>
  <button id="1001" property="widgetStyle"/>
  <button id="2001" property="widgetStyle.2"/>
</buttons>
```

**With suffix support (new way):**
```xml
<!-- One button handles both widget slots -->
<buttons suffix="true">
  <button id="309" property="widget"/>
  <button id="1001" property="widgetStyle"/>
</buttons>
```

## Dependencies

Make a property depend on another property having a value:

```xml
<property name="widgetStyle" requires="widgetPath">
  <options>...</options>
</property>
```

The `widgetStyle` picker only becomes active when `widgetPath` has a value. When `widgetPath` is cleared, `widgetStyle` is also cleared.

### Multiple Widgets Example

With suffix-aware buttons, you only define base properties once:

```xml
<!-- Property definitions (no .2 duplicates needed) -->
<property name="widget" type="widget"/>
<property name="widgetStyle" requires="widgetPath">
  <options>
    <include content="StyleOptions"/>
  </options>
</property>

<!-- Button mappings with suffix support -->
<buttons>
  <button id="309" property="widget" suffix="true"/>
  <button id="1001" property="widgetStyle" suffix="true"/>
</buttons>
```

When button 309 is clicked in widget2 mode:
- Acts on `widget.2` property
- `requires="widgetPath"` becomes `requires="widgetPath.2"`

## Fallbacks

Provide default values when a property isn't explicitly set:

```xml
<fallbacks>
  <fallback property="widgetArt">
    <when condition="widgetType=albums | songs | artists">Square Poster</when>
    <when condition="widgetType=weather">Landscape</when>
    <default>Poster</default>
  </fallback>
</fallbacks>
```

| Element | Description |
|---------|-------------|
| `<when>` | Conditional fallback with `condition` attribute |
| `<default>` | Default fallback when no conditions match |

Rules are evaluated in order. First matching rule wins.

### Using Includes in Fallbacks

```xml
<include name="CommonFallbacks">
  <when condition="widgetType=albums">Square Poster</when>
  <when condition="widgetType=songs">Square Poster</when>
</include>

<fallbacks>
  <fallback property="widgetArt">
    <include content="CommonFallbacks"/>
    <default>Poster</default>
  </fallback>
</fallbacks>
```

## Navigation

Map control IDs to back navigation targets:

```xml
<navigation>
  <onback from="1001,1002,1003,1004" to="800"/>
  <onback from="2001,2002,2003,2004" to="801"/>
</navigation>
```

| Attribute | Description |
|-----------|-------------|
| `from` | Comma-separated list of control IDs |
| `to` | Target control ID when back is pressed |

## Condition Syntax

Conditions use a simple expression syntax:

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `widgetType=movies` |
| `~` | Contains | `widgetPath~skin.helper` |
| `!` | Negation | `!widgetType=weather` |
| `\|` | OR | `widgetType=movies \| tvshows` |
| `+` | AND | `widgetStyle=Panel + widgetArt=Poster` |
| `[...]` | Grouping | `![widgetType=weather \| system]` |

### Compact OR Syntax

Property name carries forward:

```
widgetType=movies | episodes | tvshows
```

Expands to:

```
widgetType=movies | widgetType=episodes | widgetType=tvshows
```

### Examples

```xml
<!-- Simple equality -->
condition="widgetType=movies"

<!-- Multi-value (OR) -->
condition="widgetType=movies | tvshows | episodes"

<!-- Negation -->
condition="!widgetType=weather"

<!-- Contains -->
condition="widgetPath~skin.helper"

<!-- AND -->
condition="widgetStyle=Panel + widgetArt=Poster"

<!-- Negated group -->
condition="![widgetType=weather | system]"
```
