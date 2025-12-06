# Backgrounds

## Table of Contents

- [Structure](#structure)
- [Background Element](#background-element)
- [Types](#types)
- [Playlist Sources](#playlist-sources)
- [Conditions](#conditions)
- [Returned Properties](#returned-properties)

## Structure

`shortcuts/backgrounds.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
  <background name="movie-fanart" label="Movie Fanart" type="property">
    <path>$INFO[Container(9035).ListItem.Art(fanart)]</path>
    <icon>DefaultMovies.png</icon>
    <condition>Library.HasContent(movies)</condition>
  </background>
</backgrounds>
```

## Background Element

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique identifier |
| `label` | Yes | Display name |
| `type` | Yes | Background type |

| Element | Required | Description |
|---------|----------|-------------|
| `<path>` | Varies | Image path or info label |
| `<icon>` | No | Icon for picker |
| `<condition>` | No | Visibility condition |
| `<source>` | No | Playlist sources |

## Types

### static

Single image file:

```xml
<background name="default-bg" label="Default" type="static">
  <path>special://skin/backgrounds/default.jpg</path>
</background>
```

### property

Kodi info label:

```xml
<background name="movie-fanart" label="Movie Fanart" type="property">
  <path>$INFO[Container(9035).ListItem.Art(fanart)]</path>
</background>

<background name="slideshow" label="Movie Slideshow" type="property">
  <path>$INFO[Window(Home).Property(SkinInfo.Slideshow.Movie.FanArt)]</path>
</background>
```

### browse

User picks single image:

```xml
<background name="custom-image" label="Custom Image" type="browse">
  <icon>DefaultPicture.png</icon>
</background>
```

### multi

User picks folder:

```xml
<background name="custom-folder" label="Custom Folder" type="multi">
  <icon>DefaultFolder.png</icon>
</background>
```

### playlist

User picks from playlist sources:

```xml
<background name="playlist" label="Playlist" type="playlist">
  <icon>DefaultPlaylist.png</icon>
  <source label="Video Playlists">special://videoplaylists/</source>
  <source label="Music Playlists">special://musicplaylists/</source>
</background>
```

### live

Dynamic content:

```xml
<background name="live-random-movies" label="Random Movies" type="live">
  <path>random movies</path>
  <condition>Library.HasContent(movies)</condition>
</background>
```

### live-playlist

User picks playlist for live content:

```xml
<background name="live-playlist" label="Live Playlist" type="live-playlist">
  <source label="Video Playlists">special://videoplaylists/</source>
</background>
```

## Playlist Sources

```xml
<source label="Video Playlists" icon="DefaultVideoPlaylists.png">special://videoplaylists/</source>
<source label="Music Playlists" icon="DefaultMusicPlaylists.png">special://musicplaylists/</source>
<source label="Skin Playlists">special://skin/playlists/</source>
```

| Attribute | Required | Description |
|-----------|----------|-------------|
| `label` | Yes | Display name |
| `icon` | No | Icon for picker |

## Conditions

```xml
<condition>Library.HasContent(movies)</condition>
<condition>!String.IsEmpty(Skin.String(weatherfanart.path))</condition>
```

## Returned Properties

| Property | Description |
|----------|-------------|
| `background` | Background ID |
| `backgroundPath` | Resolved image path |
| `backgroundName` | Display label |

Usage:

```xml
<control type="image">
  <texture background="true">$INFO[Container(9000).ListItem.Property(backgroundPath)]</texture>
</control>
```
