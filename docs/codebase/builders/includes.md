# builders/includes.py

**Path:** `resources/lib/skinshortcuts/builders/includes.py`
**Lines:** 291
**Purpose:** Build script-skinshortcuts-includes.xml from menu models.

---

## Overview

The IncludesBuilder takes menu models and produces the final includes.xml file that Kodi reads. It generates menu includes, submenu includes, custom widget includes, and template-based includes.

---

## IncludesBuilder Class (line 15)

### __init__(menus, templates=None, property_schema=None) (line 18)
Initialize builder.

**Parameters:**
- `menus` - list[Menu] to build
- `templates` - Optional TemplateSchema for template-based includes
- `property_schema` - Optional PropertySchema for template_only filtering

**Instance attributes:**
- `_menu_map` - dict mapping menu.name → Menu for quick lookup

---

### build() → ET.Element (line 29)
Build the includes XML tree.

**Build order:**
1. For each root menu (is_submenu=False):
   - Menu include (`skinshortcuts-{name}`)
   - Submenu include (`skinshortcuts-{name}-submenu`)
   - Custom widget includes (`skinshortcuts-{item}-customwidget{n}`)
2. Template includes (if templates defined)

**Returns:** ET.Element root `<includes>`

**Used by:** config.py (SkinConfig.build_includes)

---

### write(path, indent=True) (line 268)
Write includes XML to file.

**Parameters:**
- `path` - Output file path
- `indent` - Whether to add indentation (default True)

**Used by:** config.py (SkinConfig.build_includes)

---

## Internal Methods

### _build_menu_include(menu) (line 76)
Build main menu include.

**Output:** `<include name="skinshortcuts-{menu.name}">`

Skips disabled items.

---

### _build_submenu_include(parent_menu) (line 88)
Build combined submenu include for a root menu.

**Output:** `<include name="skinshortcuts-{menu.name}-submenu">`

Collects all submenu items from all parent items that have submenus, builds each with parent reference and visibility condition.

---

### _build_submenu_item(item, idx, parent_item, menu, container) (line 118)
Build a submenu item with parent linking.

**Adds:**
- `parent` property pointing to parent item
- Visibility condition based on container selection

---

### _build_custom_widget_includes(parent_menu) (line 148)
Build custom widget includes for a root menu.

**Pattern:** Searches for menus named `{item.name}.customwidget` through `.customwidget.10`

**Output:** `<include name="skinshortcuts-{item}-customwidget{n}">`

---

### _build_item(item, idx, menu) (line 185)
Build a single item element.

**Structure:**
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

**Action order:**
1. Before default actions
2. Conditional item actions
3. Unconditional item actions
4. After default actions

---

### _is_template_only(prop_name) (line 250)
Check if property is marked template_only in schema.

Template-only properties are used by TemplateBuilder but not included in menu item output.

---

### _add_property(parent, name, value) (line 261)
Static method to add a property element to parent.

---

## Module Function

### _indent_xml(elem, level=0) (line 277)
Add indentation to XML tree for readable output.

---

## Dead Code Analysis

All code appears to be in active use.

---

## Test Candidates

1. `build()` with menus having submenus
2. `_build_submenu_item()` visibility condition generation
3. `_build_custom_widget_includes()` with various slot suffixes
4. `_build_item()` action ordering (before/conditional/unconditional/after)
5. Template_only property filtering
