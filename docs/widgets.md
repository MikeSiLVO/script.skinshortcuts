# Widgets

## Table of Contents

- [Structure](#structure)
- [Widget Element](#widget-element)
- [Content Types](#content-types)
- [Conditions](#conditions)
- [Groups](#groups)
- [Returned Properties](#returned-properties)

## Structure

`shortcuts/widgets.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<widgets>
  <widget name="recent-movies" label="$LOCALIZE[20386]" type="movies">
    <path>videodb://recentlyaddedmovies/</path>
    <target>videos</target>
    <icon>DefaultRecentlyAddedMovies.png</icon>
    <condition>Library.HasContent(movies)</condition>
  </widget>
</widgets>
```

## Widget Element

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique widget identifier |
| `label` | Yes | Display name |
| `type` | No | Content type hint |

| Element | Required | Description |
|---------|----------|-------------|
| `<path>` | Yes | Content source path |
| `<target>` | Yes | Target window |
| `<icon>` | No | Icon for picker |
| `<condition>` | No | Visibility condition |

### Path Types

```xml
<path>videodb://recentlyaddedmovies/</path>                    <!-- Library -->
<path>special://skin/playlists/movies.xsp</path>               <!-- Playlist -->
<path>plugin://plugin.video.example/?action=list</path>        <!-- Add-on -->
<path>library://video/movies/inprogress.xml/</path>            <!-- Library node -->
```

### Targets

| Target | Content |
|--------|---------|
| `videos` | Movies, TV, music videos |
| `music` | Albums, artists, songs |
| `programs` | Add-ons, scripts |
| `pictures` | Photos |
| `games` | Games |
| `pvr` | Live TV, recordings |

## Content Types

Video: `movies`, `tvshows`, `episodes`, `musicvideos`, `sets`

Music: `albums`, `artists`, `songs`

Other: `pictures`, `pvr`, `games`, `addons`, `custom`

## Conditions

```xml
<condition>Library.HasContent(movies)</condition>
<condition>Library.HasContent(tvshows)</condition>
<condition>System.AddonIsEnabled(plugin.video.example)</condition>
<condition>Skin.HasSetting(ShowAdvancedWidgets)</condition>
```

Multiple conditions (AND logic):

```xml
<widget name="tmdb-movies" label="TMDb Movies" type="movies">
  <path>plugin://plugin.video.themoviedb.helper/?info=trending</path>
  <target>videos</target>
  <condition>System.AddonIsEnabled(plugin.video.themoviedb.helper)</condition>
  <condition>Skin.HasSetting(ShowTMDbWidgets)</condition>
</widget>
```

## Groups

```xml
<widgets>
  <group name="library" label="Library">
    <widget name="recent-movies" label="Recently Added" type="movies">
      <path>videodb://recentlyaddedmovies/</path>
      <target>videos</target>
    </widget>
  </group>

  <group name="addons" label="Add-ons">
    <condition>System.AddonIsEnabled(plugin.video.themoviedb.helper)</condition>
    <widget name="tmdb-trending" label="Trending" type="movies">
      <path>plugin://plugin.video.themoviedb.helper/?info=trending</path>
      <target>videos</target>
    </widget>
  </group>
</widgets>
```

## Returned Properties

| Property | Description |
|----------|-------------|
| `widget` | Widget ID |
| `widgetPath` | Content path |
| `widgetType` | Content type |
| `widgetTarget` | Target window |
| `widgetName` | Display label |

Multiple widgets use suffixes: `widget.2`, `widgetPath.2`, etc.

Usage:

```xml
<control type="list" id="3000">
  <content target="$INFO[Container(9000).ListItem.Property(widgetTarget)]">
    $INFO[Container(9000).ListItem.Property(widgetPath)]
  </content>
</control>
```
