# Starter Configuration

Copy/paste groupings for a skin starting from nothing. The script has no built-in shortcut list, so the picker shows only what the skin defines.

Labels use Kodi core string IDs and icons use Kodi's `Default*.png` set, so nothing here needs skin strings or textures. Group labels with no core string equivalent are plain text.

---

## Table of Contents

* [Shortcut Groupings](#shortcut-groupings)
* [Widget Groups](#widget-groups)
* [Trimming It Down](#trimming-it-down)

---

## Shortcut Groupings

Goes inside `<menus>` in `shortcuts/menus.xml`. The `<shortcut>` elements are fixed entries the skin owns; the `<content>` elements resolve against the running system, so they follow whatever the user has installed, scanned or set up.

```xml
<groupings>
  <group name="common" label="Common" icon="DefaultFolder.png">
    <shortcut name="videos" label="$LOCALIZE[3]" icon="DefaultVideo.png">
      <action>ActivateWindow(Videos,library://video/,return)</action>
    </shortcut>
    <shortcut name="movies" label="$LOCALIZE[342]" icon="DefaultMovies.png" visible="Library.HasContent(movies)">
      <action>ActivateWindow(Videos,videodb://movies/titles/,return)</action>
    </shortcut>
    <shortcut name="tvshows" label="$LOCALIZE[20343]" icon="DefaultTVShows.png" visible="Library.HasContent(tvshows)">
      <action>ActivateWindow(Videos,videodb://tvshows/titles/,return)</action>
    </shortcut>
    <shortcut name="musicvideos" label="$LOCALIZE[20389]" icon="DefaultMusicVideos.png" visible="Library.HasContent(musicvideos)">
      <action>ActivateWindow(Videos,videodb://musicvideos/titles/,return)</action>
    </shortcut>
    <shortcut name="music" label="$LOCALIZE[2]" icon="DefaultMusicAlbums.png">
      <action>ActivateWindow(Music,library://music/,return)</action>
    </shortcut>
    <shortcut name="pictures" label="$LOCALIZE[1]" icon="DefaultPicture.png">
      <action>ActivateWindow(Pictures)</action>
    </shortcut>
    <shortcut name="programs" label="$LOCALIZE[10001]" icon="DefaultAddonProgram.png">
      <action>ActivateWindow(Programs,Addons,return)</action>
    </shortcut>
    <shortcut name="games" label="$LOCALIZE[10821]" icon="DefaultAddonGame.png">
      <action>ActivateWindow(Games)</action>
    </shortcut>
    <shortcut name="weather" label="$LOCALIZE[12600]" icon="DefaultAddonWeather.png">
      <action>ActivateWindow(Weather)</action>
    </shortcut>
    <shortcut name="favourites" label="$LOCALIZE[1036]" icon="DefaultFavourites.png">
      <action>ActivateWindow(FavouritesBrowser)</action>
    </shortcut>
    <shortcut name="filemanager" label="$LOCALIZE[7]" icon="DefaultFolder.png">
      <action>ActivateWindow(FileManager)</action>
    </shortcut>
    <shortcut name="settings" label="$LOCALIZE[5]" icon="DefaultAddonService.png">
      <action>ActivateWindow(Settings)</action>
    </shortcut>
  </group>

  <group name="tv" label="$LOCALIZE[19020]" icon="DefaultPVRChannels.png" visible="PVR.HasTVChannels">
    <shortcut name="tv-guide" label="$LOCALIZE[19069]" icon="DefaultPVRGuide.png">
      <action>ActivateWindow(TVGuide)</action>
    </shortcut>
    <shortcut name="tv-channels" label="$LOCALIZE[19023]" icon="DefaultPVRChannels.png">
      <action>ActivateWindow(TVChannels)</action>
    </shortcut>
    <shortcut name="tv-recordings" label="$LOCALIZE[19163]" icon="DefaultPVRRecordings.png">
      <action>ActivateWindow(TVRecordings)</action>
    </shortcut>
    <content source="pvr" target="tv" folder="$LOCALIZE[19023]" />
  </group>

  <group name="radio" label="$LOCALIZE[19021]" icon="DefaultPVRChannels.png" visible="PVR.HasRadioChannels">
    <shortcut name="radio-guide" label="$LOCALIZE[19069]" icon="DefaultPVRGuide.png">
      <action>ActivateWindow(RadioGuide)</action>
    </shortcut>
    <shortcut name="radio-channels" label="$LOCALIZE[19024]" icon="DefaultPVRChannels.png">
      <action>ActivateWindow(RadioChannels)</action>
    </shortcut>
    <content source="pvr" target="radio" folder="$LOCALIZE[19024]" />
  </group>

  <group name="library" label="$LOCALIZE[14022]" icon="DefaultVideo.png">
    <content source="nodes" target="video" folder="$LOCALIZE[14236]" />
    <content source="nodes" target="music" folder="$LOCALIZE[14237]" />
  </group>

  <group name="playlists" label="$LOCALIZE[136]" icon="DefaultPlaylist.png">
    <content source="playlists" target="video" folder="$LOCALIZE[14236]" />
    <content source="playlists" target="music" folder="$LOCALIZE[14237]" />
  </group>

  <group name="addons" label="$LOCALIZE[24001]" icon="DefaultAddon.png">
    <group name="addons-video" label="$LOCALIZE[1037]" icon="DefaultAddonVideo.png">
      <content source="addons" target="video" label="$LOCALIZE[1037]" />
    </group>
    <group name="addons-music" label="$LOCALIZE[1038]" icon="DefaultAddonMusic.png">
      <content source="addons" target="music" label="$LOCALIZE[1038]" />
    </group>
    <group name="addons-pictures" label="$LOCALIZE[1039]" icon="DefaultAddonPicture.png">
      <content source="addons" target="pictures" label="$LOCALIZE[1039]" />
    </group>
    <group name="addons-programs" label="$LOCALIZE[10001]" icon="DefaultAddonProgram.png">
      <content source="addons" target="programs" label="$LOCALIZE[10001]" />
    </group>
  </group>

  <group name="sources" label="$LOCALIZE[20094]" icon="DefaultFolder.png">
    <content source="sources" target="video" folder="$LOCALIZE[3]" />
    <content source="sources" target="music" folder="$LOCALIZE[2]" />
    <content source="sources" target="pictures" folder="$LOCALIZE[1]" />
  </group>

  <group name="favourites" label="$LOCALIZE[1036]" icon="DefaultFavourites.png">
    <content source="favourites" />
  </group>

  <group name="settings" label="$LOCALIZE[5]" icon="DefaultAddonService.png">
    <content source="settings" />
  </group>

  <group name="power" label="$LOCALIZE[33060]" icon="DefaultAddonNone.png">
    <content source="commands" />
  </group>
</groupings>
```

> **See also:** [Shortcut Groupings](menus.md#shortcut-groupings) for every attribute, and [Content Target Reference](menus.md#content-target-reference) for each source's valid targets

---

## Widget Groups

A whole `shortcuts/widgets.xml`. Library paths are Kodi's own nodes, so they work without a skin playlist.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<widgets>
  <group name="movies" label="$LOCALIZE[20342]" icon="DefaultMovies.png" visible="Library.HasContent(movies)">
    <widget name="recent-movies" label="$LOCALIZE[20386]" type="movies" target="videos" icon="DefaultRecentlyAddedMovies.png">
      <path>videodb://recentlyaddedmovies/</path>
      <limit>25</limit>
    </widget>
    <widget name="all-movies" label="$LOCALIZE[342]" type="movies" target="videos" icon="DefaultMovies.png">
      <path>videodb://movies/titles/</path>
      <sortby>random</sortby>
      <limit>25</limit>
    </widget>
    <group name="movie-genres" label="$LOCALIZE[135]" icon="DefaultGenre.png">
      <content source="library" target="moviegenres" />
    </group>
  </group>

  <group name="tvshows" label="$LOCALIZE[20343]" icon="DefaultTVShows.png" visible="Library.HasContent(tvshows)">
    <widget name="recent-episodes" label="$LOCALIZE[20387]" type="episodes" target="videos" icon="DefaultRecentlyAddedEpisodes.png">
      <path>videodb://recentlyaddedepisodes/</path>
      <limit>25</limit>
    </widget>
    <widget name="inprogress-tvshows" label="$LOCALIZE[626]" type="tvshows" target="videos" icon="DefaultTVShows.png">
      <path>videodb://inprogresstvshows/</path>
      <limit>25</limit>
    </widget>
    <group name="tvshow-genres" label="$LOCALIZE[135]" icon="DefaultGenre.png">
      <content source="library" target="tvgenres" />
    </group>
  </group>

  <group name="music" label="$LOCALIZE[2]" icon="DefaultMusicAlbums.png" visible="Library.HasContent(music)">
    <widget name="recent-albums" label="$LOCALIZE[359]" type="albums" target="music" icon="DefaultMusicRecentlyAdded.png">
      <path>musicdb://recentlyaddedalbums/</path>
      <limit>25</limit>
    </widget>
    <widget name="played-albums" label="$LOCALIZE[517]" type="albums" target="music" icon="DefaultMusicRecentlyPlayed.png">
      <path>musicdb://recentlyplayedalbums/</path>
      <limit>25</limit>
    </widget>
    <group name="music-genres" label="$LOCALIZE[135]" icon="DefaultMusicGenres.png">
      <content source="library" target="musicgenres" />
    </group>
  </group>

  <widget name="favourites" label="$LOCALIZE[1036]" type="videos" target="videos" icon="DefaultFavourites.png">
    <path>favourites://</path>
  </widget>

  <content source="playlists" target="video" folder="$LOCALIZE[136]" />
  <content source="addons" target="video" folder="$LOCALIZE[1037]" />
</widgets>
```

> **See also:** [Widget Configuration](widgets.md) for widget attributes, types and picker behaviour

---

## Trimming It Down

* A `<group>` costs the user a keypress. Drop the ones the skin will not use rather than shipping every source.
* `visible` on a group hides it when its content cannot exist (`PVR.HasTVChannels`, `Library.HasContent(movies)`), which keeps the picker short on a fresh install.
* `flat="true"` on a group drops the folder level and lists its children inline. Useful for a small group that does not deserve its own folder.
* Fixed `<shortcut>` entries are the skin's to maintain. Kodi window names and paths change between versions, so check them when bumping the skin's target version.

> **See also:** [Menu Configuration](menus.md), [Widget Configuration](widgets.md), [Getting Started](getting-started.md)
