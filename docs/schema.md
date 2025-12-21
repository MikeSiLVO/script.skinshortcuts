# Skin Shortcuts v3 Schema Reference

Quick reference for all XML configuration files. For detailed documentation, see the [skinning docs](skinning/).

***

## File Overview

### Input Files (Skin Configuration)

Located in the skin's `shortcuts/` folder:

| File | Purpose |
|------|---------|
| `menus.xml` | Menu structure, items, groupings, icon sources, action overrides |
| `widgets.xml` | Widget definitions and groupings for widget picker |
| `backgrounds.xml` | Background options and groupings for background picker |
| `properties.xml` | Property definitions, options, fallbacks, button mappings |
| `templates.xml` | Template definitions for generating skin includes |

### Output File (Generated)

| File | Location | Purpose |
|------|----------|---------|
| `script-skinshortcuts-includes.xml` | Skin's resolution folder (e.g., `16x9/`) | Generated includes file containing all menu items and properties |

### User Data

| File | Location | Purpose |
|------|----------|---------|
| `{skin_id}.userdata.json` | `userdata/addon_data/script.skinshortcuts/` | User customizations merged with skin defaults at build time |

***

## menus.xml

Defines menu structure, shortcut picker groupings, icon sources, and action overrides.

```xml
<menus>
  <menu name="mainmenu" container="9000">
    <defaults widget="recent-movies" background="movie-fanart">
      <allow widgets="true" backgrounds="true" submenus="true"/>
      <property name="widgetStyle">Panel</property>
    </defaults>
    <item name="movies" submenu="movies" widget="recent-movies" background="movie-fanart">
      <label>$LOCALIZE[20342]</label>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
      <action condition="!Library.HasContent(movies)">ActivateWindow(Videos,files)</action>
      <icon>DefaultMovies.png</icon>
      <visible>Library.HasContent(movies)</visible>
      <property name="widgetStyle">Panel</property>
    </item>
  </menu>

  <submenu name="movies" container="9001">
    <item name="recent">
      <label>Recent</label>
      <action>ActivateWindow(Videos,videodb://recentlyaddedmovies/)</action>
    </item>
  </submenu>

  <groupings>
    <group name="common" label="Common">
      <shortcut name="movies" label="Movies" icon="DefaultMovies.png">
        <action>ActivateWindow(Videos,videodb://movies/)</action>
      </shortcut>
      <shortcut name="playlists" label="Playlists" icon="DefaultPlaylist.png"
                path="special://profile/playlists/video/" browse="video"/>
      <content source="playlists" target="video" folder="Video Playlists"/>
    </group>
  </groupings>

  <icons>
    <source label="Skin Icons">special://skin/extras/icons/</source>
    <source label="Browse...">browse</source>
  </icons>

  <overrides>
    <action replace="ActivateWindow(favourites)">ActivateWindow(favouritesbrowser)</action>
  </overrides>

  <dialogs>
    <subdialog buttonID="800" mode="widget1" setfocus="309"/>
    <subdialog buttonID="801" mode="widget2" setfocus="309" suffix=".2"/>
  </dialogs>

  <contextmenu>true</contextmenu>
</menus>
```

### Element Reference

