# loaders/menu.py

**Path:** `resources/lib/skinshortcuts/loaders/menu.py`
**Lines:** 484
**Purpose:** Load menus, groupings, and related configuration from menus.xml.

***

## Overview

This is the primary loader for menu configuration. It parses the `menus.xml` file which contains menu definitions, shortcut groupings, icon sources, subdialog definitions, and action overrides.

***

## Public Functions

### load_menu_config(path) (line 28)

Load complete menu configuration from menus.xml.

**Parameters:**

* `path` - Path to menus.xml

**Returns:** MenuConfig containing:

* `menus` - All Menu objects
* `groupings` - Shortcut picker groups
* `icon_sources` - Icon picker sources
* `subdialogs` - Subdialog definitions
* `action_overrides` - Action replacement rules
* `show_context_menu` - Context menu visibility

**Used by:** config.py (SkinConfig.load), dialog.py

***

### load_groupings(path) (line 371)

Load shortcut groupings from menus.xml.

**Parameters:**

* `path` - Path to menus.xml

**Returns:** list[Group] from `<groupings>` element

**Used by:** dialog.py (shortcut picker without full config reload)

***

## Internal Functions

### `_parse_menus`(root, path) (line 58)

Parse `<menu>` and `<submenu>` elements from root.

***

### `_parse_icons`(root) (line 75)

Parse icon sources from `<icons>` element.

**Supports two formats:**

1. Simple: `<icons>path/to/icons/</icons>`
2. Advanced: `<icons><source label="..." condition="..." visible="...">path</source></icons>`

**Attributes parsed:**

* `label` - Display label in picker
* `condition` - Property condition (evaluated against item properties)
* `visible` - Kodi visibility condition (evaluated at runtime)
* `icon` - Icon for this source

***

### `_parse_context_menu`(root) (line 110)

Parse `<contextmenu>` element. Returns True by default.

***

### `_parse_dialogs`(root) (line 123)

Parse subdialog definitions from `<dialogs>` element.

**XML Schema:**

```xml
<dialogs>
  <subdialog buttonID="800" mode="widget1" setfocus="309" suffix=".2">
    <onclose condition="widgetType=custom" action="menu" menu="{item}.customwidget" />
  </subdialog>
</dialogs>
```

***

### `_parse_onclose`(subdialog_elem) (line 182)

Parse onclose actions from subdialog element.

***

### `_parse_overrides`(root) (line 205)

Parse action overrides from `<overrides>` element.

**XML Schema:**

```xml
<overrides>
  <action replace="ActivateWindow(favourites)">ActivateWindow(favouritesbrowser)</action>
</overrides>
```

***

### `_parse_menu`(elem, path, is_submenu=False) (line 228)

Parse a single menu element.

**Parses:**

* `name` attribute (required)
* `container` attribute
* `<item>` children
* `<defaults>` element
* `<allow>` element

***

### `_parse_item`(elem, menu_name, path) (line 252)

Parse a menu item element.

**Required:**

* `name` attribute
* `<label>` child
* At least one `<action>` child

**Optional:**

* `<label2>`, `<icon>`, `<thumb>`, `<visible>`, `<disabled>`
* `<property name="...">` children
* `<protect type="..." heading="..." message="..." />`
* `widget`, `background`, `submenu`, `required` attributes

**Note:** `widget` and `background` attributes are shorthand for properties.

***

### `_parse_defaults`(elem) (line 321)

Parse `<defaults>` element for menu-wide defaults.

**Supports:**

* `<property>` children
* `<action>` children with `when` and `condition` attributes
* `widget` and `background` attributes (shorthand for properties)

***

### `_parse_allow`(elem) (line 355)

Parse `<allow>` element for feature toggles.

***

### `_parse_groupings`(root, path) (line 404)

Parse `<groupings>` element containing shortcut picker groups.

***

### `_parse_group`(elem, path) (line 419)

Parse a group element with nested groups, shortcuts, and content refs.

**Children parsed in document order:**

* `<shortcut>` → Shortcut
* `<group>` → Group (recursive)
* `<content>` → Content

***

### `_parse_shortcut`(elem, path) (line 451)

Parse a shortcut element.

**Two modes:**

1. Action: `<action>ActivateWindow(...)</action>`
2. Browse: `browse="videos"` + `<path>videodb://...</path>`

***

## Dead Code Analysis

All code appears to be in active use.

***

## Test Candidates

1. `load_menu_config()` with complete menus.xml
2. `_parse_item()` with various optional fields
3. `_parse_shortcut()` action mode vs browse mode
4. `_parse_icons()` simple vs advanced format
5. `_parse_group()` with nested groups and content refs
6. Action override parsing and application
