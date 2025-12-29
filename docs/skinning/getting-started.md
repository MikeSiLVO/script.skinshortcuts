# Getting Started

This guide walks through integrating Skin Shortcuts into your skin.

***

## Table of Contents

* [Overview](#overview)
* [File Setup](#file-setup)
* [Basic Menu](#basic-menu)
* [Opening the Dialog](#opening-the-dialog)
* [Displaying the Menu](#displaying-the-menu)
* [Building Includes](#building-includes)
* [Adding Widgets](#adding-widgets)
* [Next Steps](#next-steps)

***

## Overview

Skin Shortcuts generates menu includes from XML configuration files. The workflow is:

1. Create configuration files in `shortcuts/`
2. User opens management dialog to customize
3. Script generates `script-skinshortcuts-includes.xml`
4. Skin displays menus using `<include>` elements

***

## File Setup

Create a `shortcuts/` folder in your skin root:

```
skin.name/
└── shortcuts/
    ├── menus.xml         # Required: Menu structure
    ├── widgets.xml       # Optional: Widget definitions
    ├── backgrounds.xml   # Optional: Background options
    ├── properties.xml    # Optional: Custom properties
    └── templates.xml     # Optional: Output templates
```

All files except `menus.xml` are optional. Start with just `menus.xml` and add others as needed.

***

## Basic Menu

Create `shortcuts/menus.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies">
      <label>$LOCALIZE[342]</label>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
      <icon>DefaultMovies.png</icon>
    </item>
    <item name="tvshows">
      <label>$LOCALIZE[20343]</label>
      <action>ActivateWindow(Videos,videodb://tvshows/)</action>
      <icon>DefaultTVShows.png</icon>
    </item>
    <item name="settings">
      <label>$LOCALIZE[10004]</label>
      <action>ActivateWindow(Settings)</action>
      <icon>DefaultAddonProgram.png</icon>
    </item>
  </menu>
</menus>
```

This defines a menu named `mainmenu` with three items.

***

## Opening the Dialog

Add a button to open the management dialog:

```xml
<control type="button">
  <label>Edit Menu</label>
  <onclick>RunScript(script.skinshortcuts,type=manage&amp;menu=mainmenu)</onclick>
</control>
```

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `type` | Yes | `manage` to open the management dialog |
| `menu` | Yes | Menu name to edit (e.g., `mainmenu`) |
| `path` | No | Custom shortcuts path (defaults to `special://skin/shortcuts/`) |

***

## Displaying the Menu

Use the generated include in your skin:

```xml
<control type="list" id="9000">
  <itemlayout>
    <control type="image">
      <texture>$INFO[ListItem.Icon]</texture>
    </control>
    <control type="label">
      <label>$INFO[ListItem.Label]</label>
    </control>
  </itemlayout>
  <focusedlayout>
    <!-- Focus styling -->
  </focusedlayout>
  <content>
    <include>skinshortcuts-mainmenu</include>
  </content>
</control>
```

**Include naming:** `skinshortcuts-{menu_name}`

Each include generates `<item>` elements with properties accessible via `ListItem.Property(name)`.

***

## Building Includes

The script automatically builds includes when the management dialog closes with changes. You can also trigger a manual build:

```xml
<onclick>RunScript(script.skinshortcuts,type=buildxml)</onclick>
```

**Build parameters:**

| Parameter | Description |
|-----------|-------------|
| `type=buildxml` | Trigger include build |
| `force=true` | Force rebuild even if unchanged |
| `path=...` | Custom shortcuts path |
| `output=...` | Custom output path |

**Output location:** `script-skinshortcuts-includes.xml` is written to each resolution folder defined in your skin's `addon.xml` (e.g., `16x9/`, `21x9/`).

***

## Adding Widgets

To let users assign widgets to menu items:

### 1. Define widgets in `widgets.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<widgets>
  <widget name="recent-movies" label="$LOCALIZE[20386]" type="movies">
    <path>videodb://recentlyaddedmovies/</path>
    <target>videos</target>
    <icon>DefaultRecentlyAddedMovies.png</icon>
  </widget>
</widgets>
```

### 2. Add widget button mapping in `properties.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<properties>
  <property name="widget" type="widget" />
  <buttons>
    <button id="309" property="widget" type="widget" />
  </buttons>
</properties>
```

### 3. Add widget button to dialog:

```xml
<control type="button" id="309">
  <label>Choose Widget</label>
</control>
```

Button IDs are configured in `properties.xml`. See [Properties](properties.md) for full configuration.

### 4. Display widget content:

```xml
<control type="list" id="3000">
  <content target="$INFO[Container(9000).ListItem.Property(widgetTarget)]">
    $INFO[Container(9000).ListItem.Property(widgetPath)]
  </content>
</control>
```

***

## Next Steps

* [Menus](menus.md) - Full menu configuration reference
* [Widgets](widgets.md) - Widget definitions and picker groupings
* [Backgrounds](backgrounds.md) - Background options
* [Properties](properties.md) - Custom property schemas
* [Management Dialog](management-dialog.md) - Dialog control IDs and properties

***

## Quick Navigation

[Back to Top](#getting-started)

**Sections:** [Overview](#overview) | [File Setup](#file-setup) | [Basic Menu](#basic-menu) | [Opening the Dialog](#opening-the-dialog) | [Displaying the Menu](#displaying-the-menu) | [Building Includes](#building-includes) | [Adding Widgets](#adding-widgets) | [Next Steps](#next-steps)

**Related Docs:** [Files](files.md) | [Menus](menus.md) | [Widgets](widgets.md) | [Properties](properties.md) | [Management Dialog](management-dialog.md)
