# Widget Configuration

The `widgets.xml` file defines widgets that users can assign to menu items.

***

## Table of Contents

* [File Structure](#file-structure)
* [Widget Element](#widget-element)
* [Widget Types](#widget-types)
* [Groups](#groups)
* [Dynamic Content](#dynamic-content)
* [Conditions](#conditions)
* [Output Properties](#output-properties)
* [Multiple Widgets](#multiple-widgets)

***

## File Structure

Widgets and groups are defined directly at the root level:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<widgets showGetMore="true">
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

***

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
| `slot` | No | - | For `type="custom"`: widget property slot |

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

***

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

### Custom Widgets

Custom widgets let users define their own item list:

```xml
<widget name="custom-items" label="Custom Widget" type="custom" slot="widget">
  <!-- No path required - items are user-defined -->
</widget>
```

When selected, the dialog opens an item editor for the custom menu.

***

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
</widgets>
```

### `<group>` Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier |
| `label` | Yes | Display label |
| `icon` | No | Icon for picker display (default: `DefaultFolder.png`) |
| `condition` | No | Property condition (evaluated against item properties) |
| `visible` | No | Kodi visibility condition (evaluated at runtime) |

Groups can contain:

* `<widget>` - Widget definitions
* `<group>` - Nested groups
* `<content>` - Dynamic content

***

## Dynamic Content

Add dynamic content from system sources:

```xml
<content source="playlists" target="videos" />
<content source="addons" target="videos" folder="Video Add-ons" />
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

### Nodes Source

The `nodes` source provides access to library navigation nodes (the top-level library categories like Movies, TV Shows, Music Videos, etc.):

```xml
<content source="nodes" target="videos" />
<content source="nodes" target="music" />
```

#### Nodes Target Values

| Target | Description |
|--------|-------------|
| `videos` | Video library nodes (Movies, TV Shows, Music Videos, etc.) |
| `music` | Music library nodes (Artists, Albums, Songs, etc.) |

***

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

***

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

***

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

***

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

***

## Quick Navigation

[Back to Top](#widget-configuration)

**Sections:** [File Structure](#file-structure) | [Widget Element](#widget-element) | [Widget Types](#widget-types) | [Groups](#groups) | [Dynamic Content](#dynamic-content) | [Conditions](#conditions) | [Output Properties](#output-properties) | [Multiple Widgets](#multiple-widgets)

**Related Docs:** [Menus](menus.md) | [Backgrounds](backgrounds.md) | [Properties](properties.md) | [Templates](templates.md) | [Conditions](conditions.md)