| Element | Parent | Required Attributes | Optional Attributes | Description |
|---------|--------|---------------------|---------------------|-------------|
| `<menu>` | menus | `name` | `container` | Main menu definition |
| `<submenu>` | menus | `name` | `container` | Submenu definition |
| `<defaults>` | menu/submenu | — | `widget`, `background` | Default settings for items |
| `<allow>` | defaults | — | `widgets`, `backgrounds`, `submenus` | Feature toggles |
| `<item>` | menu/submenu | `name` | `submenu`, `widget`, `background`, `required` | Menu item |
| `<label>` | item | — | — | Display text |
| `<label2>` | item | — | — | Secondary label |
| `<action>` | item/defaults | — | `condition`, `when` | Action to execute |
| `<icon>` | item | — | — | Icon path |
| `<thumb>` | item | — | — | Thumbnail path |
| `<visible>` | item | — | — | Visibility condition |
| `<disabled>` | item | — | — | If "true", item not selectable |
| `<property>` | item/defaults | `name` | — | Custom property |
| `<protect>` | item | — | `type`, `heading`, `message` | Protection rule |
| `<groupings>` | menus | — | — | Shortcut picker structure |
| `<group>` | groupings | `name`, `label` | `condition`, `visible`, `icon` | Shortcut group |
| `<shortcut>` | group | `name`, `label` | `icon`, `condition`, `visible`, `path`, `browse` | Shortcut option |
| `<content>` | group | `source` | `target`, `path`, `condition`, `visible`, `icon`, `label`, `folder` | Dynamic content |
| `<icons>` | menus | — | — | Icon browser sources |
| `<source>` | icons | — | `label`, `condition`, `visible`, `icon` | Icon source path |
| `<overrides>` | menus | — | — | Action overrides |
| `<action>` | overrides | `replace` | — | Replacement action |
| `<dialogs>` | menus | — | — | Subdialog definitions |
| `<subdialog>` | dialogs | `buttonID`, `mode` | `setfocus`, `suffix` | Subdialog mapping |
| `<contextmenu>` | menus | — | — | Enable/disable context menu |

***

## widgets.xml

Defines widgets and widget picker groupings.

```xml
<widgets showGetMore="true">
  <!-- Flat widget at root level -->
  <widget name="favourites" label="Favourites" type="videos" target="videos">
    <path>favourites://</path>
  </widget>

  <!-- Custom widget (no path required) -->
  <widget name="custom" label="Custom" type="custom" slot="widget"/>

  <!-- Group with nested widgets -->
  <group name="movies" label="Movies" icon="DefaultMovies.png" source="library"
         visible="Library.HasContent(movies)">
    <widget name="recent" label="Recent" type="movies" icon="DefaultRecentlyAddedMovies.png">
      <path>videodb://recentlyaddedmovies/</path>
      <limit>25</limit>
      <sortby>dateadded</sortby>
      <sortorder>descending</sortorder>
    </widget>

    <!-- Nested group -->
    <group name="genres" label="By Genre">
      <content source="library" target="moviegenres"/>
    </group>
  </group>
</widgets>
```

### Element Reference

| Element | Parent | Required Attributes | Optional Attributes | Description |
|---------|--------|---------------------|---------------------|-------------|
| `<widgets>` | — | — | `showGetMore` | Root element |
| `<widget>` | widgets/group | `name`, `label` | `type`, `target`, `icon`, `condition`, `visible`, `source`, `slot` | Widget definition |
| `<path>` | widget | — | — | Content path (required except type="custom") |
| `<limit>` | widget | — | — | Item limit |
| `<sortby>` | widget | — | — | Sort field |
| `<sortorder>` | widget | — | — | Sort direction |
| `<group>` | widgets/group | `name`, `label` | `condition`, `visible`, `icon`, `source` | Widget group |
| `<content>` | group | `source` | `target`, `path`, `condition`, `visible`, `icon`, `label`, `folder` | Dynamic content |

### Widget Types

`movies`, `tvshows`, `episodes`, `musicvideos`, `sets`, `albums`, `artists`, `songs`, `pictures`, `pvr`, `games`, `addons`, `custom`

***

## backgrounds.xml

Defines background options and groupings.

