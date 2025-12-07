# Condition Syntax

Conditions filter items and control behavior based on property values.

---

## Table of Contents

- [Two Types of Conditions](#two-types-of-conditions)
- [Property Conditions](#property-conditions)
- [Kodi Visibility Conditions](#kodi-visibility-conditions)
- [Property Condition Syntax](#property-condition-syntax)
- [Operators](#operators)
- [Combining Conditions](#combining-conditions)
- [Compact OR Syntax](#compact-or-syntax)
- [Negation](#negation)
- [Grouping](#grouping)
- [Examples](#examples)

---

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

---

## Property Conditions

Property conditions use a simple expression language to compare against the current item's properties.

### Where Used

- `<shortcut condition="...">` - Filter in shortcut picker
- `<group condition="...">` - Filter group in picker
- `<widget condition="...">` - Filter widget in picker
- `<option condition="...">` - Filter property option
- Template `<condition>` - Control template building
- Template `<property condition="...">` - Conditional property
- Template `<value condition="...">` - Conditional var value
- Fallback `<when condition="...">` - Conditional fallback

---

## Kodi Visibility Conditions

Evaluated at runtime using Kodi's condition system.

### Where Used

- `<shortcut visible="...">` - Filter in shortcut picker
- `<group visible="...">` - Filter group in picker
- `<widget visible="...">` - Filter widget in picker
- `<item visible="...">` - Filter in management dialog
- Background `<condition>` - Filter background option
- Icon `<source condition="...">` - Filter icon source

### Common Kodi Conditions

```xml
visible="Library.HasContent(movies)"
visible="System.AddonIsEnabled(plugin.video.example)"
visible="Skin.HasSetting(ShowAdvanced)"
visible="System.HasAddon(resource.images.moviegenreicons.transparent)"
visible="!String.IsEmpty(Window(Home).Property(SomeProperty))"
```

---

## Property Condition Syntax

### Equality

Check if property equals a value:

```
propertyName=value
```

```xml
<shortcut condition="widgetType=movies">
```

### Contains

Check if property contains a substring:

```
propertyName~value
```

```xml
<shortcut condition="widgetPath~videodb://">
```

---

## Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `=` | Equals | `widgetType=movies` |
| `~` | Contains | `widgetPath~videodb://` |
| `+` | AND | `widgetType=movies + widgetStyle=Panel` |
| `\|` | OR | `widgetType=movies \| widgetType=tvshows` |
| `!` | NOT | `!widgetType=movies` |

---

## Combining Conditions

### AND

Both conditions must be true:

```
condition1 + condition2
```

```xml
<option condition="widgetType=movies + widgetStyle=Panel">
```

### OR

Either condition must be true:

```
condition1 | condition2
```

```xml
<shortcut condition="widgetType=movies | widgetType=tvshows">
```

### Mixed

AND has higher precedence than OR. Use grouping for complex logic:

```
[condition1 | condition2] + condition3
```

---

## Compact OR Syntax

Compare one property against multiple values:

```
propertyName=value1 | value2 | value3
```

Expands to:

```
propertyName=value1 | propertyName=value2 | propertyName=value3
```

```xml
<!-- These are equivalent -->
<option condition="widgetType=movies | episodes | tvshows">
<option condition="widgetType=movies | widgetType=episodes | widgetType=tvshows">
```

---

## Negation

### Simple Negation

Negate a single condition:

```
!propertyName=value
```

```xml
<option condition="!widgetType=movies">
```

### Grouped Negation

Negate an entire group:

```
![condition1 | condition2]
```

```xml
<!-- True when widget is neither movies nor tvshows -->
<option condition="![widgetType=movies | widgetType=tvshows]">
```

---

## Grouping

Use brackets to control evaluation order:

```
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

---

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
  <condition>!String.IsEmpty(widgetPath)</condition>
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
    <shortcut name="movies" label="Movies"
              condition="widgetType=movies"
              visible="Library.HasContent(movies)">
      <action>ActivateWindow(Videos,videodb://movies/)</action>
    </shortcut>
  </group>
</groupings>
```

### Suffix in Conditions

For multi-widget support, conditions on suffixed properties:

```xml
<option condition="widgetType.2=movies">
<when condition="widgetStyle.2=Panel">
```

Suffix transforms are applied automatically when using `suffix` attribute on includes or button mappings.

---

## Evaluation Order

1. Empty conditions return `true`
2. Compact OR syntax is expanded
3. Brackets are evaluated first (innermost to outermost)
4. AND (`+`) binds tighter than OR (`|`)
5. Negation (`!`) applies to immediately following term

---

## Quick Navigation

[Back to Top](#condition-syntax)

**Sections:** [Two Types](#two-types-of-conditions) | [Property Conditions](#property-conditions) | [Kodi Visibility](#kodi-visibility-conditions) | [Syntax](#property-condition-syntax) | [Operators](#operators) | [Combining](#combining-conditions) | [Compact OR](#compact-or-syntax) | [Negation](#negation) | [Grouping](#grouping) | [Examples](#examples)

**Related Docs:** [Templates](templates.md) | [Properties](properties.md) | [Menus](menus.md) | [Widgets](widgets.md)
