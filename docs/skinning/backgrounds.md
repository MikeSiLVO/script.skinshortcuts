# Background Configuration

The `backgrounds.xml` file defines background options that users can assign to menu items.

***

## Table of Contents

* [File Structure](#file-structure)
* [Background Types](#background-types)
* [Groups](#groups)
* [Static](#static)
* [Property](#property)
* [Browse](#browse)
* [Multi](#multi)
* [Playlist](#playlist)
* [Live](#live)
* [Live Playlist](#live-playlist)
* [Sources](#sources)
* [Conditions](#conditions)
* [Output Properties](#output-properties)

***

## File Structure

Backgrounds and groups are defined directly at the root level:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
  <!-- Flat background (appears ungrouped in picker) -->
  <background name="custom-image" label="Custom Image" type="browse">
    <icon>DefaultPicture.png</icon>
    <source label="Browse...">browse</source>
  </background>

  <!-- Group of backgrounds (creates nested navigation in picker) -->
  <group name="library-fanart" label="Library Fanart" visible="Library.HasContent(movies)">
    <background name="movie-fanart" label="Movie Fanart" type="property">
      <path>$INFO[Window(Home).Property(MovieFanart)]</path>
    </background>
  </group>
</backgrounds>
```

***

## Background Types

| Type | Description |
|------|-------------|
| `static` | Single image file |
| `property` | Kodi info label that resolves to an image |
| `browse` | User browses for a single image |
| `multi` | User browses for a folder (slideshow) |
| `playlist` | User selects a playlist for images |
| `live` | Dynamic content from library |
| `live-playlist` | Dynamic content from user-selected playlist |

***

## Groups

Organize backgrounds into categories for the picker dialog:

```xml
<backgrounds>
  <!-- Group creates nested navigation -->
  <group name="library" label="Library Fanart" icon="DefaultVideo.png" visible="Library.HasContent(movies)">
    <background name="movie-fanart" label="Movie Fanart" type="property">
      <path>$INFO[Window(Home).Property(MovieFanart)]</path>
    </background>

    <background name="tv-fanart" label="TV Show Fanart" type="property" visible="Library.HasContent(tvshows)">
      <path>$INFO[Window(Home).Property(TVFanart)]</path>
    </background>

    <!-- Nested group -->
    <group name="live-fanart" label="Live Backgrounds">
      <background name="random-movies" label="Random Movies" type="live">
        <path>random movies</path>
      </background>
    </group>
  </group>

  <!-- Flat background (no group) -->
  <background name="custom-image" label="Custom Image" type="browse">
    <icon>DefaultPicture.png</icon>
    <source label="Browse...">browse</source>
  </background>
</backgrounds>
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

* `<background>` - Background definitions
* `<group>` - Nested groups
* `<content>` - Dynamic content (same as widgets/menus)

***

## Static

A single image file:

```xml
<background name="default" label="Default Background" type="static">
  <path>special://skin/backgrounds/default.jpg</path>
  <icon>DefaultPicture.png</icon>
</background>
```

### Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier |
| `label` | Yes | Display label |
| `type` | Yes | `static` |
| `condition` | No | Property condition (evaluated against item properties) |
| `visible` | No | Kodi visibility condition (evaluated at runtime) |

### Child Elements

| Element | Required | Description |
|---------|----------|-------------|
| `<path>` | Yes | Image file path |
| `<icon>` | No | Icon for picker |

***

## Property

Uses a Kodi info label that resolves to an image path:

```xml
<background name="current-fanart" label="Current Item Fanart" type="property">
  <path>$INFO[Container(9000).ListItem.Art(fanart)]</path>
  <icon>DefaultPicture.png</icon>
</background>

<background name="slideshow" label="Random Movie Slideshow" type="property" visible="System.AddonIsEnabled(script.skin.info.service) + Library.HasContent(movies)">
  <path>$INFO[Window(Home).Property(SkinHelper.Slideshow.Movie.FanArt)]</path>
  <icon>DefaultMovies.png</icon>
</background>
```

### Child Elements

| Element | Required | Description |
|---------|----------|-------------|
| `<path>` | Yes | Kodi info label |
| `<icon>` | No | Icon for picker |

***

## Browse

User browses for a single image file:

```xml
<background name="custom-image" label="Custom Image" type="browse">
  <icon>DefaultPicture.png</icon>
  <source label="Skin Backgrounds">special://skin/backgrounds/</source>
  <source label="Browse...">browse</source>
</background>
```

### Sources

Provide starting locations for the file browser:

```xml
<source label="Skin Backgrounds" icon="DefaultFolder.png" visible="Skin.HasSetting(UseHDBackgrounds)">
  special://skin/backgrounds/hd/
</source>
<source label="Browse...">browse</source>
```

| Attribute | Description |
|-----------|-------------|
| `label` | Display label in source picker |
| `icon` | Icon for this source |
| `condition` | Property condition (evaluated against item properties) |
| `visible` | Kodi visibility condition (evaluated at runtime) |

Use `browse` as the path for free file browser access.

***

## Multi

User browses for a folder (for slideshows):

```xml
<background name="custom-folder" label="Image Folder" type="multi">
  <icon>DefaultFolder.png</icon>
  <source label="My Backgrounds">special://profile/backgrounds/</source>
  <source label="Browse...">browse</source>
</background>
```

Works the same as `browse` type, but selects a folder instead of a single file.

***

## Playlist

User selects a playlist to extract images from:

```xml
<background name="from-playlist" label="Playlist Images" type="playlist">
  <icon>DefaultPlaylist.png</icon>
  <source label="Video Playlists">special://profile/playlists/video/</source>
  <source label="Music Playlists">special://profile/playlists/music/</source>
  <source label="Skin Playlists">special://skin/playlists/</source>
</background>
```

### Playlist Sources

| Attribute | Required | Description |
|-----------|----------|-------------|
| `label` | Yes | Display label |
| `icon` | No | Icon (default: `DefaultPlaylist.png`) |

***

## Live

Dynamic background from library content:

```xml
<background name="random-movies" label="Random Movie Fanart" type="live" visible="Library.HasContent(movies)">
  <path>random movies</path>
  <icon>DefaultMovies.png</icon>
</background>
```

### Live Path Values

| Path | Description |
|------|-------------|
| `random movies` | Random movie fanart |
| `random tvshows` | Random TV show fanart |
| `random music` | Random album art |

***

## Live Playlist

Dynamic content from a user-selected playlist:

```xml
<background name="live-playlist" label="Live Playlist" type="live-playlist">
  <icon>DefaultPlaylist.png</icon>
  <source label="Video Playlists">special://profile/playlists/video/</source>
  <source label="Music Playlists">special://profile/playlists/music/</source>
</background>
```

Combines playlist selection with dynamic content extraction.

***

## Sources

Both `<source>` elements are used differently based on background type:

### For browse/multi types

Sources provide starting locations for the file browser. Can include conditions:

```xml
<source label="HD Backgrounds" visible="Skin.HasSetting(UseHD)">
  special://skin/backgrounds/hd/
</source>
```

| Attribute | Description |
|-----------|-------------|
| `label` | Display label in picker |
| `condition` | Property condition (evaluated against item properties) |
| `visible` | Kodi visibility condition (evaluated at runtime) |
| `icon` | Icon for this source |

### For playlist/live-playlist types

Sources define playlist locations to browse:

```xml
<source label="Video Playlists" icon="DefaultVideoPlaylists.png">
  special://profile/playlists/video/
</source>
```

***

## Conditions

### Property Conditions

Evaluated against current item properties:

```xml
<background name="movie-bg" label="Movies" condition="widgetType=movies">
  ...
</background>
```

See [Conditions](conditions.md) for syntax.

### Kodi Visibility Conditions

Evaluated at runtime using `xbmc.getCondVisibility()`:

```xml
<background name="skin-fanart" label="Skin Fanart" visible="System.AddonIsEnabled(script.skin.info.service)">
  ...
</background>

<group name="library" label="Library" visible="Library.HasContent(movies)">
  ...
</group>
```

### Multiple Conditions

```xml
<background name="advanced" label="Advanced Background" condition="widgetType=movies" visible="Skin.HasSetting(ShowAdvancedBackgrounds)">
  ...
</background>
```

Both conditions must pass for the background to appear.

***

## Output Properties

When a background is assigned to a menu item, these core properties are set:

| Property | Description |
|----------|-------------|
| `background` | Background name |
| `backgroundPath` | Image path |
| `backgroundLabel` | Display label |
| `backgroundType` | Background type (static, property, browse, etc.) |
| `backgroundPlaylistType` | Playlist content type (for playlist/live-playlist types only) |

The `backgroundPlaylistType` property contains the raw content type from the smart playlist (.xsp) file:

| Value | Description |
|-------|-------------|
| `movies` | Movie content |
| `tvshows` | TV show content |
| `episodes` | Episode content (no posters) |
| `musicvideos` | Music video content (no posters) |
| `songs` | Song content |
| `albums` | Album content |
| `artists` | Artist content |
| `mixed` | Mixed content types |

Episodes and musicvideos don't have poster artwork. Skins can use this property to select fallback images.

Additional properties can be configured via [properties.xml](properties.md).

Access via `ListItem.Property(name)`:

```xml
<control type="image">
  <texture background="true">
    $INFO[Container(9000).ListItem.Property(backgroundPath)]
  </texture>
</control>
```

For static/property types, `backgroundPath` contains the defined path. For browse/multi types, it contains the user-selected path. For playlist types, your skin handles the slideshow logic using the path.

***

## Quick Navigation

[Back to Top](#background-configuration)

**Sections:** [File Structure](#file-structure) | [Background Types](#background-types) | [Groups](#groups) | [Static](#static) | [Property](#property) | [Browse](#browse) | [Multi](#multi) | [Playlist](#playlist) | [Live](#live) | [Live Playlist](#live-playlist) | [Sources](#sources) | [Conditions](#conditions) | [Output Properties](#output-properties)

**Related Docs:** [Menus](menus.md) | [Widgets](widgets.md) | [Properties](properties.md) | [Templates](templates.md) | [Conditions](conditions.md)