```xml
<backgrounds>
  <!-- Static background -->
  <background name="default" label="Default" type="static">
    <path>special://skin/backgrounds/default.jpg</path>
    <icon>DefaultPicture.png</icon>
  </background>

  <!-- Property-based (info label) -->
  <background name="movie-fanart" label="Movie Fanart" type="property"
              visible="Library.HasContent(movies)">
    <path>$INFO[Container(9000).ListItem.Art(fanart)]</path>
  </background>

  <!-- Browse for single image -->
  <background name="custom" label="Custom Image" type="browse">
    <source label="Skin Backgrounds">special://skin/backgrounds/</source>
    <source label="Browse...">browse</source>
  </background>

  <!-- Browse for folder (slideshow) -->
  <background name="folder" label="Image Folder" type="multi">
    <source label="My Backgrounds">special://profile/backgrounds/</source>
    <source label="Browse...">browse</source>
  </background>

  <!-- Playlist-based -->
  <background name="playlist" label="Playlist Images" type="playlist">
    <source label="Video Playlists">special://profile/playlists/video/</source>
  </background>

  <!-- Live background -->
  <background name="live-movies" label="Random Movies" type="live"
              visible="Library.HasContent(movies)">
    <path>random movies</path>
  </background>

  <!-- Group -->
  <group name="library" label="Library Fanart" icon="DefaultVideo.png"
         visible="Library.HasContent(movies)">
    <background name="movie-fanart" label="Movie Fanart" type="property">
      <path>$INFO[Window(Home).Property(MovieFanart)]</path>
    </background>
  </group>
</backgrounds>
```

### Element Reference

| Element | Parent | Required Attributes | Optional Attributes | Description |
|---------|--------|---------------------|---------------------|-------------|
| `<backgrounds>` | — | — | — | Root element |
| `<background>` | backgrounds/group | `name`, `label` | `type`, `condition`, `visible` | Background definition |
| `<path>` | background | — | — | Image path or info label |
| `<icon>` | background | — | — | Icon for picker |
| `<source>` | background | — | `label`, `condition`, `visible`, `icon` | Browse/playlist source |
| `<group>` | backgrounds/group | `name`, `label` | `condition`, `visible`, `icon` | Background group |
| `<content>` | group | `source` | `target`, etc. | Dynamic content |

### Background Types

| Type | Description | Path Required |
|------|-------------|---------------|
| `static` | Single image file | Yes |
| `property` | Kodi info label resolving to image | Yes |
| `browse` | User browses for single image | No |
| `multi` | User browses for folder (slideshow) | No |
| `playlist` | Images from user-selected playlist | No |
| `live` | Dynamic content from library | Yes |
| `live-playlist` | Dynamic content from playlist | No |

***

## properties.xml

Defines property schemas, button mappings, and fallback values.

```xml
<properties>
  <includes>
    <include name="artOptions">
      <option value="Poster" label="Poster"/>
      <option value="Landscape" label="Landscape"/>
    </include>
  </includes>

  <property name="widgetStyle" type="options" requires="widget">
    <options>
      <option value="Panel" label="Panel"/>
      <option value="Wide" label="Wide"/>
      <include content="artOptions"/>
    </options>
  </property>

  <property name="hideLabels" type="toggle"/>

  <buttons suffix="true">
    <button id="350" property="widgetStyle" title="Widget Style" requires="widget"/>
    <group suffix="false">
      <button id="360" property="hideLabels" title="Hide Labels" type="toggle"/>
    </group>
  </buttons>

  <fallbacks>
    <fallback property="widgetStyle">
      <when condition="widgetType=movies">Panel</when>
      <default>Wide</default>
    </fallback>
  </fallbacks>
</properties>
```

### Element Reference

| Element | Parent | Required Attributes | Optional Attributes | Description |
|---------|--------|---------------------|---------------------|-------------|
| `<properties>` | — | — | — | Root element |
| `<includes>` | properties | — | — | Reusable definitions |
| `<include>` | includes | `name` | — | Include definition |
| `<include/>` | options/fallback | `content` | `suffix` | Include reference |
| `<property>` | properties | `name` | `type`, `requires`, `templateonly` | Property definition |
| `<options>` | property | — | — | Option container |
| `<option>` | options/include | `value`, `label` | `condition` | Option value |
| `<icon>` | option | — | `condition` | Option icon |
| `<buttons>` | properties | — | `suffix` | Button mappings |
| `<group>` | buttons | — | `suffix` | Button group |
| `<button>` | buttons/group | `id`, `property` | `title`, `suffix`, `showNone`, `showIcons`, `type`, `requires` | Button mapping |
| `<fallbacks>` | properties | — | — | Fallback definitions |
| `<fallback>` | fallbacks | `property` | — | Fallback for property |
| `<when>` | fallback | `condition` | — | Conditional fallback |
| `<default>` | fallback | — | — | Default fallback |

