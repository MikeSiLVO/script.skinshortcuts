# Management Dialog

## Table of Contents

- [Opening](#opening)
- [Control IDs](#control-ids)
- [List Properties](#list-properties)
- [Window Properties](#window-properties)

## Opening

```xml
<onclick>RunScript(script.skinshortcuts,type=manage&amp;menu=mainmenu)</onclick>
```

| Parameter | Description |
|-----------|-------------|
| `type` | `manage` |
| `menu` | Menu name |

## Control IDs

### Core Controls

| ID | Function |
|----|----------|
| 211 | Menu items list |
| 301 | Add item |
| 302 | Delete item |
| 303 | Move up |
| 304 | Move down |
| 305 | Change label |
| 306 | Change icon |
| 307 | Change action |
| 308 | Reset to defaults |
| 313 | Toggle enabled/disabled |
| 401 | Choose shortcut |
| 405 | Edit submenu |

### Property Controls

| ID | Function |
|----|----------|
| 311 | Background picker |
| 312 | Widget picker |
| 401+ | Custom properties |

## List Properties

Properties available on items in list 211:

| Property | Description |
|----------|-------------|
| `ListItem.Label` | Item label |
| `ListItem.Label2` | Secondary label |
| `ListItem.Icon` | Item icon |
| `ListItem.Property(action)` | Action |
| `ListItem.Property(widget)` | Widget ID |
| `ListItem.Property(widgetName)` | Widget name |
| `ListItem.Property(background)` | Background ID |
| `ListItem.Property(backgroundName)` | Background name |
| `ListItem.Property(disabled)` | Is disabled |
| `ListItem.Property(required)` | Cannot delete |
| `ListItem.Property(submenu)` | Submenu name |

## Window Properties

| Property | Description |
|----------|-------------|
| `groupname` | Current menu ID |
| `hasChanges` | Unsaved changes exist |

## Dialog XML

Minimal example:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<window type="dialog">
  <defaultcontrol always="true">211</defaultcontrol>

  <controls>
    <control type="list" id="211">
      <itemlayout>
        <control type="image">
          <texture>$INFO[ListItem.Icon]</texture>
        </control>
        <control type="label">
          <label>$INFO[ListItem.Label]</label>
        </control>
      </itemlayout>
      <focusedlayout>
        <!-- focus styling -->
      </focusedlayout>
    </control>

    <control type="button" id="301"><label>Add</label></control>
    <control type="button" id="302"><label>Delete</label></control>
    <control type="button" id="303"><label>Up</label></control>
    <control type="button" id="304"><label>Down</label></control>
    <control type="button" id="305"><label>Label</label></control>
    <control type="button" id="401"><label>Choose Shortcut</label></control>
    <control type="button" id="312"><label>Widget</label></control>
    <control type="button" id="311"><label>Background</label></control>
    <control type="button" id="405">
      <label>Edit Submenu</label>
      <visible>!String.IsEmpty(Container(211).ListItem.Property(submenu))</visible>
    </control>
  </controls>
</window>
```
