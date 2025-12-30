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
    <allow widgets="true" backgrounds="true" submenus="true" />
    <defaults widget="recent-movies" background="movie-fanart">
      <action when="before">Dialog.Close(all,true)</action>
      <property name="widgetStyle">Panel</property>
    </defaults>
    <item name="movies" submenu="movies" widget="recent-movies" background="movie-fanart" required="true">
      <label>$LOCALIZE[20342]</label>
      <label2>Video Library</label2>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
      <action condition="!Library.HasContent(movies)">ActivateWindow(Videos,files)</action>
      <icon>DefaultMovies.png</icon>
      <thumb>special://skin/thumbs/movies.png</thumb>
      <visible>Library.HasContent(movies)</visible>
      <disabled>false</disabled>
      <property name="widgetStyle">Panel</property>
      <protect type="action" heading="$LOCALIZE[31001]" message="$LOCALIZE[31002]" />
    </item>
  </menu>

  <submenu name="movies" container="9001">
    <allow widgets="false" backgrounds="false" submenus="false" />
    <item name="recent">
      <label>Recent</label>
      <action>ActivateWindow(Videos,videodb://recentlyaddedmovies/)</action>
    </item>
  </submenu>

  <groupings>
    <group name="common" label="Common" icon="DefaultShortcut.png" condition="..." visible="...">
      <shortcut name="movies" label="Movies" icon="DefaultMovies.png" type="Video" condition="..." visible="...">
        <action>ActivateWindow(Videos,videodb://movies/)</action>
      </shortcut>
      <shortcut name="playlists" label="Playlists" icon="DefaultPlaylist.png" path="special://profile/playlists/video/" browse="videos" />
      <group name="nested" label="Nested Group">...</group>
      <content source="playlists" target="videos" folder="Video Playlists" label="..." icon="..." condition="..." visible="..." />
    </group>
  </groupings>

  <icons>
    <source label="Skin Icons" icon="DefaultFolder.png" condition="..." visible="...">special://skin/extras/icons/</source>
    <source label="Browse...">browse</source>
  </icons>

  <overrides>
    <action replace="ActivateWindow(favourites)">ActivateWindow(favouritesbrowser)</action>
  </overrides>

  <dialogs>
    <subdialog buttonID="800" mode="widget1" setfocus="309">
      <onclose action="menu" menu="{item}.customwidget" condition="widgetType=custom" />
    </subdialog>
    <subdialog buttonID="801" mode="widget2" setfocus="309" suffix=".2" />
  </dialogs>

  <contextmenu>true</contextmenu>
</menus>
```

### Element Reference

| Element | Parent | Required Attributes | Optional Attributes | Description |
|---------|--------|---------------------|---------------------|-------------|
| `<menu>` | menus | `name` | `container` | Main menu definition |
| `<submenu>` | menus | `name` | `container` | Submenu definition (built when referenced) |
| `<allow>` | menu/submenu | — | `widgets`, `backgrounds`, `submenus` | Feature toggles for dialog |
| `<defaults>` | menu/submenu | — | `widget`, `background` | Default settings for items |
| `<action>` | defaults | — | `when`, `condition` | Default action (before/after) |
| `<property>` | defaults | `name` | — | Default property value |
| `<item>` | menu/submenu | `name` | `submenu`, `widget`, `background`, `required`, `visible` | Menu item |
| `<label>` | item | — | — | Display text |
| `<label2>` | item | — | — | Secondary label |
| `<action>` | item | — | `condition` | Action to execute (multiple allowed) |
| `<icon>` | item | — | — | Icon path |
| `<thumb>` | item | — | — | Thumbnail path |
| `<visible>` | item | — | — | Visibility condition for output |
| `<disabled>` | item | — | — | If "true", item not selectable |
| `<property>` | item | `name` | — | Custom property |
| `<protect>` | item | — | `type`, `heading`, `message` | Protection rule |
| `<groupings>` | menus | — | — | Shortcut picker structure |
| `<group>` | groupings/group | `name`, `label` | `condition`, `visible`, `icon` | Shortcut group |
| `<shortcut>` | group | `name`, `label` | `icon`, `type`, `condition`, `visible`, `path`, `browse` | Shortcut option |
| `<action>` | shortcut | — | — | Shortcut action |
| `<path>` | shortcut | — | — | Browse path (for browse mode) |
| `<content>` | group | `source` | `target`, `path`, `condition`, `visible`, `icon`, `label`, `folder` | Dynamic content |
| `<icons>` | menus | — | — | Icon browser sources |
| `<source>` | icons | — | `label`, `condition`, `visible`, `icon` | Icon source path |
| `<overrides>` | menus | — | — | Action overrides |
| `<action>` | overrides | `replace` | — | Replacement action |
| `<dialogs>` | menus | — | — | Subdialog definitions |
| `<subdialog>` | dialogs | `buttonID`, `mode` | `setfocus`, `suffix` | Subdialog mapping |
| `<onclose>` | subdialog | `action` | `menu`, `condition` | Action when subdialog closes |
| `<contextmenu>` | menus | — | — | Enable/disable context menu |

### Protect Types

| Type | Description |
|------|-------------|
| `delete` | Confirm before deleting |
| `action` | Confirm before changing action |
| `all` | Confirm both |

***

## widgets.xml

Defines widgets and widget picker groupings.

```xml
<widgets showGetMore="true">
  <!-- Flat widget at root level -->
  <widget name="favourites" label="Favourites" type="videos" target="videos" icon="DefaultFavourites.png" source="library" condition="..." visible="...">
    <path>favourites://</path>
    <limit>25</limit>
    <sortby>dateadded</sortby>
    <sortorder>descending</sortorder>
  </widget>

  <!-- Custom widget (no path required) -->
  <widget name="custom" label="Custom" type="custom" slot="widget" />

  <!-- Group with nested widgets -->
  <group name="movies" label="Movies" icon="DefaultMovies.png" source="library" condition="..." visible="Library.HasContent(movies)">
    <widget name="recent" label="Recent" type="movies" icon="DefaultRecentlyAddedMovies.png">
      <path>videodb://recentlyaddedmovies/</path>
      <limit>25</limit>
    </widget>

    <!-- Nested group -->
    <group name="genres" label="By Genre">
      <content source="library" target="moviegenres" />
    </group>

    <!-- Dynamic content -->
    <content source="playlists" target="videos" folder="Playlists" />
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
| `<sortorder>` | widget | — | — | Sort direction (`ascending`/`descending`) |
| `<group>` | widgets/group | `name`, `label` | `condition`, `visible`, `icon`, `source` | Widget group |
| `<content>` | group | `source` | `target`, `path`, `condition`, `visible`, `icon`, `label`, `folder` | Dynamic content |

### Widget Types

`movies`, `tvshows`, `episodes`, `musicvideos`, `sets`, `albums`, `artists`, `songs`, `pictures`, `pvr`, `games`, `addons`, `custom`

### Widget Output Properties

| Property | Description |
|----------|-------------|
| `widget` | Widget name |
| `widgetLabel` | Display label |
| `widgetPath` | Content path |
| `widgetTarget` | Target window |
| `widgetType` | Content type |
| `widgetSource` | Source type |

***

## backgrounds.xml

Defines background options and groupings.

```xml
<backgrounds>
  <!-- Static background -->
  <background name="default" label="Default" type="static" condition="..." visible="...">
    <path>special://skin/backgrounds/default.jpg</path>
    <icon>DefaultPicture.png</icon>
  </background>

  <!-- Property-based (info label) -->
  <background name="movie-fanart" label="Movie Fanart" type="property" visible="Library.HasContent(movies)">
    <path>$INFO[Container(9000).ListItem.Art(fanart)]</path>
  </background>

  <!-- Browse for single image -->
  <background name="custom" label="Custom Image" type="browse">
    <source label="Skin Backgrounds" icon="DefaultFolder.png" condition="..." visible="...">
      special://skin/backgrounds/
    </source>
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
  <background name="live-movies" label="Random Movies" type="live" visible="Library.HasContent(movies)">
    <path>random movies</path>
  </background>

  <!-- Live playlist background -->
  <background name="live-playlist" label="Live Playlist" type="live-playlist">
    <source label="Video Playlists">special://profile/playlists/video/</source>
  </background>

  <!-- Group -->
  <group name="library" label="Library Fanart" icon="DefaultVideo.png" condition="..." visible="Library.HasContent(movies)">
    <background name="movie-fanart" label="Movie Fanart" type="property">
      <path>$INFO[Window(Home).Property(MovieFanart)]</path>
    </background>
    <group name="nested" label="Nested">...</group>
    <content source="playlists" target="videos" />
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

### Live Path Values

| Path | Description |
|------|-------------|
| `random movies` | Random movie fanart |
| `random tvshows` | Random TV show fanart |
| `random music` | Random album art |

### Background Output Properties

| Property | Description |
|----------|-------------|
| `background` | Background name |
| `backgroundPath` | Image path |
| `backgroundLabel` | Display label |
| `backgroundType` | Background type |
| `backgroundPlaylistType` | Playlist content type |

***

## properties.xml

Defines property schemas, button mappings, and fallback values.

```xml
<properties>
  <includes>
    <include name="artOptions">
      <option value="Poster" label="Poster">
        <icon>poster.png</icon>
        <icon condition="widgetType=movies">movie-poster.png</icon>
      </option>
      <option value="Landscape" label="Landscape">
        <icon>landscape.png</icon>
      </option>
    </include>
  </includes>

  <property name="widgetStyle" type="options" requires="widget" templateonly="false">
    <options>
      <option value="Panel" label="Panel" condition="..." />
      <option value="Wide" label="Wide" />
      <include content="artOptions" suffix=".2" />
    </options>
  </property>

  <property name="hideLabels" type="toggle" />
  <property name="extraWidget" type="widget" />
  <property name="customBg" type="background" />

  <buttons suffix="true">
    <button id="350" property="widgetStyle" title="Widget Style" suffix="true" showNone="true" showIcons="true" type="options" requires="widget" />
    <group suffix="false">
      <button id="360" property="hideLabels" title="Hide Labels" type="toggle" />
    </group>
  </buttons>

  <fallbacks>
    <fallback property="widgetStyle">
      <when condition="widgetType=movies">Panel</when>
      <when condition="widgetType=tvshows">Wide</when>
      <include content="styleFallbacks" />
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
| `<icon>` | option | — | `condition` | Option icon (multiple allowed) |
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

Defines templates for generating skin includes. For detailed documentation, see [Template Configuration](skinning/templates.md).

```xml
<templates>
  <!-- Named expressions -->
  <expressions>
    <expression name="HasWidget" nosuffix="false">widgetPath</expression>
    <expression name="WidgetContainer" nosuffix="true">9000</expression>
  </expressions>

  <!-- Lookup tables -->
  <presets>
    <preset name="WidgetDimensions">
      <values condition="widgetArt=Poster" width="200" height="300" />
      <values condition="widgetArt=Landscape" width="356" height="200" />
      <values width="200" height="200" />
    </preset>
  </presets>

  <!-- Reusable property groups -->
  <propertyGroups>
    <propertyGroup name="widgetProps">
      <property name="path" from="widgetPath" condition="..." />
      <property name="staticValue">245</property>
      <var name="layout">
        <value condition="widgetStyle=Panel">panel</value>
        <value>list</value>
      </var>
      <preset content="WidgetDimensions" />
      <propertyGroup content="nestedGroup" />
    </propertyGroup>
  </propertyGroups>

  <!-- Reusable control snippets -->
  <includes>
    <include name="FocusAnimation">
      <animation effect="zoom" start="90" end="100" time="200">Focus</animation>
    </include>
  </includes>

  <!-- Variable definitions -->
  <variables>
    <variable name="MenuLabel">
      <value condition="Container(9000).HasFocus($PROPERTY[index])">
        $INFO[Container(9000).ListItem($PROPERTY[index]).Label]
      </value>
    </variable>
    <variableGroup name="menuVars">
      <variable name="MenuLabel" />
      <variableGroup content="nestedVars" />
    </variableGroup>
  </variables>

  <!-- Template with single output -->
  <template include="MainMenu" idprefix="80" build="menu" menu="mainmenu" templateonly="auto">
    <condition>widgetType</condition>
    <property name="style" from="widgetStyle" condition="..." />
    <property name="staticValue">100</property>
    <var name="aspect">
      <value condition="widgetArt=Poster">stretch</value>
      <value>scale</value>
    </var>
    <preset content="WidgetDimensions" suffix=".2" condition="..." />
    <propertyGroup content="widgetProps" suffix=".2" condition="..." />
    <variableGroup content="menuVars" suffix=".2" condition="..." />

    <controls>
      <control type="button" id="$MATH[$PROPERTY[index] * 1000 + 100]">
        <label>$PROPERTY[label]</label>
        <onclick>$PROPERTY[path]</onclick>
        <skinshortcuts>visibility</skinshortcuts>
        <skinshortcuts include="FocusAnimation" />
        <skinshortcuts include="OptionalContent" condition="widgetPath" wrap="true" />
      </control>

      <!-- Submenu items iteration -->
      <skinshortcuts items="widgets" condition="widgetType=custom" filter="widgetArt=Poster">
        <var name="widgetInclude">
          <value condition="widgetArt=Poster">Widget_Poster</value>
          <value>Widget_Default</value>
        </var>
        <preset content="WidgetDimensions" />
        <propertyGroup content="widgetProps" />
        <control type="group" id="$MATH[$PARENT[index] * 1000 + 600 + $PROPERTY[index]]">
          <include content="$PROPERTY[widgetInclude]">
            <param name="path">$PROPERTY[widgetPath]</param>
            <param name="limit">$IF[$PROPERTY[widgetLimit] THEN $PROPERTY[widgetLimit] ELSE 25]</param>
          </include>
        </control>
      </skinshortcuts>
    </controls>

    <variables>
      <variable name="WidgetPath-$PROPERTY[name]" condition="widgetPath" output="...">
        <value condition="...">$INFO[...]</value>
      </variable>
    </variables>
  </template>

  <!-- Template with multiple outputs -->
  <template>
    <output include="widget1" idprefix="8011" />
    <output include="widget2" idprefix="8021" suffix=".2" />
    <condition>widgetPath</condition>
    <controls>...</controls>
  </template>

  <!-- List mode template -->
  <template include="WidgetSlots" build="list">
    <list>
      <item slot="" label="Widget 1" />
      <item slot=".2" label="Widget 2" />
    </list>
    <property name="suffix" from="slot" />
    <controls>...</controls>
  </template>

  <!-- Raw mode template -->
  <template include="UtilityInclude" build="true">
    <param name="id" default="9000" />
    <controls>
      <control type="group" id="$PARAM[id]" />
    </controls>
  </template>

  <!-- Submenu template -->
  <submenu include="Submenu" level="1" name="">
    <property name="parent" from="name" />
    <controls>...</controls>
  </submenu>
</templates>
```

### Element Reference

| Element | Parent | Required Attributes | Optional Attributes | Description |
|---------|--------|---------------------|---------------------|-------------|
| `<templates>` | — | — | — | Root element |
| `<expressions>` | templates | — | — | Named expression definitions |
| `<expression>` | expressions | `name` | `nosuffix` | Reusable expression |
| `<presets>` | templates | — | — | Preset lookup tables |
| `<preset>` | presets | `name` | — | Preset with conditional values |
| `<values>` | preset | — | `condition`, *attributes* | Preset row with attribute values |
| `<propertyGroups>` | templates | — | — | Reusable property groups |
| `<propertyGroup>` | propertyGroups | `name` | — | Property group definition |
| `<includes>` | templates | — | — | Reusable control snippets |
| `<include>` | includes | `name` | — | Include definition |
| `<variables>` | templates/template | — | — | Variable definitions |
| `<variable>` | variables | `name` | `condition`, `output` | Variable definition |
| `<value>` | variable | — | `condition` | Variable value |
| `<variableGroup>` | variables | `name` | — | Variable group definition |
| `<template>` | templates | — | `include`, `build`, `idprefix`, `templateonly`, `menu` | Template definition |
| `<output>` | template | `include` | `idprefix`, `suffix` | Multi-output target |
| `<condition>` | template | — | — | Template condition (ANDed) |
| `<property>` | template/propertyGroup | `name` | `from`, `condition` | Property definition |
| `<var>` | template/propertyGroup/items | `name` | — | Conditional variable |
| `<value>` | var | — | `condition` | Var value (first match wins) |
| `<preset/>` | template/propertyGroup/items | `content` | `condition`, `suffix` | Apply preset reference |
| `<propertyGroup/>` | template/propertyGroup/items | `content` | `condition`, `suffix` | Apply property group |
| `<variableGroup/>` | template | `content` | `condition`, `suffix` | Apply variable group |
| `<list>` | template | — | — | List items (build="list") |
| `<item>` | list | — | *attributes* | List item |
| `<param>` | template | `name` | `default` | Parameter (build="true") |
| `<controls>` | template/submenu | — | — | Control container |
| `<skinshortcuts>` | controls | — | `include`, `condition`, `wrap`, `items`, `filter` | Special tag |
| `<submenu>` | templates | — | `include`, `level`, `name` | Submenu template |

### Skinshortcuts Tag

| Usage | Description |
|-------|-------------|
| `<skinshortcuts>visibility</skinshortcuts>` | Generate visibility condition |
| `<skinshortcuts include="name" />` | Expand include (unwrapped) |
| `<skinshortcuts include="name" wrap="true" />` | Output as Kodi `<include>` |
| `<skinshortcuts include="name" condition="prop" />` | Conditional include |
| `<skinshortcuts items="widgets" />` | Iterate submenu items |
| `<skinshortcuts items="widgets" filter="widgetArt=Poster" />` | Filtered iteration |
| `<skinshortcuts items="widgets" condition="widgetType=custom" />` | Conditional iteration |

### Dynamic Expressions

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `$PROPERTY[name]` | Item property value | `$PROPERTY[widgetPath]` |
| `$PARENT[name]` | Parent item property (items iteration) | `$PARENT[label]` |
| `$EXP[name]` | Expression value | `$EXP[HasWidget]` |
| `$MATH[expr]` | Arithmetic expression | `$MATH[index * 1000 + 100]` |
| `$IF[cond THEN val ELSE val]` | Conditional value | `$IF[widgetLimit THEN $PROPERTY[widgetLimit] ELSE 25]` |
| `$INCLUDE[name]` | Converted to `<include>` | `$INCLUDE[skinshortcuts-template-Widgets]` |
| `$PARAM[name]` | Parameter (raw mode) | `$PARAM[id]` |

### Math Operators

| Operator | Description |
|----------|-------------|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `//` | Floor division |
| `%` | Modulo |
| `()` | Grouping |

### Build Modes

| Mode | Attribute | Description |
|------|-----------|-------------|
| Menu | `build="menu"` (default) | Iterate over menu items |
| List | `build="list"` | Iterate over explicit `<list><item>` |
| Raw | `build="true"` | No iteration, output controls once |

### Built-in Properties

| Property | Description |
|----------|-------------|
| `index` | Item index (1-based) |
| `name` | Item name identifier |
| `menu` | Parent menu name |
| `idprefix` | Template's idprefix value |
| `id` | Computed ID: `{idprefix}{index}` |
| `suffix` | Output suffix (e.g., `.2`) or empty |
| `label` | Item label |
| `path` | Primary action |

***

## Condition Syntax

Property conditions used in `condition` attributes (evaluated against item properties).

### Operators

| Symbol | Keyword | Description | Example |
|--------|---------|-------------|---------|
| *(none)* | — | Has value (truthy) | `widgetPath` |
| `=` | `EQUALS` | Equals | `widgetType=movies` |
| `~` | `CONTAINS` | Contains | `widgetPath~skin.helper` |
| `!` | `NOT` | Negation | `!widgetType=weather` |
| — | `EMPTY` | Is empty | `widgetPath EMPTY` |
| — | `IN` | Value in list | `widgetType IN movies,episodes` |
| `\|` | `OR` | Logical OR | `widgetType=movies \| tvshows` |
| `+` | `AND` | Logical AND | `widget=library + widgetType=movies` |
| `[...]` | — | Grouping | `![widgetType=weather \| system]` |

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

`genres`, `moviegenres`, `tvgenres`, `musicgenres`, `years`, `movieyears`, `tvyears`, `studios`, `moviestudios`, `tvstudios`, `tags`, `movietags`, `tvtags`, `actors`, `movieactors`, `tvactors`, `directors`, `moviedirectors`, `tvdirectors`, `artists`, `albums`

### Nodes Targets

`videos`, `music`

***

## RunScript Parameters

### Build XML

```
RunScript(script.skinshortcuts,type=buildxml)
```

Generates the includes file.

### Manage Menu

```
RunScript(script.skinshortcuts,type=manage,menu=mainmenu)
```

| Parameter | Description |
|-----------|-------------|
| `menu` | Menu to edit (e.g., `mainmenu`, `movies`) |

### Reset All

```
RunScript(script.skinshortcuts,type=resetall)
```

Resets all user data to defaults.

### Clear Menu

```
RunScript(script.skinshortcuts,type=clear,menu=mainmenu)
```

Clears a specific menu's user data.

***

## Window Properties

### Management Dialog Properties

| Property | Description |
|----------|-------------|
| `menuname` | Current menu ID being edited |
| `allowWidgets` | `true` if widgets enabled for this menu |
| `allowBackgrounds` | `true` if backgrounds enabled for this menu |
| `allowSubmenus` | `true` if submenus enabled for this menu |
| `skinshortcuts-hasdeleted` | `true` if deleted items exist |

### Home Window Properties

| Property | Description |
|----------|-------------|
| `skinshortcuts-dialog` | Current subdialog mode |
| `skinshortcuts-suffix` | Current property suffix (e.g., `.2`) |

***

## Output Properties

### Widget Properties

| Property | Description |
|----------|-------------|
| `widget` | Widget name |
| `widgetPath` | Content path |
| `widgetLabel` | Display label |
| `widgetTarget` | Target window |
| `widgetType` | Content type |
| `widgetSource` | Source type |

### Background Properties

| Property | Description |
|----------|-------------|
| `background` | Background name |
| `backgroundPath` | Image path |
| `backgroundLabel` | Display label |
| `backgroundType` | Background type |
| `backgroundPlaylistType` | Playlist content type |

Additional properties configured via `properties.xml`.

### Multiple Slots

| Slot | Properties |
|------|------------|
| Widget 1 | `widget`, `widgetPath`, `widgetType`, etc. |
| Widget 2 | `widget.2`, `widgetPath.2`, `widgetType.2`, etc. |
| Widget 3 | `widget.3`, `widgetPath.3`, `widgetType.3`, etc. |
