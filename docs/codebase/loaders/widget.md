# loaders/widget.py

**Path:** `resources/lib/skinshortcuts/loaders/widget.py`
**Lines:** 122
**Purpose:** Load widget configuration from widgets.xml.

***

## Overview

Parses the `widgets.xml` file which contains widget definitions and groups for the widget picker dialog. Widgets and groups are defined directly at the root level.

***

## Public Functions

### load_widgets(path) (line 13)

Load complete widget configuration from XML file.

Parses `<widget>` and `<group>` elements directly from root `<widgets>` element.
Widgets at root level appear flat in picker, groups create nested navigation.

**Parameters:**

* `path` - Path to widgets.xml

**Returns:** WidgetConfig containing:

* `widgets` - Flat list of all Widget objects (root-level only)
* `groupings` - List of widgets and groups for picker (includes both)
* `show_get_more` - Whether to show "Get More..." option

**Used by:** config.py (SkinConfig.load), dialog/properties.py

***

## Internal Functions

### `_parse_widget`(elem, path, default_source="") (line 52)

Parse a widget element.

**Required:**

* `name` attribute
* `label` attribute
* `<path>` child (except for type="custom")

**Attributes:**

* `name`, `label` - Required
* `type`, `target`, `icon`, `condition`, `visible`, `source`, `slot` - Optional

**Child Elements:**

* `<path>` - Required (except type="custom")
* `<sortby>`, `<sortorder>`, `<limit>` - Optional

**Source inheritance:** If widget has no `source` attribute, inherits `default_source` from parent group.

**Raises:** WidgetConfigError if missing required fields

***

### `_parse_widget_group`(elem, path, default_source="") (line 91)

Parse a widget group element.

**Required:**

* `name` attribute
* `label` attribute

**Optional:**

* `condition` attribute - Property condition
* `visible` attribute - Kodi visibility condition
* `icon` attribute - Icon for picker display
* `source` attribute (inherited by child widgets)

**Children parsed in document order:**

* `<widget>` → Widget
* `<group>` → WidgetGroup (recursive)
* `<content>` → Content

**Source inheritance:** Group's `source` is passed to child widgets/groups as `default_source`.

***

## XML Schema

```xml
<widgets showGetMore="true">
  <!-- Flat widget at root level -->
  <widget name="favourites" label="Favourites" type="videos" target="videos">
    <path>favourites://</path>
  </widget>

  <!-- Custom widget (no path required) -->
  <widget name="custom" label="Custom" type="custom" slot="widget" />

  <!-- Group with nested widgets -->
  <group name="movies" label="Movies" icon="DefaultMovies.png" source="library">
    <widget name="recentmovies" label="Recent" type="movies" icon="DefaultRecentlyAddedMovies.png">
      <path>videodb://recentlyaddedmovies/</path>
    </widget>

    <!-- Nested group -->
    <group name="genres" label="By Genre">
      <content source="library" target="moviegenres" />
    </group>
  </group>

  <!-- Group with visibility condition -->
  <group name="pvr" label="PVR" visible="PVR.HasTVChannels">
    <widget name="tvchannels" label="TV Channels" type="pvr">
      <path>pvr://channels/tv/</path>
    </widget>
  </group>
</widgets>
```

***

## Test Candidates

1. `load_widgets()` with complete widgets.xml
2. `_parse_widget()` with type="custom" (no path required)
3. `_parse_widget()` source inheritance from group
4. `_parse_widget_group()` with nested groups
5. Mixed groups and widgets at root level
