# Condition Syntax

Conditions filter items and control behavior based on property values.

***

## Table of Contents

* [Two Types of Conditions](#two-types-of-conditions)
* [Property Conditions](#property-conditions)
* [Kodi Visibility Conditions](#kodi-visibility-conditions)
* [Property Condition Syntax](#property-condition-syntax)
* [Operators](#operators)
* [Combining Conditions](#combining-conditions)
* [Compact OR Syntax](#compact-or-syntax)
* [Negation](#negation)
* [Grouping](#grouping)
* [Examples](#examples)

***

## Two Types of Conditions

Skin Shortcuts uses two types of conditions:

| Type | Attribute | Evaluated Against | When Evaluated |
|------|-----------|-------------------|----------------|
| Property | `condition` | Item properties dict | During dialog/picker operations |
| Kodi | `visible` | Kodi runtime state | Via `xbmc.getCondVisibility()` |

### Property Conditions

Checked against item's property dictionary:

```xml
<shortcut name="movie-widget" condition="widgetType=movies">
```

### Kodi Visibility Conditions

Checked against Kodi runtime state:

```xml
<shortcut name="tmdb-widget" visible="System.AddonIsEnabled(plugin.video.themoviedb.helper)">
```

***

## Property Conditions

Property conditions use a simple expression language to compare against the current item's properties.

### Where Used

* `<shortcut condition="...">` - Filter in shortcut picker
* `<group condition="...">` - Filter group in picker
* `<widget condition="...">` - Filter widget in picker
* `<background condition="...">` - Filter background in picker
* `<option condition="...">` - Filter property option
* `<source condition="...">` - Filter icon/browse source
* Template `<condition>` - Control template building
* Template `<property condition="...">` - Conditional property
* Template `<value condition="...">` - Conditional var value
* Fallback `<when condition="...">` - Conditional fallback

***

## Kodi Visibility Conditions

Evaluated at runtime using Kodi's condition system.

### Where Used

* `<shortcut visible="...">` - Filter in shortcut picker
* `<group visible="...">` - Filter group in picker
* `<widget visible="...">` - Filter widget in picker
* `<background visible="...">` - Filter background in picker
* `<item visible="...">` - Filter in management dialog
* `<source visible="...">` - Filter icon/browse source
* `<action condition="...">` - Conditional action execution

### Common Kodi Conditions

```xml
visible="Library.HasContent(movies)"
visible="System.AddonIsEnabled(plugin.video.example)"
visible="Skin.HasSetting(ShowAdvanced)"
visible="System.HasAddon(resource.images.moviegenreicons.transparent)"
visible="!String.IsEmpty(Window(Home).Property(SomeProperty))"
```

***

## Property Condition Syntax

### Property Exists (Truthy)

Check if property has any non-empty value:

```text
propertyName
```

```xml
<!-- True if widgetPath has any value -->
<shortcut condition="widgetPath">

<!-- True if suffix has any value (widget2 in multi-output) -->
<skinshortcuts include="HorizontalNavigation2" condition="suffix" />
```

### Property Empty (Falsy)

Check if property is empty or not set:

```text
!propertyName
propertyName EMPTY
```

Both forms are equivalent. See also: [EMPTY Operator](#empty-operator)

```xml
<!-- True if widgetPath is empty or not set -->
<shortcut condition="!widgetPath">

<!-- True if no suffix (widget1 in multi-output) -->
<skinshortcuts include="HorizontalNavigation1" condition="!suffix" />
```

### Equality

Check if property equals a value:

```text
propertyName=value
```

```xml
<shortcut condition="widgetType=movies">

<!-- Check for empty value explicitly -->
<option condition="suffix=">
```

### Contains

Check if property contains a substring:

```text
propertyName~value
```

```xml
<shortcut condition="widgetPath~videodb://">
```

***

## Operators

Operators can be written as symbols or keywords. Use whichever style you prefer.

### Comparison Operators

| Symbol | Keyword | Meaning | Example |
|--------|---------|---------|---------|
| *(none)* | - | Has value (truthy) | `widgetPath` |
| `=` | `EQUALS` | Equals | `widgetType=movies` or `widgetType EQUALS movies` |
| `~` | `CONTAINS` | Contains substring | `widgetPath~videodb://` or `widgetPath CONTAINS videodb://` |
| - | `EMPTY` | Is empty/not set | `widgetPath EMPTY` (same as `!widgetPath`) |
| - | `IN` | Value in list | `widgetType IN movies,episodes,tvshows` |

### Logical Operators

| Symbol | Keyword | Meaning | Example |
|--------|---------|---------|---------|
| `+` | `AND` | Both must be true | `cond1 + cond2` or `cond1 AND cond2` |
| `\|` | `OR` | Either must be true | `cond1 \| cond2` or `cond1 OR cond2` |
| `!` | `NOT` | Negate condition | `!widgetPath` or `NOT widgetPath` |

### EMPTY Operator

Check if a property is empty or not set:

```xml
<option condition="widgetPath EMPTY">
<option condition="NOT widgetPath EMPTY">
```

> **Equivalents:** These all mean "widgetPath is empty/not set":
> - `widgetPath EMPTY`
> - `!widgetPath`
> - `NOT widgetPath`

### IN Operator

Check if a property value matches any item in a comma-separated list:

```xml
<option condition="widgetType IN movies,episodes,tvshows">
```

Equivalent to `widgetType=movies | widgetType=episodes | widgetType=tvshows` but more concise.

***

## Combining Conditions

### AND

Both conditions must be true:

```text
condition1 + condition2
condition1 AND condition2
```

```xml
<option condition="widgetType=movies + widgetStyle=Panel">
<option condition="widgetType EQUALS movies AND widgetStyle EQUALS Panel">
```

### OR

Either condition must be true:

```text
condition1 | condition2
condition1 OR condition2
```

```xml
<shortcut condition="widgetType=movies | widgetType=tvshows">
<shortcut condition="widgetType EQUALS movies OR widgetType EQUALS tvshows">
```

### Mixed

AND has higher precedence than OR. Use grouping for complex logic:

```text
[condition1 | condition2] + condition3
```

***

## Compact OR Syntax

Compare one property against multiple values:

```text
propertyName=value1 | value2 | value3
```

Expands to:

```text
propertyName=value1 | propertyName=value2 | propertyName=value3
```

```xml
<!-- These are equivalent -->
<option condition="widgetType=movies | episodes | tvshows">
<option condition="widgetType=movies | widgetType=episodes | widgetType=tvshows">
```

***

## Negation

### Property Empty Check

Check if property is empty or not set:

```text
!propertyName
NOT propertyName
propertyName EMPTY
```

```xml
<!-- True when suffix is empty (widget1 in multi-output) -->
<skinshortcuts include="Navigation1" condition="!suffix" />
<skinshortcuts include="Navigation1" condition="NOT suffix" />
<skinshortcuts include="Navigation1" condition="suffix EMPTY" />

<!-- True when widgetPath is not set -->
<option condition="!widgetPath">
```

### Negated Equality

Check if property does NOT equal a value:

```text
!propertyName=value
NOT propertyName=value
```

```xml
<option condition="!widgetType=movies">
<option condition="NOT widgetType EQUALS movies">
```

### Negation in Compound Conditions

Negation applies to the immediately following term:

```text
!prop + other = (!prop) AND (other)
NOT prop AND other = (NOT prop) AND (other)
```

```xml
<!-- suffix empty AND widgetArt equals Poster -->
<option condition="!suffix + widgetArt=Poster">
<option condition="NOT suffix AND widgetArt EQUALS Poster">
```

### Grouped Negation

Negate an entire group:

```text
![condition1 | condition2]
```

```xml
<!-- True when widget is neither movies nor tvshows -->
<option condition="![widgetType=movies | widgetType=tvshows]">
```

***

## Grouping

Use brackets to control evaluation order:

```text
[condition1 | condition2] + [condition3 | condition4]
```

```xml
<!-- Widget is (movies or tvshows) AND style is (Panel or Wide) -->
<option condition="[widgetType=movies | widgetType=tvshows] + [widgetStyle=Panel | widgetStyle=Wide]">
```

Nested grouping:

```xml
<option condition="![widgetType=movies | [widgetType=tvshows + widgetStyle=Panel]]">
```

***

## Examples

### Filter by Widget Type

```xml
<option value="Poster" condition="widgetType=movies">
<option value="Square" condition="widgetType=albums">
<option value="Wide" condition="widgetType=episodes | widgetType=tvshows">
```

### Conditional Template

```xml
<template include="MovieWidgets">
  <condition>widgetType=movies</condition>
  <condition>widgetPath</condition>
</template>
```

Multiple `<condition>` elements are ANDed together.

### Property Fallback

```xml
<fallback property="widgetArt">
  <when condition="widgetType=movies">Poster</when>
  <when condition="widgetType=albums + widgetStyle=Panel">Cover</when>
  <when condition="widgetType~tv">Landscape</when>
  <default>Fanart</default>
</fallback>
```

### Picker Filtering

```xml
<groupings>
  <group name="library" label="Library" visible="Library.HasContent(movies)">
    <shortcut name="movies" label="Movies" condition="widgetType=movies" visible="Library.HasContent(movies)">
      <action>ActivateWindow(Videos,videodb://movies/)</action>
    </shortcut>
  </group>
</groupings>
```

### Multi-Output Templates and Suffix

For multi-widget support, templates can define multiple outputs with different suffixes:

```xml
<template name="Widgets">
  <output include="widget1" idprefix="8011" />
  <output include="widget2" idprefix="8021" suffix=".2" />
  ...
</template>
```

The `suffix` built-in property is available in conditions:

```xml
<!-- Widget 1 (no suffix) -->
<skinshortcuts include="HorizontalNavigation1" condition="!suffix" />
<values condition="!suffix" top="424" />

<!-- Widget 2 (suffix=.2) -->
<skinshortcuts include="HorizontalNavigation2" condition="suffix=.2" />
<values condition="suffix=.2" top="70" />

<!-- Any widget with a suffix -->
<option condition="suffix">
```

Suffixed properties can also be checked directly:

```xml
<option condition="widgetType.2=movies">
<when condition="widgetStyle.2=Panel">
```

Suffix transforms are applied automatically when using `suffix` attribute on outputs.

***

## Evaluation Order

1. Empty conditions return `true`
2. Compact OR syntax is expanded
3. Brackets are evaluated first (innermost to outermost)
4. AND (`+`) and OR (`|`) are split (AND binds tighter)
5. Negation (`!`) applies to the immediately following term
6. Property-only terms (`prop` or `!prop`) check for truthy/falsy value
7. Equality (`=`) and contains (`~`) compare against the value

***

## Quick Navigation

[Back to Top](#condition-syntax)

**Sections:** [Two Types](#two-types-of-conditions) | [Property Conditions](#property-conditions) | [Kodi Visibility](#kodi-visibility-conditions) | [Syntax](#property-condition-syntax) | [Operators](#operators) | [Combining](#combining-conditions) | [Compact OR](#compact-or-syntax) | [Negation](#negation) | [Grouping](#grouping) | [Examples](#examples)

**Related Docs:** [Templates](templates.md) | [Properties](properties.md) | [Menus](menus.md) | [Widgets](widgets.md)
