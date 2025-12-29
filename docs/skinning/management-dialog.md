# Management Dialog

The management dialog (`script-skinshortcuts.xml`) provides the UI for editing menus.

***

## Table of Contents

* [Overview](#overview)
* [Dialog XML](#dialog-xml)
* [Control IDs](#control-ids)
* [Window Properties](#window-properties)
* [ListItem Properties](#listitem-properties)
* [Subdialogs](#subdialogs)
* [Script Commands](#script-commands)

***

## Overview

The script opens a WindowXMLDialog from your skin's `script-skinshortcuts.xml`. You design the layout and controls; the script handles the logic.

***

## Dialog XML

Create `script-skinshortcuts.xml` in your skin's XML folder:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<window>
  <defaultcontrol always="true">211</defaultcontrol>

  <controls>
    <!-- Menu items list -->
    <control type="list" id="211">
      <itemlayout>
        <control type="image">
          <texture>$INFO[ListItem.Icon]</texture>
        </control>
        <control type="label">
          <label>$INFO[ListItem.Label]</label>
        </control>
      </itemlayout>
      <focusedlayout>...</focusedlayout>
    </control>

    <!-- Action buttons -->
    <control type="button" id="301"><label>Add</label></control>
    <control type="button" id="302"><label>Delete</label></control>
    <control type="button" id="303"><label>Move Up</label></control>
    <control type="button" id="304"><label>Move Down</label></control>
    <control type="button" id="305"><label>Change Label</label></control>
    <control type="button" id="306"><label>Change Icon</label></control>
    <control type="button" id="307"><label>Change Action</label></control>

    <!-- Optional buttons -->
    <control type="button" id="311"><label>Restore Deleted</label></control>
    <control type="button" id="312"><label>Reset to Default</label></control>
    <control type="button" id="313"><label>Enable/Disable</label></control>
    <control type="button" id="401"><label>Choose Shortcut</label></control>
    <control type="button" id="405"><label>Edit Submenu</label></control>
  </controls>
</window>
```

***

## Control IDs

### Required Controls

| ID | Function |
|----|----------|
| `211` | Menu items list (required) |
| `212` | Subdialog context list (optional) |

Control 212 is a single-item list that mirrors the currently selected item from 211. Use it in subdialogs to read item properties without conflicting with the main list:

```xml
<!-- In subdialog mode, read from 212 instead of 211 -->
<label>$INFO[Container(212).ListItem.Property(widgetLabel)]</label>
```

### Built-in Buttons

| ID | Function |
|----|----------|
| `301` | Add new item |
| `302` | Delete selected item |
| `303` | Move item up |
| `304` | Move item down |
| `305` | Change label (keyboard input) |
| `306` | Change icon (file browser) |
| `307` | Change action (keyboard input) |
| `311` | Restore a deleted item |
| `312` | Reset current item to default |
| `313` | Toggle disabled state |
| `401` | Choose shortcut from groupings |
| `405` | Edit submenu |

### Custom Buttons

All property buttons (widget, background, custom options) are configured in `properties.xml`. Common conventions:

| ID Range | Typical Use |
|----------|-------------|
| `309` | Widget picker |
| `310` | Background picker |
| `350-399` | Custom property buttons |
| `800+` | Subdialog triggers (via `menus.xml`) |

These are not built-in - you must define button mappings in your `properties.xml`.

***

## Window Properties

Properties set on the dialog window for conditional visibility:

### Menu Context

| Property | Description |
|----------|-------------|
| `menuname` | Current menu ID (e.g., `mainmenu`) |
| `allowWidgets` | `true` or `false` |
| `allowBackgrounds` | `true` or `false` |
| `allowSubmenus` | `true` or `false` |
| `skinshortcuts-hasdeleted` | `true` if deleted items exist |

### Subdialog Mode (Home Window)

These properties are set on the **Home window** (not the dialog) so they remain accessible when native dialogs (like DialogSelect) are open:

| Property | Description |
|----------|-------------|
| `skinshortcuts-dialog` | Current subdialog mode (empty for main) |
| `skinshortcuts-suffix` | Current property suffix (e.g., `.2`) |

### Usage

```xml
<!-- Menu context properties (on dialog window) -->
<visible>String.IsEqual(Window.Property(allowWidgets),true)</visible>

<!-- Subdialog properties (on Home window) -->
<visible>String.IsEmpty(Window(Home).Property(skinshortcuts-dialog))</visible>
<visible>String.IsEqual(Window(Home).Property(skinshortcuts-dialog),widget1)</visible>
<visible>String.IsEqual(Window(Home).Property(skinshortcuts-suffix),.2)</visible>
```

***

## ListItem Properties

Properties available on items in the menu list (control 211):

### Core Properties

| Property | Description |
|----------|-------------|
| `ListItem.Label` | Display label |
| `ListItem.Label2` | Primary action |
| `ListItem.Icon` | Icon path |
| `ListItem.Property(name)` | Item identifier |
| `ListItem.Property(path)` | Primary action |
| `ListItem.Property(skinshortcuts-disabled)` | `True` or `False` |

### Widget Properties

| Property | Description |
|----------|-------------|
| `ListItem.Property(widget)` | Widget name |
| `ListItem.Property(widgetLabel)` | Widget display label |
| `ListItem.Property(widgetPath)` | Widget content path |
| `ListItem.Property(widgetType)` | Widget content type |
| `ListItem.Property(widgetTarget)` | Widget target window |

### Background Properties

| Property | Description |
|----------|-------------|
| `ListItem.Property(background)` | Background name |
| `ListItem.Property(backgroundLabel)` | Background display label |
| `ListItem.Property(backgroundPath)` | Background image path |

### Submenu Properties

| Property | Description |
|----------|-------------|
| `ListItem.Property(hasSubmenu)` | `true` if item has submenu |
| `ListItem.Property(submenu)` | Submenu name |

### Status Properties

| Property | Description |
|----------|-------------|
| `ListItem.Property(isResettable)` | `true` if modified from default |
| `ListItem.Property(skinshortcuts-isRequired)` | `True` if item cannot be deleted/disabled |
| `ListItem.Property(skinshortcuts-isProtected)` | `True` if item has protection rules |

### Custom Properties

Any property defined in `properties.xml`:

```xml
<visible>!String.IsEmpty(Container(211).ListItem.Property(widgetStyle))</visible>
<label>$INFO[Container(211).ListItem.Property(widgetStyleLabel)]</label>
```

Properties with options also get a `{name}Label` property with the resolved label.

***

## Subdialogs

Subdialogs support multi-widget editing by opening the same dialog with a different mode.

### Configuration

In `menus.xml`:

```xml
<dialogs>
  <subdialog buttonID="800" mode="widget1" setfocus="309" />
  <subdialog buttonID="801" mode="widget2" setfocus="309" suffix=".2">
    <onclose condition="widgetType.2=custom" action="menu" menu="{item}.customwidget.2" />
  </subdialog>
</dialogs>
```

### Dialog Behavior

When button 800 is clicked:

1. `Window(Home).Property(skinshortcuts-dialog)` = `widget1`
2. Focus moves to control 309
3. UI updates to show widget 1 controls

When button 801 is clicked:

1. `Window(Home).Property(skinshortcuts-dialog)` = `widget2`
2. `Window(Home).Property(skinshortcuts-suffix)` = `.2`
3. Property reads/writes use `.2` suffix (e.g., `widgetPath.2`)

### Skin Layout

Use visibility conditions to show different controls. Note that subdialog properties are on the Home window:

```xml
<!-- Main dialog controls -->
<control type="group">
  <visible>String.IsEmpty(Window(Home).Property(skinshortcuts-dialog))</visible>
  <!-- Main menu editing controls -->
</control>

<!-- Widget 1 subdialog controls -->
<control type="group">
  <visible>String.IsEqual(Window(Home).Property(skinshortcuts-dialog),widget1)</visible>
  <!-- Widget editing controls -->
</control>

<!-- Widget 2 subdialog controls -->
<control type="group">
  <visible>String.IsEqual(Window(Home).Property(skinshortcuts-dialog),widget2)</visible>
  <!-- Widget editing controls (same layout, different suffix) -->
</control>
```

### OnClose Actions

Execute actions when subdialog closes:

```xml
<onclose condition="widgetType.2=custom" action="menu" menu="{item}.customwidget.2" />
```

* `{item}` is replaced with current item name
* Opens item editor for custom widget menu

***

## Script Commands

### Open Management Dialog

```xml
<onclick>RunScript(script.skinshortcuts,type=manage&amp;menu=mainmenu)</onclick>
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `type` | Yes | `manage` |
| `menu` | Yes | Menu ID to edit |
| `path` | No | Custom shortcuts path |

### Build Includes

```xml
<onclick>RunScript(script.skinshortcuts,type=buildxml)</onclick>
<onclick>RunScript(script.skinshortcuts,type=buildxml&amp;force=true)</onclick>
```

| Parameter | Description |
|-----------|-------------|
| `type` | `buildxml` |
| `force` | `true` to force rebuild |
| `path` | Custom shortcuts path |
| `output` | Custom output path |

### Reset All Menus

```xml
<onclick>RunScript(script.skinshortcuts,type=resetall)</onclick>
```

Prompts for confirmation, then deletes userdata and rebuilds.

### Clear Custom Menu

```xml
<onclick>RunScript(script.skinshortcuts,type=clear&amp;menu=movies.customwidget&amp;property=widget)</onclick>
```

| Parameter | Description |
|-----------|-------------|
| `type` | `clear` |
| `menu` | Custom menu name to clear |
| `property` | Property to clear on parent item |

***

## Dialog Flow

1. User clicks "Edit Menu" button in skin
2. Script opens `script-skinshortcuts.xml`
3. List control 211 populates with menu items
4. User edits items using control buttons
5. User presses back/close
6. Script saves changes and closes dialog
7. Script rebuilds includes if changes were made
8. Skin reloads to apply new includes

***

## Quick Navigation

[Back to Top](#management-dialog)

**Sections:** [Overview](#overview) | [Dialog XML](#dialog-xml) | [Control IDs](#control-ids) | [Window Properties](#window-properties) | [ListItem Properties](#listitem-properties) | [Subdialogs](#subdialogs) | [Script Commands](#script-commands) | [Dialog Flow](#dialog-flow)

**Related Docs:** [Getting Started](getting-started.md) | [Menus](menus.md) | [Properties](properties.md) | [Builtin Properties](builtin-properties.md)
