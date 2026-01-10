# builders/includes.py

**Path:** `resources/lib/skinshortcuts/builders/includes.py`
**Purpose:** Build script-skinshortcuts-includes.xml from menu models.

***

## Overview

Produces the final includes.xml file that Kodi reads. Generates menu includes, submenu includes, custom widget includes, and delegates to TemplateBuilder for template-based includes.

***

## IncludesBuilder Class

### `__init__`(menus, templates=None, property_schema=None)

| Parameter | Description |
|-----------|-------------|
| `menus` | list[Menu] to build |
| `templates` | Optional TemplateSchema for template-based includes |
| `property_schema` | Optional PropertySchema for template_only filtering |

### build() → ET.Element

Build the includes XML tree. For each root menu:
1. Menu include (`skinshortcuts-{name}`)
2. Submenu include (`skinshortcuts-{name}-submenu`)
3. Custom widget includes (`skinshortcuts-{item}-customwidget{n}`)
4. Template includes (if templates defined)

### write(path, indent=True)

Write includes XML to file.

***

## Output Structure

### Standard Item Output

```xml
<item id="1">
  <label>Movies</label>
  <label2>...</label2>
  <icon>...</icon>
  <thumb>...</thumb>
  <onclick condition="...">action</onclick>
  <visible>condition</visible>
  <property name="id">1</property>
  <property name="name">movies</property>
  <property name="menu">mainmenu</property>
  <property name="path">ActivateWindow(...)</property>
  ...custom properties...
</item>
```

### Control Type Output

When `menu.controltype` is set (e.g., `"button"`):

```xml
<control type="button" id="8000">
  <label>Movies</label>
  <icon>...</icon>
  <include condition="...">BeforeInclude</include>
  <onclick>action</onclick>
  <include>AfterInclude</include>
  <visible>condition</visible>
</control>
```

Properties are not included in control output. Include references from defaults and items are placed based on their position (before-onclick or after-onclick). Control IDs start from `menu.startid` (parsed from the `id` attribute, default: 1).

**Action order:** before defaults → conditional item actions → unconditional item actions → after defaults

***

## Internal Methods

| Method | Purpose |
|--------|---------|
| `_build_menu_include` | Build main menu include, skips disabled items |
| `_build_submenu_include` | Build combined submenu include with parent refs and visibility |
| `_build_submenu_item` | Build submenu item with parent linking |
| `_build_custom_widget_includes` | Build includes by following `customWidget` property references |
| `_build_item` | Build single item element with all properties |
| `_is_template_only` | Check if property should be excluded from output |
