# Widget Configuration

The `widgets.xml` file defines widgets that users can assign to menu items.

---

## Table of Contents

* [File Structure](#file-structure)
* [Widget Element](#widget-element)
* [Widget Types](#widget-types)
* [Groups](#groups)
* [Dynamic Content](#dynamic-content)
* [Conditions](#conditions)
* [Output Properties](#output-properties)
* [Multiple Widgets](#multiple-widgets)
* [Widget Menus](#widget-menus)
* [Widget Picker Button](#widget-picker-button)
* [Standalone Widget Picker](#standalone-widget-picker)

---

## File Structure

Widgets and groups are defined directly at the root level:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<widgets>
  <!-- Flat widget (appears ungrouped in picker) -->
  <widget name="favourites" label="Favourites" type="videos">
    <path>favourites://</path>
  </widget>

  <!-- Group of widgets (creates nested navigation in picker) -->
  <group name="movies" label="Movies" visible="Library.HasContent(movies)">
    <widget name="recent-movies" label="Recently Added" type="movies">
      <path>videodb://recentlyaddedmovies/</path>
    </widget>
  </group>
</widgets>
```

---

## Widget Element

```xml
<widget name="recent-movies" label="$LOCALIZE[20386]" type="movies" target="videos" icon="DefaultRecentlyAddedMovies.png" source="library" condition="..." visible="...">
  <path>videodb://recentlyaddedmovies/</path>
  <limit>25</limit>
  <sortby>dateadded</sortby>
  <sortorder>descending</sortorder>
</widget>
```

### Attributes

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `name` | Yes | - | Unique identifier |
| `label` | Yes | - | Display label |
| `type` | No | - | Content type (e.g., `movies`, `episodes`, `albums`) |
| `target` | No | `videos` | Target window: `videos`, `music`, `pictures`, `programs` |
| `icon` | No | - | Icon for picker |
| `source` | No | - | Source type: `library`, `playlist`, `addon`. Inherited from parent group if not set |
| `condition` | No | - | Property condition (evaluated against item properties) |
| `visible` | No | - | Kodi visibility condition (evaluated at runtime) |
| `slot` | No | - | Restricts this widget to a specific widget slot (e.g. `widget`, `widget.2`); the widget appears in the picker only when that slot is being edited. Applies to all widget types. A widget with no slot shows for every slot. |
| `browse` | No | `false` | `true` to allow browse-into during picker (see [Browse Into](#browse-into)) |

### Child Elements

| Element | Required | Default | Description |
|---------|----------|---------|-------------|
| `<path>` | Yes\* | - | Content path. \*Not required for `type="custom"` |
| `<limit>` | No | - | Maximum number of items |
| `<sortby>` | No | - | Sort field |
| `<sortorder>` | No | - | Sort direction: `ascending` or `descending` |

### Path Examples

```xml
<!-- Library path -->
<path>videodb://recentlyaddedmovies/</path>

<!-- Library node -->
<path>library://video/movies/inprogress.xml/</path>

<!-- Playlist -->
<path>special://skin/playlists/movies.xsp</path>

<!-- Add-on -->
<path>plugin://plugin.video.example/?action=list</path>
```

---

## Widget Types

The `type` attribute helps skins identify content type for styling:

| Type | Content |
|------|---------|
| `movies` | Movies |
| `tvshows` | TV Shows |
| `episodes` | Episodes |
| `musicvideos` | Music Videos |
| `sets` | Movie Sets |
| `albums` | Music Albums |
| `artists` | Artists |
| `songs` | Songs |
| `pictures` | Pictures |
| `pvr` | PVR Content |
| `games` | Games |
| `addons` | Add-ons |
| `custom` | Custom (user-defined items) |

### Browse Into

By default, selecting a widget in the picker assigns the widget as-is. Set `browse="true"` to let users browse into the widget's path and pick a sub-location instead:

```xml
<widget name="movies-browser" label="Browse Movies" type="movies" browse="true">
  <path>videodb://movies/</path>
</widget>
```

When browsing, the user navigates directories and the first entry ("Create menu item to here") uses the current location as-is. `<content source="addons">` resolves plugin-source addons as browsable automatically, no attribute needed in that case.

### Custom Widgets

Custom widgets let users define their own item list:

```xml
<widget name="custom-items" label="Custom Widget" type="custom" slot="widget">
  <!-- No path required - items are user-defined -->
</widget>
```

When selected, the dialog opens an item editor for the custom menu.

---

## Groups

Organize widgets into categories for the picker dialog:

```xml
<widgets>
  <!-- Group creates nested navigation -->
  <group name="movies" label="Movies" icon="DefaultMovies.png" visible="Library.HasContent(movies)">
    <widget name="recent" label="Recently Added" type="movies">
      <path>videodb://recentlyaddedmovies/</path>
    </widget>

    <widget name="inprogress" label="In Progress" type="movies">
      <path>videodb://inprogressmovies/</path>
    </widget>

    <!-- Nested group -->
    <group name="genres" label="By Genre">
      <content source="library" target="moviegenres" />
    </group>

    <!-- Dynamic content -->
    <content source="playlists" target="videos" />
  </group>

  <!-- Flat widget (no group) -->
  <widget name="favourites" label="Favourites" type="videos">
    <path>favourites://</path>
  </widget>

  <!-- Dynamic content at root -->
  <content source="playlists" target="videos" folder="Video Playlists" />
</widgets>
```

Top-level `<widgets>` accepts `<widget>`, `<group>`, and `<content>`. Use `folder="..."` on a `<content>` to wrap its resolved entries in a picker folder.

### `<group>` Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier |
| `label` | Yes (unless `flat="true"`) | Display label for the folder header |
| `icon` | No | Icon for picker display (default: `DefaultFolder.png`) |
| `condition` | No | Property condition (evaluated against item properties) |
| `visible` | No | Kodi visibility condition (evaluated at runtime) |
| `flat` | No | When `true`, children appear inline at parent level instead of inside a folder |

Groups can contain:

* `<widget>` - Widget definitions
* `<group>` - Nested groups
* `<content>` - Dynamic content

### Flat Groups

A group with `flat="true"` does not render as a folder. Its children appear at the parent level when the group's `condition` and `visible` both pass. This lets a single picker invocation expose different widget sets without per-widget visibility conditions.

```xml
<widgets>
  <group name="spotlight" flat="true" visible="String.IsEqual(Window(Home).Property(widgetContext),spotlight)">
    <widget name="recent-movies" label="Recent Movies" type="movies">
      <path>videodb://recentlyaddedmovies/</path>
    </widget>
    <widget name="watchlist" label="Watchlist" type="movies">
      <path>plugin://plugin.video.themoviedb.helper/?info=watchlist</path>
    </widget>
  </group>

  <group name="fallback" flat="true" visible="String.IsEqual(Window(Home).Property(widgetContext),fallback)">
    <widget name="genres" label="Genres" type="moviegenres">
      <path>videodb://movies/genres/</path>
    </widget>
  </group>
</widgets>
```

Pair flat groups with a window property the picker is invoked with. The condition references that property; only the matching group's widgets appear at the top level. Pass the property using paired `prop=NAME,value=VALUE` args in the script call (see [Window Property Pass-Through](management-dialog.md#window-property-pass-through)):

```xml
<onclick>RunScript(script.skinshortcuts,type=skinstring,prop=widgetContext,value=spotlight,skinPath=home.widget.path,skinLabel=home.widget.label,skinType=home.widget.type,skinTarget=home.widget.target)</onclick>
```

The script sets `widgetContext=spotlight` on Home for the picker's lifetime and clears it on close, so the matching flat group's widgets show and the property doesn't leak.

`label` and `icon` are unused when `flat="true"` and may be omitted.

---

## Dynamic Content

Add dynamic content from system sources:

```xml
<content source="playlists" target="videos" />
<content source="addons" target="videos" folder="Video Add-ons" />
<content source="addons" target="music" folder="Music Add-ons" />
<content source="addons" target="pictures" folder="Picture Add-ons" />
<content source="addons" target="executable" folder="Program Add-ons" />
<content source="addons" target="games" folder="Game Add-ons" />
```

| Attribute | Description |
|-----------|-------------|
| `source` | Content type: `playlists`, `addons`, `sources`, `favourites`, `pvr`, `commands`, `settings`, `library`, `nodes` |
| `target` | Media context: `videos`, `music`, `pictures`, `programs`, `tv`, `radio` |
| `folder` | Wrap items in a folder with this label |
| `path` | Custom path override |
| `condition` | Property condition (evaluated against item properties) |
| `visible` | Kodi visibility condition (evaluated at runtime) |
| `icon` | Icon override |
| `label` | Label override |

For `source="addons"`, an add-on resolves as browsable when it is a plugin add-on (it exposes a `plugin://` path) and as a single-click launcher when it is a script. This is decided per add-on, not per target: a program add-on like AutoWidget is browsable under `target="executable"`, while a plain script launcher there is not. See the [Content Target Reference](menus.md#content-target-reference) for every source's valid targets.

### Nodes Source

The `nodes` source provides access to library navigation nodes. The picker shows the top-level categories (Movies, TV Shows, Music Videos, etc.) and lets the user drill into any sub-node:

```xml
<content source="nodes" target="videos" />
<content source="nodes" target="music" />
<content source="nodes" target="library" />
```

#### Nodes Target Values

| Target | Description |
|--------|-------------|
| `videos` | Video library nodes (Movies, TV Shows, Music Videos, etc.) |
| `music` | Music library nodes (Artists, Albums, Songs, etc.) |
| `library` | Two browsable entries (Videos and Music) at the top; user drills into either |

---

### Library Source

The `library` source provides access to library database content (genres, years, actors, etc.):

```xml
<content source="library" target="moviegenres" />
<content source="library" target="tvgenres" />
<content source="library" target="musicgenres" />
<content source="library" target="years" />
<content source="library" target="studios" />
<content source="library" target="actors" />
<content source="library" target="directors" />
<content source="library" target="artists" />
<content source="library" target="albums" />
```

#### Library Target Values

| Target | Description |
|--------|-------------|
| `genres`, `moviegenres` | Movie genres |
| `tvgenres` | TV show genres |
| `musicgenres` | Music genres |
| `years`, `movieyears` | Movie years |
| `tvyears` | TV show years |
| `studios`, `moviestudios` | Movie studios |
| `tvstudios` | TV show studios |
| `tags`, `movietags` | Movie tags |
| `tvtags` | TV show tags |
| `actors`, `movieactors` | Movie actors |
| `tvactors` | TV show actors |
| `directors`, `moviedirectors` | Movie directors |
| `tvdirectors` | TV show directors |
| `artists` | Music artists |
| `albums` | Music albums |

---

## Conditions

### Property Conditions

Evaluated against current item properties:

```xml
<widget name="movie-widget" label="Movies" condition="widgetType=movies">
  ...
</widget>
```

See [Conditions](conditions.md) for syntax.

### Kodi Visibility Conditions

Evaluated at runtime using `xbmc.getCondVisibility()`:

```xml
<widget name="tmdb-widget" label="TMDb Movies" visible="System.AddonIsEnabled(plugin.video.themoviedb.helper)">
  ...
</widget>

<group name="library" label="Library" visible="Library.HasContent(movies)">
  ...
</group>
```

### Multiple Conditions

```xml
<widget name="advanced" label="Advanced Widget" condition="widgetType=movies" visible="Skin.HasSetting(ShowAdvancedWidgets)">
  ...
</widget>
```

Both conditions must pass for the widget to appear.

---

## Output Properties

When a widget is assigned to a menu item, these core properties are set:

| Property | Description |
|----------|-------------|
| `widget` | Widget name |
| `widgetLabel` | Display label |
| `widgetPath` | Content path |
| `widgetTarget` | Target window |
| `widgetType` | Content type (e.g., `movies`, `episodes`, `albums`) |
| `widgetSource` | Source type (e.g., `library`, `playlist`, `addon`) |
| `widgetLimit` | Maximum item count (from `<limit>`) |
| `widgetSortBy` | Sort field (from `<sortby>`) |
| `widgetSortOrder` | Sort direction (from `<sortorder>`) |

`widgetLimit`, `widgetSortBy`, and `widgetSortOrder` are set only when adding a widget in a `type="widgets"` menu, where the widget's `<limit>`/`<sortby>`/`<sortorder>` are carried onto the item.

Additional skin-specific properties can be configured via [properties.xml](properties.md).

Access via `ListItem.Property(name)`:

```xml
<control type="list" id="3000">
  <content target="$INFO[Container(9000).ListItem.Property(widgetTarget)]">
    $INFO[Container(9000).ListItem.Property(widgetPath)]
  </content>
  <visible>!String.IsEmpty(Container(9000).ListItem.Property(widgetPath))</visible>
</control>
```

> **See also:** [Built-in Properties](builtin-properties.md) for complete property reference

---

## Multiple Widgets

For multiple widget slots per menu item, use property suffixes:

| Slot | Properties |
|------|------------|
| Widget 1 | `widget`, `widgetPath`, `widgetType`, `widgetTarget`, `widgetLabel`, `widgetSource` |
| Widget 2 | `widget.2`, `widgetPath.2`, `widgetType.2`, `widgetTarget.2`, `widgetLabel.2`, `widgetSource.2` |
| Widget 3 | `widget.3`, `widgetPath.3`, ... |

Configure via [subdialogs](menus.md#subdialogs) in `menus.xml`:

```xml
<dialogs>
  <subdialog buttonID="800" mode="widget1" setfocus="309" />
  <subdialog buttonID="801" mode="widget2" setfocus="309" suffix=".2" />
</dialogs>
```

Display additional widgets:

```xml
<!-- Widget 2 -->
<control type="list" id="3001">
  <content target="$INFO[Container(9000).ListItem.Property(widgetTarget.2)]">
    $INFO[Container(9000).ListItem.Property(widgetPath.2)]
  </content>
  <visible>!String.IsEmpty(Container(9000).ListItem.Property(widgetPath.2))</visible>
</control>
```

---

## Widget Menus

A menu with `type="widgets"` puts the management dialog into widget mode. In this mode, adding an item opens the widget picker instead of the shortcut picker, and the item's label and icon are set from the selected widget.

This works on both `<menu>` and `<submenu>` elements.

### Standalone Widget Menu

A top-level widget menu managed independently of any other menu:

```xml
<!-- menus.xml -->
<menu name="globalwidgets" type="widgets">
  <allow widgets="true" />
  <item name="gw-recent-movies">
    <label>Recently Added Movies</label>
    <icon>DefaultRecentlyAddedMovies.png</icon>
    <property name="widgetPath">videodb://recentlyaddedmovies/</property>
    <property name="widgetType">movies</property>
    <property name="widgetTarget">videos</property>
  </item>
</menu>
```

Open it directly:

```xml
<onclick>RunScript(script.skinshortcuts,type=manage&amp;menu=globalwidgets)</onclick>
```

The generated include `skinshortcuts-globalwidgets` contains each item with its widget properties.

### Per-Item Widget Submenu

A widget submenu tied to a parent menu item via the subdialog system:

```xml
<!-- menus.xml -->
<submenu name="movies.widgets" type="widgets">
  <item name="movies-recent">
    <label>Recently Added</label>
    <property name="widgetPath">videodb://recentlyaddedmovies/</property>
    <property name="widgetType">movies</property>
    <property name="widgetTarget">videos</property>
  </item>
</submenu>

<dialogs>
  <subdialog buttonID="406" mode="widgets" setfocus="309">
    <onclose action="menu" menu="{item}.widgets" />
  </subdialog>
</dialogs>
```

Use with [items templates](templates.md#dynamic-widgets-pattern) to iterate over the widget items and generate controls per widget.

The parent menu item also carries `submenuPath` — the first widget path of this submenu — so the item can drive visibility or detect "no widgets" directly, without a hidden counter container. To also emit the full numbered list, set `submenuPath="all"` on the parent `<menu>` (or globally with a `<submenuPath>all</submenuPath>` element under `<menus>` for every menu):

```xml
<menu name="mainmenu" submenuPath="all">
```

It goes on the menu, not the submenu, so it also covers submenus a user builds at runtime, which have no `<submenu>` element to annotate.

See [Submenu Widget Path](builtin-properties.md#submenu-widget-path) for the property details.

### Dialog Behavior

In widget mode (`type="widgets"`):

- **Add** opens the widget picker (from `widgets.xml`) instead of the shortcut picker
- **Item label and icon** are set from the selected widget
- The window property `skinshortcuts-menutype` is set to `widgets`

> **See also:** [Widget Picker Button](#widget-picker-button) for adding a widget picker to individual items, [Dynamic Widgets Pattern](templates.md#dynamic-widgets-pattern) for template iteration

---

## Widget Picker Button

To add a widget picker button to the management dialog, define a `type="widget"` property in `properties.xml` and map it to a button ID.

### Setup

In `properties.xml`, add a property and button mapping:

```xml
<properties>
  <property name="widget" type="widget" />

  <buttons>
    <button id="309" property="widget" />
  </buttons>
</properties>
```

In your management dialog XML, add a button with the matching ID:

```xml
<control type="button" id="309">
  <label>Choose Widget</label>
  <visible>String.IsEmpty(Window.Property(disableWidgets))</visible>
</control>
```

When clicked, this opens the widget picker populated from `widgets.xml`. The selected widget auto-populates these properties on the menu item:

| Property | Value |
|----------|-------|
| `widget` | Widget name |
| `widgetLabel` | Display label |
| `widgetPath` | Content path |
| `widgetType` | Content type |
| `widgetTarget` | Target window |
| `widgetSource` | Source type |

Selecting "None" clears all widget properties.

### Multiple Widget Slots

For additional widget slots, use [subdialogs](menus.md#subdialogs) with a suffix:

```xml
<!-- properties.xml -->
<buttons suffix="true">
  <button id="309" property="widget" />
</buttons>
```

```xml
<!-- menus.xml -->
<dialogs>
  <subdialog buttonID="800" mode="widget1" setfocus="309" />
  <subdialog buttonID="801" mode="widget2" setfocus="309" suffix=".2" />
</dialogs>
```

The suffix transforms property names automatically: `widget` becomes `widget.2`, `widgetPath` becomes `widgetPath.2`, etc.

> **See also:** [Properties](properties.md#button-mappings) for button mapping options, [Suffix Transforms](properties.md#suffix-transforms) for how suffixes work, [Multiple Widgets](#multiple-widgets) for display setup

---

## Standalone Widget Picker

The widget picker can be used outside the management dialog to store a selected widget directly in Kodi skin strings. This is useful for standalone screens (e.g., hub windows) where widgets aren't tied to menu items.

### RunScript Call

```xml
<onclick>RunScript(script.skinshortcuts,type=skinstring&amp;skinPath=MyWidgetPath&amp;skinLabel=MyWidgetLabel&amp;skinType=MyWidgetType&amp;skinTarget=MyWidgetTarget)</onclick>
```

This opens the same widget picker used by the management dialog, driven by the skin's `widgets.xml`.

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `type=skinstring` | Yes | Opens the standalone widget picker |
| `path` | No | Custom shortcuts path (defaults to skin's shortcuts folder) |
| `skinPath` | No | Skin string name to store widget path |
| `skinLabel` | No | Skin string name to store widget label |
| `skinType` | No | Skin string name to store widget type |
| `skinTarget` | No | Skin string name to store widget target |

### Behavior

- **Select widget:** Sets each provided skin string via `Skin.SetString()`
- **Select "None":** Clears all provided skin strings via `Skin.Reset()`
- **Cancel:** No changes

The "None" option is always shown at the top of the picker.

### Skin XML Usage

```xml
<!-- Button to pick a widget -->
<control type="button">
  <label>Choose Widget</label>
  <onclick>RunScript(script.skinshortcuts,type=skinstring&amp;skinPath=HubWidget1.Path&amp;skinLabel=HubWidget1.Label&amp;skinType=HubWidget1.Type&amp;skinTarget=HubWidget1.Target)</onclick>
</control>

<!-- Display the selected widget -->
<control type="list" id="5000">
  <content target="$INFO[Skin.String(HubWidget1.Target)]">$INFO[Skin.String(HubWidget1.Path)]</content>
  <visible>!String.IsEmpty(Skin.String(HubWidget1.Path))</visible>
</control>

<!-- Show selected widget name -->
<control type="label">
  <label>$INFO[Skin.String(HubWidget1.Label)]</label>
</control>
```

---

[↑ Top](#widget-configuration) · [Skinning Docs](index.md)
