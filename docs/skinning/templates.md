# Template Configuration

The `templates.xml` file defines how the script generates include files. Templates transform menu items into Kodi-compatible XML.

---

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
  * [Dynamic Widgets Pattern](#dynamic-widgets-pattern)
  * [Troubleshooting "No Menu Items Matched"](#troubleshooting-no-menu-items-matched)
* [Property Groups](#property-groups)
* [Presets](#presets)
* [Preset Groups](#preset-groups)
* [Variables](#variables)
* [Expressions](#expressions)
* [Includes](#includes)
* [Submenus](#submenus)
* [Conditions](#conditions)
* [templateonly Attribute](#templateonly-attribute)
* [Complete Example](#complete-example)

---

## Overview

Without `templates.xml`, the script generates basic includes with menu items as `<item>` elements. Templates let you:

* Define custom control structures
* Create property-based visibility conditions
* Generate Kodi variables
* Build conditional includes

> **See also:** [Built-in Properties](builtin-properties.md) for available item properties

---

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
  <template include="Widgets" build="true">...</template>

  <!-- Submenu templates -->
  <submenu include="Submenu" level="1">...</submenu>
</templates>
```

---

## Template Element

```xml
<template include="MainMenu" idprefix="menu">
  <condition>...</condition>
  <property name="style" from="widgetStyle" />
  <var name="aspect">...</var>
  <propertyGroup content="widgetProps" />
  <preset content="aspectRatio" />
  <variableGroup content="widgetVars" />
  <controls>...</controls>
</template>
```

### Attributes

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `include` | Yes | - | Output include name (`skinshortcuts-template-{include}`) |
| `build` | No | `menu` | Build mode: `menu` or `true` |
| `idprefix` | No | - | Prefix for computed control IDs |
| `menu` | No | (all menus) | Restrict the template to a single menu by name (e.g. `mainmenu`). When omitted, the template runs against every menu. |
| `templateonly` | No | - | Skip include generation: `true` (always) or `auto` (if unassigned) |

---

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
2. **Conditions** are transformed: property names get suffixed whether they appear with a value (`condition="widgetType=movies"` → `condition="widgetType.2=movies"`) or as bare presence checks (`condition="widgetPath"` → `condition="widgetPath.2"`)
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
    <!-- Widget 2 (suffix=.2) -->
    <values condition="suffix=.2 + widgetArt=Poster" top="70" />
    <values condition="suffix=.2" top="112" />
    <!-- Widget 1 (default) -->
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

---

## Build Modes

### Menu Mode (Default)

Iterates over menu items:

```xml
<template include="MainMenu">
  <controls>
    <control type="button">
      <label>$PROPERTY[label]</label>
      <onclick>$PROPERTY[action]</onclick>
    </control>
  </controls>
</template>
```

Generates one copy of `<controls>` per menu item, with `$PROPERTY[name]` replaced by item values.

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

`$PARAM` is native Kodi include-parameter syntax, not a script feature; the script passes it through untouched. The template's `<param name="id" default="9000" />` declaration is not carried into the generated include, so the default is lost: always pass the param from the consuming include.

Raw mode also supports `<skinshortcuts>visibility</skinshortcuts>` markers. Instead of per-item visibility, the marker generates an OR'd condition across all matching menu items, outputting controls once with combined visibility. This is useful for elements that should be visible when *any* matching item is focused:

```xml
<template include="SharedBackground" build="true" menu="mainmenu">
  <condition>backgroundPath</condition>
  <controls>
    <control type="image">
      <skinshortcuts>visibility</skinshortcuts>
      <texture>background.jpg</texture>
    </control>
  </controls>
</template>
```

Output (single control, not repeated per item):

```xml
<control type="image">
  <visible>String.IsEqual(Container(9000).ListItem.Property(name),movies) | String.IsEqual(Container(9000).ListItem.Property(name),tvshows)</visible>
  <texture>background.jpg</texture>
</control>
```

If no items match the template's conditions, the visibility is set to `false`.

### Raw Mode with Properties

When a `build="true"` template defines properties, vars, or presets, the builder resolves them per menu item and deduplicates the output. Items that resolve to identical controls are grouped into a single control with OR'd visibility. Items that resolve differently get separate controls.

```xml
<template include="BackgroundWidget" build="true" menu="mainmenu">
  <property name="widgetTarget" condition="widgetTarget.backgroundWidget" from="widgetTarget.backgroundWidget" />
  <property name="widgetPath" condition="widgetPath.backgroundWidget" from="widgetPath.backgroundWidget" />
  <property name="widgetTarget">$INFO[Skin.String(widgetTarget)]</property>
  <property name="widgetPath">$INFO[Skin.String(widgetPath)]</property>
  <controls>
    <control type="wraplist">
      <content limit="25" target="$PROPERTY[widgetTarget]">$PROPERTY[widgetPath]</content>
      <skinshortcuts>visibility</skinshortcuts>
    </control>
  </controls>
</template>
```

If 3 items use the global skin string fallback and 1 item has a custom `backgroundWidget`, the output is 2 controls:

```xml
<!-- Items without custom background widget (deduplicated) -->
<control type="wraplist">
  <content limit="25" target="$INFO[Skin.String(widgetTarget)]">$INFO[Skin.String(widgetPath)]</content>
  <visible>...item1... | ...item3... | ...item4...</visible>
</control>

<!-- Item with custom background widget -->
<control type="wraplist">
  <content limit="25" target="movies">plugin://some.addon/path</content>
  <visible>...item2...</visible>
</control>
```

Without properties defined, raw mode outputs controls once with all visibility OR'd (no per-item processing).

---

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

### Override Pattern

When one property should override another based on a toggle, use mutually exclusive conditions so first-wins doesn't block the override:

```xml
<!-- Override: when "useCustomSort" toggle is set, use fixed value -->
<property name="sortby" condition="useCustomSort">custom_value</property>
<!-- Default: otherwise read from the item property -->
<property name="sortby" condition="!useCustomSort" from="widgetSortby" />
```

The `!useCustomSort` negation keeps the two branches mutually exclusive. Without it, the first property sets the value and the second's `from` would always overwrite (since `from` always wins when set).

This pattern lets a skinner bind two UI controls to the same effective output: a full picker for the default property, plus a quick toggle that overrides it when enabled.

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
| `action` | Full action string |
| `path` | Bare content path |
| `visible` | Visibility condition |

These come from the menu item's attributes, along with any custom properties set in menus.xml or by the user.

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
    <onclick>$PROPERTY[action]</onclick>
    <visible>$EXP[HasWidget]</visible>
  </control>
</controls>
```

### Placeholders

| Placeholder | Description |
|-------------|-------------|
| `$PROPERTY[name]` | Property or var value |
| `$EXP[name]` | Expression value (expanded in conditions) |
| `$PARAM[name]` | Native Kodi include parameter (raw mode); resolved by Kodi, not the script, and the `<param>` default is not emitted |

Note: Vars defined with `<var>` are resolved during context building and accessible via `$PROPERTY[name]`.

---

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
<visible>$IF[NOT widgetPath EMPTY THEN true ELSE false]</visible>
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
1. `$EXP[...]` - expression references
2. `$PARENT[...]` - parent item properties (items templates only)
3. `$PROPERTY[...]` - property substitution (resolved before `$MATH`/`$IF` so their inner refs are filled)
4. `$MATH[...]` - arithmetic expressions
5. `$IF[...]` - conditional expressions

`$INCLUDE[...]` conversion happens separately after substitution.

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

Outputs (per item in menu mode):

```xml
<control type="image">
  <visible>String.IsEqual(Container(9000).ListItem.Property(name),movies)</visible>
  <texture>/path/to/background.jpg</texture>
</control>
```

In `build="true"` (raw) mode, the same marker generates an OR'd condition across matching items. When properties are defined, items are grouped by resolved output and each group gets its own OR'd visibility. See [Raw Mode](#raw-mode) and [Raw Mode with Properties](#raw-mode-with-properties) for details.

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

### Onclick Expansion

Generate onclick elements from a menu item's actions:

```xml
<controls>
  <control type="button" id="$PROPERTY[id]">
    <label>$PROPERTY[label]</label>
    <skinshortcuts>onclick</skinshortcuts>
    <visible>$PROPERTY[visible]</visible>
  </control>
</controls>
```

The `<skinshortcuts>onclick</skinshortcuts>` element is replaced with all onclick elements from the item's actions, including:

1. **Before defaults** - Actions from menu's `<defaults>` with `when="before"`
2. **Conditional item actions** - Item actions with `condition` attribute
3. **Unconditional item actions** - Item actions without conditions
4. **After defaults** - Actions from menu's `<defaults>` with `when="after"`

Example output:

```xml
<control type="button" id="1">
  <label>Settings</label>
  <onclick>Dialog.Close(all,true)</onclick>
  <onclick condition="System.Platform.Windows">WindowsAction()</onclick>
  <onclick>ActivateWindow(Settings)</onclick>
  <onclick>AfterAction()</onclick>
  <visible>System.CanPowerDown</visible>
</control>
```

This enables creating button menus where each menu item becomes an individual button control with full action support.

### Attributes Summary

| Attribute | Required | Description |
|-----------|----------|-------------|
| `include` | No | Name of include definition to expand |
| `condition` | No | Condition expression (see [Conditions](conditions.md)) |
| `wrap` | No | If `true`, output as Kodi `<include>` element instead of unwrapping |

**Text content:**

| Value | Description |
|-------|-------------|
| `visibility` | Generate visibility condition matching current item (per-item in menu mode, OR'd in raw mode; per-group when properties are defined) |
| `onclick` | Generate onclick elements from item actions |

---

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

### Dynamic Widgets Pattern

This pattern allows unlimited, reorderable widgets per menu item using subdialogs and items templates together.

**How it works:**

1. User clicks a button (e.g., 406) to manage widgets for a menu item
2. A subdialog opens with `action="menu" menu="{item}.widgets"`
3. User adds/removes/reorders items in that submenu (each item = one widget)
4. The items template iterates over those submenu items to generate widget controls

**menus.xml configuration:**

```xml
<dialogs>
  <subdialog buttonID="406" mode="widgets" setfocus="309">
    <onclose action="menu" menu="{item}.widgets" />
  </subdialog>
</dialogs>
```

When button 406 is clicked, the dialog switches to "widgets" mode. When that mode closes, `action="menu"` opens the `{item}.widgets` submenu for editing (e.g., `movies.widgets` if the current item is "movies").

**templates.xml configuration:**

```xml
<!-- Items template: iterates over each widget in the submenu -->
<template items="widgets" source="widgets">
  <property name="widget_id" from="index" />
  <property name="widget_path" from="widgetPath" />

  <controls>
    <control type="group" id="$MATH[$PARENT[index] * 100 + widget_id]">
      <visible>String.IsEqual(Container(9000).ListItem.Property(name),$PARENT[name])</visible>
      <content>$PROPERTY[widget_path]</content>
    </control>
  </controls>
</template>

<!-- Regular template with insert marker -->
<template include="Widgets">
  <controls>
    <skinshortcuts insert="widgets" />
  </controls>
</template>
```

The items template looks up `{parent_item.name}.widgets` (e.g., `movies.widgets`) and generates controls for each widget item in that submenu.

### Troubleshooting "No Menu Items Matched"

If your template outputs `<description>Automatically generated - no menu items matched this template</description>`, check:

1. **Template condition** - If you have `<condition>someProperty</condition>`, ensure menu items have that property set
2. **Submenu exists** - The submenu `{item}.{source}` must exist (e.g., `movies.widgets` for `source="widgets"`)
3. **Submenu has items** - Empty submenus produce no output
4. **Filter too restrictive** - If using `filter="..."`, some items may be excluded

To iterate over all menu items without conditions, omit the `<condition>` element from your items template.

---

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
  <propertyGroup content="widgetProps" />
</template>
```

### Reference Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | Name of property group to apply |
| `suffix` | No | Suffix for property transforms (e.g., `.2`) |
| `condition` | No | Only apply if condition matches item |

```xml
<!-- Only apply widget props if item has a widget -->
<propertyGroup content="widgetProps" condition="widgetPath" />

<!-- Apply with suffix for Widget 2 -->
<propertyGroup content="widgetProps" suffix=".2" condition="widgetPath.2" />
```

### Suffix Transform

Apply suffix for widget slots:

```xml
<propertyGroup content="widgetProps" suffix=".2" />
```

Transforms:

* `from="widgetPath"` → `from="widgetPath.2"`
* `condition="widgetType=movies"` → `condition="widgetType.2=movies"`

> **See also:** [Properties](properties.md) for defining custom properties

---

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
  <preset content="widgetLayout" />
  <controls>
    <control type="panel" layout="$PROPERTY[layout]" />
  </controls>
</template>
```

All matched attributes become properties.

### Preset Reference Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | Name of preset to apply |
| `suffix` | No | Suffix for condition transforms (e.g., `.2`) |
| `condition` | No | Only apply if condition matches item |

```xml
<!-- Apply layout preset for Widget 2 properties -->
<preset content="widgetLayout" suffix=".2" condition="widgetPath.2" />
```

When `suffix` is specified, preset conditions like `widgetStyle=Panel` are transformed to `widgetStyle.2=Panel`.

---

## Preset Groups

Preset groups select between presets or inline values based on conditions. Children are evaluated in document order and the first matching condition wins.

```xml
<presetGroups>
  <presetGroup name="widgetSet">
    <preset content="posterLayout" condition="widgetArt=Poster" />
    <values condition="widgetType=movies" layout="wide" columns="4" />
    <preset content="defaultLayout" />
  </presetGroup>
</presetGroups>
```

Each `<presetGroup>` child is one of:

* `<preset content="name" condition="..." />` - apply a named preset when the condition matches
* `<values attr="val" ... condition="..." />` - apply inline attribute values when the condition matches

A child with no `condition` always matches and acts as the default. The first child whose condition passes is applied; remaining children are ignored.

Reference a preset group from a template, items template, or output:

```xml
<template include="MainMenu">
  <presetGroup content="widgetSet" />
</template>
```

### Preset Group Reference Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | Name of preset group to apply |
| `suffix` | No | Suffix for condition transforms (e.g., `.2`) |
| `condition` | No | Only apply if condition matches item |

```xml
<!-- Apply preset group for Widget 2 -->
<presetGroup content="widgetSet" suffix=".2" condition="widgetPath.2" />
```

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

Variable content supports the same expression substitution as raw template controls: `$PROPERTY[...]` for item properties, `$MATH[...]` for arithmetic, `$IF[...]` for conditionals, and `$EXP[...]` for expression refs. Example:

```xml
<variable name="widgetContainer" output="WidgetContainer-$PROPERTY[id]">
    <value>$MATH[id * 100 + 3101]</value>
</variable>
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
    <variable content="ItemLabel" />
  </variableGroup>
</variables>
```

Reference in template:

```xml
<template include="MainMenu">
  <variableGroup content="menuVars" />
</template>
```

### Variable Group Reference Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | Name of variable group to apply |
| `suffix` | No | Suffix for condition transforms (e.g., `.2`) |
| `condition` | No | Only build if condition matches item |

```xml
<!-- Build widget variables only for items with widgets -->
<variableGroup content="widgetVars" condition="widgetPath" />

<!-- Build Widget 2 variables with suffix transform -->
<variableGroup content="widgetVars" suffix=".2" condition="widgetPath.2" />
```

### Variable Attributes

| Attribute | Description |
|-----------|-------------|
| `name` | Variable name |
| `condition` | Build only when condition matches item |
| `output` | Output name pattern (supports `$PROPERTY[]`) |

### Value Attributes

| Attribute | Description |
|-----------|-------------|
| `condition` | Kodi condition; emitted as-is on the output `<value>` |
| `iterate` | Expand this `<value>` into multiple entries (see below) |
| `as` | Loop variable name; required when `iterate` is used |

### Iterating `<value>` Entries

A single `<value iterate="..." as="...">` expands into multiple `<value>` entries at build time. Useful when a variable needs one entry per numbered slot.

`iterate` accepts:
- A number (`iterate="9"`) - emits 9 entries, one per slot from 1 to 9.
- A `$PROPERTY[]` reference resolving to a number - same as above with a dynamic count.
- A property base name (`iterate="widgetPath"`) - scans the item for `widgetPath`, `widgetPath.2`, `widgetPath.3`, ... and emits one entry per filled slot. Gaps are preserved (e.g., if `.2` is unset but `.3` is set, only slots 1 and 3 emit).

`as` names the loop variable. Inside the value text and its `condition`, two placeholders resolve per iteration:
- `$PROPERTY[{as}Index]` - 1-based index (`1`, `2`, `3`, ...)
- `$PROPERTY[{as}Suffix]` - the slot suffix (`""`, `".2"`, `".3"`, ...)

All other `$PROPERTY[name]` references inside the value automatically gain the slot suffix. Built-in placeholders (`id`, `name`, `index`, `default`, `menu`, `idprefix`) stay unsuffixed.

Example - one value per filled widget slot:

```xml
<variable name="WidgetPath" output="Widget-$PROPERTY[id]-Path">
  <value iterate="widgetPath" as="slot"
         condition="Container($PROPERTY[id]).HasFocus($PROPERTY[slotIndex])">
    $PROPERTY[widgetPath]
  </value>
</variable>
```

For an item with `widgetPath`, `widgetPath.3` set, this emits:

```xml
<variable name="Widget-...-Path">
  <value condition="Container(...).HasFocus(1)">[widgetPath value]</value>
  <value condition="Container(...).HasFocus(2)">[widgetPath.3 value]</value>
</variable>
```

Example - fixed count of slots:

```xml
<value iterate="9" as="num">$PROPERTY[widgetName]$PROPERTY[numSuffix]</value>
```

---

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
<propertyGroup content="movieProps" condition="$EXP[IsMovies]" />
```

### The `nosuffix` Attribute

By default, property names inside an expression are suffix-transformed under a suffixed output or reference (e.g. in a `suffix=".2"` output, `widgetArt` becomes `widgetArt.2`). Set `nosuffix="true"` to keep the expression fixed so its property names are never suffixed:

```xml
<expression name="GlobalToggle" nosuffix="true">someGlobalProp</expression>
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
    <skinshortcuts include="FocusAnimation" />
  </control>
</controls>
```

See [Skinshortcuts Tag](#skinshortcuts-tag) for details on `include`, `condition`, and `wrap` attributes.

---

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
| `level` | Any value > 0 enables iteration over main menu items' direct submenus (looked up as `mainmenu/{item.name}`). The numeric value is not a depth selector; values above 1 behave the same as 1. |
| `name` | Match a single menu by exact name. When empty, the `level` attribute (>0) drives iteration over main menu items' submenus instead; with empty name and level 0, the submenu template produces no output. |

---

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

Templates using this pattern generate custom item lists where the template output becomes the widget content.

### Output Conversion

When `$INCLUDE[...]` appears as text content in an element (e.g., after `$PROPERTY[widgetPath]` substitution), it is automatically converted to a Kodi `<include>` element:

```xml
<!-- Input (after property substitution) -->
<content>$INCLUDE[skinshortcuts-template-MovieWidgets]</content>

<!-- Output -->
<content><include>skinshortcuts-template-MovieWidgets</include></content>
```

---

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
    <propertyGroup content="widget" />

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
          <include>skinshortcuts-WidgetItem-$PROPERTY[layout]</include>
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

---

[↑ Top](#template-configuration) · [Skinning Docs](index.md)