### Property Types

| Type | Behavior |
|------|----------|
| `options` | Select from defined options list |
| `toggle` | Toggle between `True` and empty |
| `widget` | Opens widget picker |
| `background` | Opens background picker |

***

## templates.xml

Defines templates for generating skin includes.

```xml
<templates>
  <template name="menus">
    <controls>
      <skinshortcuts include="submenu-widget" condition="String.IsEmpty(ListItem.Property(widgetPath))"/>
      <control type="group">
        <visible>!String.IsEmpty(Container(9000).ListItem.Property(widgetPath))</visible>
        <control type="list">
          <content>$PROPERTY[widgetPath]</content>
        </control>
      </control>
    </controls>
  </template>

  <include name="submenu-widget">
    <control type="list">
      <content>$PROPERTY[submenuPath]</content>
    </control>
  </include>
</templates>
```

### Element Reference

| Element | Parent | Required Attributes | Optional Attributes | Description |
|---------|--------|---------------------|---------------------|-------------|
| `<templates>` | — | — | — | Root element |
| `<template>` | templates | `name` | `condition` | Template definition |
| `<controls>` | template | — | — | Control container |
| `<other>` | template | — | — | Non-iterated content |
| `<include>` | templates | `name` | — | Reusable include definition |
| `<skinshortcuts>` | controls/other | — | `include`, `condition`, `visible`, `wrap` | Include expansion tag |

### Placeholders

| Placeholder | Description |
|-------------|-------------|
| `$PROPERTY[name]` | Item property value |
| `$SKINBOOL[name]` | Skin boolean setting |
| `$LOCALIZE[id]` | Localized string |
| `$INCLUDE[name]` | Converted to `<include>name</include>` in output |

***

## Condition Syntax

Property conditions used in `condition` attributes (evaluated against item properties).

### Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Equals | `widgetType=movies` |
| `~` | Contains | `widgetPath~skin.helper` |
| `!` | Negation | `!widgetType=weather` |
| `\|` | OR | `widgetType=movies \| tvshows` |
| `+` | AND | `widget=library + widgetType=movies` |
| `[...]` | Grouping | `![widgetType=weather \| system]` |

### Compact OR Syntax

```
widgetType=movies | episodes | tvshows
```

Expands to:

```
widgetType=movies | widgetType=episodes | widgetType=tvshows
```

***

## Dynamic Content Sources

For `<content source="...">` elements:

| Source | Description |
|--------|-------------|
| `playlists` | User playlists |
| `addons` | Installed addons |
| `sources` | File sources |
| `favourites` | User favourites |
| `pvr` | PVR channels/recordings |
| `commands` | System commands |
| `settings` | Settings shortcuts |
| `library` | Library database content (genres, years, actors, etc.) |
| `nodes` | Library navigation nodes (Movies, TV Shows, etc.) |

### Library Targets

`moviegenres`, `tvgenres`, `musicgenres`, `years`, `movieyears`, `tvyears`, `studios`, `moviestudios`, `tvstudios`, `tags`, `movietags`, `tvtags`, `actors`, `movieactors`, `tvactors`, `directors`, `moviedirectors`, `tvdirectors`, `artists`, `albums`

### Nodes Targets

`video`, `music`

***

## Output Properties

### Widget Properties

| Property | Description |
|----------|-------------|
| `widget` | Widget name |
| `widgetPath` | Content path |
| `widgetLabel` | Display label |
| `widgetTarget` | Target window |

### Background Properties

| Property | Description |
|----------|-------------|
| `background` | Background name |
| `backgroundPath` | Image path |
| `backgroundLabel` | Display label |
| `backgroundType` | Background type |

Additional properties configured via `properties.xml`.
