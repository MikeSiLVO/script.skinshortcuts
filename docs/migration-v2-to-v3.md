# Skin Shortcuts v2 to v3 Migration Guide

**v3 is a complete rewrite and is NOT backward compatible with v2.**

This guide covers all changes needed to migrate a v2 skin to v3.

***

## Table of Contents

* [Breaking Changes](#breaking-changes)
* [File Structure](#file-structure)
* [menus.xml Migration](#menusxml-migration)
* [widgets.xml Migration](#widgetsxml-migration)
* [backgrounds.xml Migration](#backgroundsxml-migration)
* [properties.xml Migration](#propertiesxml-migration)
* [templates.xml Migration](#templatesxml-migration)
* [RunScript Parameters](#runscript-parameters)
* [Management Dialog Controls](#management-dialog-controls)
* [Window Properties](#window-properties)
* [Property Name Changes](#property-name-changes)
* [User Data Format](#user-data-format)
* [Migration Checklist](#migration-checklist)

***

## Breaking Changes

### Not Compatible

* v2 `overrides.xml` does not work in v3
* v2 user data (XML files) cannot be migrated automatically
* v2 template syntax is different from v3

### What Users Lose

* All existing menu customizations (users must reconfigure menus)
* Custom widget assignments
* Background selections
* Property settings

### What Skinners Must Do

1. Create new configuration files (`menus.xml`, etc.)
2. Update dialog XML (remove obsolete controls)
3. Update RunScript calls
4. Rewrite `templates.xml` if using custom templates (different syntax)
5. Update skin XML references to generated includes (if names changed)

***

## File Structure

### v2: Single File

```
shortcuts/
└── overrides.xml    (everything in one file)
```

### v3: Split Files

```
shortcuts/
├── menus.xml        (required)
├── widgets.xml      (optional)
├── backgrounds.xml  (optional)
├── properties.xml   (optional)
└── templates.xml    (optional)
```

### User Data Location

| v2                            | v3                        |
| ----------------------------- | ------------------------- |
| `{skin_id}_mainmenu.DATA.xml` | `{skin_id}.userdata.json` |
| Multiple per-menu XML files   | Single JSON file          |

***

## menus.xml Migration

### v2: Shortcuts and Defaults

```xml
<overrides>
  <!-- Shortcuts added to groupings via grouping attribute -->
  <shortcut label="Movies" type="Video" grouping="common" icon="DefaultMovies.png">
    ActivateWindow(Videos,videodb://movies/)
  </shortcut>
  <shortcut label="TV Shows" type="Video" grouping="common" icon="DefaultTVShows.png">
    ActivateWindow(Videos,videodb://tvshows/)
  </shortcut>

  <!-- Custom groupings structure -->
  <groupings>
    <node label="Common">
      <content>common</content>
    </node>
    <node label="Video">
      <content>video</content>
    </node>
  </groupings>

  <!-- Defaults -->
  <widgetdefault labelID="movies">recent-movies</widgetdefault>
  <backgrounddefault labelID="movies">movie-fanart</backgrounddefault>
  <propertydefault labelID="movies" property="widgetStyle">Panel</propertydefault>
</overrides>
```

### v3: Menus and Groupings

```xml
<menus>
  <menu name="mainmenu" container="9000">
    <!-- <allow> is optional, all attributes default to true -->
    <allow widgets="true" backgrounds="true" submenus="true" />
    <defaults widget="default-widget" background="default-bg">
      <action when="before">Dialog.Close(all,true)</action>
      <property name="widgetStyle">Panel</property>
    </defaults>

    <item name="movies" submenu="movies" widget="recent-movies" background="movie-fanart">
      <label>$LOCALIZE[20342]</label>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
      <icon>DefaultMovies.png</icon>
      <visible>Library.HasContent(movies)</visible>
      <property name="widgetStyle">Panel</property>
    </item>

    <item name="tvshows" submenu="tvshows" widget="recent-tvshows">
      <label>$LOCALIZE[20343]</label>
      <action>ActivateWindow(Videos,videodb://tvshows/)</action>
      <icon>DefaultTVShows.png</icon>
    </item>
  </menu>

  <submenu name="movies">
    <allow widgets="false" />
    <item name="all">
      <label>All Movies</label>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
    </item>
    <item name="recent">
      <label>Recently Added</label>
      <action>ActivateWindow(Videos,videodb://recentlyaddedmovies/)</action>
    </item>
  </submenu>

  <groupings>
    <group name="common" label="Common Shortcuts" icon="DefaultShortcut.png">
      <shortcut name="movies" label="Movies" icon="DefaultMovies.png">
        <action>ActivateWindow(Videos,videodb://movies/)</action>
      </shortcut>
      <shortcut name="tvshows" label="TV Shows" icon="DefaultTVShows.png">
        <action>ActivateWindow(Videos,videodb://tvshows/)</action>
      </shortcut>
      <content source="playlists" target="videos" folder="Video Playlists" />
      <content source="favourites" />
    </group>
  </groupings>

  <icons>
    <source label="Skin Icons">special://skin/extras/icons/</source>
    <source label="Browse...">browse</source>
  </icons>

  <dialogs>
    <subdialog buttonID="800" mode="widget1" setfocus="309" />
    <subdialog buttonID="801" mode="widget2" setfocus="309" suffix=".2" />
  </dialogs>

  <overrides>
    <action replace="ActivateWindow(favourites)">ActivateWindow(favouritesbrowser)</action>
  </overrides>

  <contextmenu>true</contextmenu>
</menus>
```

### Key Mappings

| v2 Element                                               | v3 Element                                                         |
| -------------------------------------------------------- | ------------------------------------------------------------------ |
| `<groupings>` → `<node label="...">`                     | `<groupings>` → `<group name="..." label="...">`                   |
| `<shortcut label="..." grouping="...">action</shortcut>` | `<shortcut name="..." label="..."><action>...</action></shortcut>` |
| `<widgetdefault labelID="...">`                          | `<item widget="...">` or `<defaults widget="...">`                 |
| `<backgrounddefault labelID="...">`                      | `<item background="...">` or `<defaults background="...">`         |
| `<propertydefault labelID="...">`                        | `<item><property name="...">` or `<defaults><property>`            |
| N/A                                                      | `<submenu name="...">` for explicit submenu structure              |
| N/A                                                      | `<menu name="...">` for standalone menus                           |
| N/A                                                      | `<allow/>` (optional, all attributes default to true)              |

### Global Overrides

v2 (supplemental action for all items in a menu):

```xml
<groupoverride group="mainmenu" condition="Window.IsActive(DialogButtonMenu.xml)">
  Close
</groupoverride>
```

v3 (before/after actions in defaults):

```xml
<defaults>
  <action when="before">Dialog.Close(all,true)</action>
  <action when="after" condition="...">SetProperty(...)</action>
</defaults>
```

### Action Overrides

v2 (override specific action):

```xml
<override action="ActivateWindow(Videos,videodb://movies/)">
  <condition>!Library.HasContent(movies)</condition>
  <action>ActivateWindow(Videos,files)</action>
</override>
```

v3 (conditional actions on item):

```xml
<item name="movies">
  <label>Movies</label>
  <action condition="Library.HasContent(movies)">ActivateWindow(Videos,videodb://movies/)</action>
  <action condition="!Library.HasContent(movies)">ActivateWindow(Videos,files)</action>
</item>
```

### Required Items (v3 only)

```xml
<item name="settings" required="true">
  <label>Settings</label>
  <action>ActivateWindow(Settings)</action>
</item>
```

Items with `required="true"` cannot be deleted by users.

### Protection (v3 only)

```xml
<item name="power">
  <label>Power</label>
  <action>ActivateWindow(ShutdownMenu)</action>
  <protect type="action" heading="Confirm" message="Change power action?" />
</item>
```

***

## widgets.xml Migration

### v2 (in overrides.xml)

```xml
<overrides>
  <!-- Widget definitions -->
  <widget label="Recent Movies" name="recent-movies" type="movies">
    special://videoplaylists/RecentMovies.xsp
  </widget>
  <widget label="In Progress" name="inprogress-movies" type="movies">
    videodb://inprogressmovies/
  </widget>

  <!-- Widget groupings (customize picker structure) -->
  <widget-groupings>
    <node label="Movies">
      <content>video</content>
      <node label="Playlists">
        <content>playlist-video</content>
      </node>
    </node>
    <content>widgets</content>
  </widget-groupings>
</overrides>
```

### v3 (widgets.xml)

```xml
<widgets showGetMore="true">
  <group name="movies" label="Movies" icon="DefaultMovies.png" visible="Library.HasContent(movies)">
    <widget name="recent-movies" label="Recently Added" type="movies" icon="DefaultRecentlyAddedMovies.png">
      <path>videodb://recentlyaddedmovies/</path>
      <limit>25</limit>
      <sortby>dateadded</sortby>
      <sortorder>descending</sortorder>
    </widget>

    <widget name="inprogress-movies" label="In Progress" type="movies">
      <path>videodb://inprogressmovies/</path>
    </widget>

    <!-- Dynamic content from playlists -->
    <content source="playlists" target="videos" />

    <!-- Dynamic content from library -->
    <content source="library" target="moviegenres" />
  </group>

  <!-- Flat widget (ungrouped) -->
  <widget name="favourites" label="Favourites" type="videos">
    <path>favourites://</path>
  </widget>

  <!-- Custom widget (user-defined items) -->
  <widget name="custom" label="Custom Widget" type="custom" slot="widget" />
</widgets>
```

### Key Mappings

| v2 Element                                                | v3 Element                                                            |
| --------------------------------------------------------- | --------------------------------------------------------------------- |
| `<widget label="..." name="..." type="...">path</widget>` | `<widget name="..." label="..." type="..."><path>...</path></widget>` |
| `<widget-groupings>` → `<node label="...">`               | `<widgets>` → `<group name="..." label="...">`                        |
| `<widgetdefault labelID="...">`                           | `<item widget="...">` or `<defaults widget="...">`                    |
| `<content>video</content>`                                | `<content source="library" target="..." />`                            |

### Widget Types

Both v2 and v3 support: `movies`, `tvshows`, `episodes`, `musicvideos`, `albums`, `artists`, `songs`, `pictures`, `pvr`, `games`, `addons`

v3 adds: `custom` (user-defined item list), `sets` (movie sets)

***

## backgrounds.xml Migration

### v2 (in overrides.xml)

```xml
<overrides>
  <!-- Background options -->
  <background label="Movie Fanart">$INFO[Window(Home).Property(MovieFanart)]</background>
  <background label="Default" icon="special://skin/backgrounds/default.jpg">default-bg</background>

  <!-- Enable browsing with default path -->
  <backgroundBrowse default="special://skin/backgrounds/">True</backgroundBrowse>

  <!-- Set defaults -->
  <backgrounddefault labelID="movies">movie-fanart</backgrounddefault>
</overrides>
```

### v3 (backgrounds.xml)

```xml
<backgrounds>
  <!-- Property-based (info label) -->
  <background name="movie-fanart" label="Movie Fanart" type="property" visible="Library.HasContent(movies)">
    <path>$INFO[Window(Home).Property(MovieFanart)]</path>
    <icon>DefaultMovies.png</icon>
  </background>

  <!-- Static image -->
  <background name="default" label="Default" type="static">
    <path>special://skin/backgrounds/default.jpg</path>
    <icon>DefaultPicture.png</icon>
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

  <!-- Live (dynamic library content) -->
  <background name="live-movies" label="Random Movies" type="live" visible="Library.HasContent(movies)">
    <path>random movies</path>
  </background>

  <!-- Live playlist -->
  <background name="live-playlist" label="Live Playlist" type="live-playlist">
    <source label="Video Playlists">special://profile/playlists/video/</source>
  </background>

  <!-- Group -->
  <group name="library" label="Library Fanart" icon="DefaultVideo.png" visible="Library.HasContent(movies)">
    <background name="movie-fanart" label="Movie Fanart" type="property">
      <path>$INFO[Window(Home).Property(MovieFanart)]</path>
    </background>
  </group>
</backgrounds>
```

### Key Mappings

| v2 Element                                                 | v3 Element                                                                    |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `<background label="...">id</background>`                  | `<background name="..." label="..." type="..."><path>...</path></background>` |
| `<backgroundBrowse default="path">True</backgroundBrowse>` | `<background type="browse">` with `<source>` elements                         |
| `<backgrounddefault labelID="...">`                        | `<item background="...">` or `<defaults background="...">`                    |

### Background Types

| v2                   | v3                                                     |
| -------------------- | ------------------------------------------------------ |
| Implied from path    | `type="static"` - Single image file                    |
| Implied from `$INFO` | `type="property"` - Kodi info label                    |
| `<backgroundBrowse>` | `type="browse"` - User selects single image            |
| N/A                  | `type="multi"` - User selects folder for slideshow     |
| N/A                  | `type="playlist"` - Images from playlist               |
| N/A                  | `type="live"` - Dynamic library content                |
| N/A                  | `type="live-playlist"` - Dynamic content from playlist |

***

## properties.xml Migration

### v2 (in overrides.xml)

```xml
<overrides>
  <propertySettings property="widgetStyle" buttonID="350" title="Widget Style" />
  <property property="widgetStyle" label="Panel">Panel</property>
  <property property="widgetStyle" label="Wide" condition="widgetType=movies">Wide</property>
  <propertyfallback property="widgetStyle" attribute="widgetType" value="movies">Panel</propertyfallback>
</overrides>
```

### v3 (properties.xml)

```xml
<properties>
  <!-- Reusable option sets -->
  <includes>
    <include name="artTypes">
      <option value="Poster" label="Poster">
        <icon>poster.png</icon>
      </option>
      <option value="Landscape" label="Landscape">
        <icon>landscape.png</icon>
      </option>
    </include>
  </includes>

  <!-- Property definitions -->
  <property name="widgetStyle" type="options" requires="widget">
    <options>
      <option value="Panel" label="Panel" />
      <option value="Wide" label="Wide" condition="widgetType=movies" />
      <include content="artTypes" />
    </options>
  </property>

  <property name="hideLabels" type="toggle" />
  <property name="extraWidget" type="widget" />
  <property name="customBg" type="background" />

  <!-- Button mappings -->
  <buttons suffix="true">
    <button id="350" property="widgetStyle" title="Widget Style" showNone="true" showIcons="true" requires="widget" />
    <group suffix="false">
      <button id="360" property="hideLabels" title="Hide Labels" type="toggle" />
    </group>
  </buttons>

  <!-- Fallback values -->
  <fallbacks>
    <fallback property="widgetStyle">
      <when condition="widgetType=movies">Panel</when>
      <when condition="widgetType=tvshows">Wide</when>
      <default>Panel</default>
    </fallback>
  </fallbacks>
</properties>
```

### Key Mappings

| v2 Element                                                      | v3 Element                                                                             |
| --------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `<propertySettings property="..." buttonID="..." />`             | `<buttons><button id="..." property="..." /></buttons>`                                 |
| `<property property="..." label="...">value</property>`         | `<property name="..."><options><option value="..." label="..." /></options></property>` |
| `<propertyfallback property="..." attribute="..." value="...">` | `<fallbacks><fallback property="..."><when condition="...">`                           |

### Property Types

| Type              | v2                                 | v3                                |
| ----------------- | ---------------------------------- | --------------------------------- |
| Options           | `<property>` elements              | `type="options"` with `<options>` |
| Toggle            | `<propertySettings toggle="..." />` | `type="toggle"`                   |
| Widget picker     | Button 312                         | `type="widget"`                   |
| Background picker | Button 310                         | `type="background"`               |

***

## templates.xml Migration

v3 introduces a new template system. If your v2 skin used custom templates, you must rewrite them.

### v3 Template Features

#### Named Expressions

```xml
<expressions>
  <expression name="HasWidget">widgetPath</expression>
  <expression name="IsMovies">widgetType=movies</expression>
</expressions>
```

Use with `$EXP[HasWidget]` in controls.

#### Presets (Lookup Tables)

```xml
<presets>
  <preset name="WidgetDimensions">
    <values condition="widgetArt=Poster" width="200" height="300" />
    <values condition="widgetArt=Landscape" width="356" height="200" />
    <values width="200" height="200" />
  </preset>
</presets>
```

First matching condition wins. All matched row attributes become properties.

#### Property Groups

```xml
<propertyGroups>
  <propertyGroup name="widgetProps">
    <property name="path" from="widgetPath" />
    <property name="target" from="widgetTarget" />
    <var name="layout">
      <value condition="widgetStyle=Panel">panel</value>
      <value>list</value>
    </var>
    <preset content="WidgetDimensions" />
  </propertyGroup>
</propertyGroups>
```

Reference with `<propertyGroup content="widgetProps" />` in templates.

#### Dynamic Expressions

| Expression                | Description                            | Example                                                |
| ------------------------- | -------------------------------------- | ------------------------------------------------------ |
| `$PROPERTY[name]`         | Item property value                    | `$PROPERTY[widgetPath]`                                |
| `$PARENT[name]`           | Parent item property (items iteration) | `$PARENT[label]`                                       |
| `$EXP[name]`              | Named expression                       | `$EXP[HasWidget]`                                      |
| `$MATH[expr]`             | Arithmetic                             | `$MATH[index * 1000 + 100]`                            |
| `$IF[cond THEN a ELSE b]` | Conditional                            | `$IF[widgetLimit THEN $PROPERTY[widgetLimit] ELSE 25]` |

#### Multi-Output Templates

Single template generating multiple includes:

```xml
<template>
  <output include="widget1" idprefix="8011" />
  <output include="widget2" idprefix="8021" suffix=".2" />
  <condition>widgetPath</condition>
  <controls>
    <control type="panel" id="$PROPERTY[id]">
      <content>$PROPERTY[widgetPath]</content>
    </control>
  </controls>
</template>
```

The `suffix=".2"` transforms property reads (`widgetPath` → `widgetPath.2`) and conditions.

#### Submenu Items Iteration

Items templates iterate over submenu items. They are defined separately and referenced via insert markers:

```xml
<templates>
  <!-- Items template: defines what to generate for each submenu item -->
  <template items="widgets" source="widgets" filter="widgetArt=Poster">
    <var name="widgetInclude">
      <value condition="widgetArt=Poster">Widget_Poster</value>
      <value>Widget_Default</value>
    </var>

    <controls>
      <control type="group" id="$MATH[$PARENT[index] * 1000 + 600 + $PROPERTY[index]]">
        <include content="$PROPERTY[widgetInclude]">
          <param name="path">$PROPERTY[widgetPath]</param>
          <param name="parent">$PARENT[label]</param>
        </include>
      </control>
    </controls>
  </template>

  <!-- Regular template: uses insert marker to include items -->
  <template include="Widgets">
    <condition>widgetType=custom</condition>
    <controls>
      <control type="grouplist" id="$MATH[$PROPERTY[index] * 1000 + 400]">
        <skinshortcuts>visibility</skinshortcuts>

        <!-- Insert widgets here -->
        <skinshortcuts insert="widgets" />
      </control>
    </controls>
  </template>
</templates>
```

* `<template items="widgets">` - Defines an items template named "widgets"
* `source="widgets"` - Looks up submenu `{parent.name}.widgets`
* `filter` - Only include submenu items matching condition
* `<skinshortcuts insert="widgets" />` - Insert marker in regular templates
* `$PROPERTY[...]` - Submenu item properties
* `$PARENT[...]` - Parent item properties

#### Build Modes

| Mode                     | Usage                                                   |
| ------------------------ | ------------------------------------------------------- |
| `build="menu"` (default) | Iterate over menu items                                 |
| `build="list"`           | Iterate over explicit `<list><item>` elements           |
| `build="true"`           | No iteration, output controls once (with `$PARAM[...]`) |

***

## RunScript Parameters

| v2                           | v3                                      |
| ---------------------------- | --------------------------------------- |
| `type=manage&group=mainmenu` | `type=manage&menu=mainmenu`             |
| `type=buildxml&group=...`    | `type=buildxml` (no group param needed) |
| `type=resetall`              | `type=resetall` (unchanged)             |
| N/A                          | `type=clear&menu=mainmenu` (new)        |

### v2

```xml
<onclick>RunScript(script.skinshortcuts,type=manage,group=mainmenu)</onclick>
```

### v3

```xml
<onclick>RunScript(script.skinshortcuts,type=manage,menu=mainmenu)</onclick>
```

***

## Management Dialog Controls

### Unchanged Control IDs

| ID  | Function        |
| --- | --------------- |
| 211 | Menu items list |
| 301 | Add shortcut    |
| 302 | Delete shortcut |
| 303 | Move up         |
| 304 | Move down       |
| 305 | Edit label      |
| 306 | Edit icon       |
| 307 | Edit action     |
| 313 | Toggle disabled |
| 401 | Choose shortcut |
| 405 | Edit submenu    |

### Changed in v3

| ID  | v2 Function                         | v3 Function            |
| --- | ----------------------------------- | ---------------------- |
| 309 | Widget picker (deprecated, use 312) | Via subdialog system   |
| 310 | Background picker                   | Via subdialog system   |
| 311 | Thumbnail selector                  | Restore deleted item   |
| 312 | Widget picker                       | Reset item to defaults |

Widget and background pickers in v3 are configured via `<subdialog>` elements in menus.xml, not hardcoded IDs.

### Removed in v3

| ID      | v2 Function              |
| ------- | ------------------------ |
| 101-103 | Shortcut type selector   |
| 111     | Available shortcuts list |
| 308     | Restore shortcuts        |
| 404     | Set custom property      |

Remove these controls from your dialog XML.

***

## Window Properties

### Dialog Properties

| Property                   | v2  | v3                            |
| -------------------------- | --- | ----------------------------- |
| `groupname`                | ✓   | Renamed to `menuname`         |
| `groupDisplayName`         | ✓   | Removed                       |
| `menuname`                 | —   | ✓ (new, replaces `groupname`) |
| `allowWidgets`             | —   | ✓ (new)                       |
| `allowBackgrounds`         | —   | ✓ (new)                       |
| `allowSubmenus`            | —   | ✓ (new)                       |
| `skinshortcuts-hasdeleted` | —   | ✓ (new)                       |

### Home Window Properties (v3 only)

| Property               | Description             |
| ---------------------- | ----------------------- |
| `skinshortcuts-dialog` | Current subdialog mode  |
| `skinshortcuts-suffix` | Current property suffix |

***

## Property Name Changes

| v2           | v3            |
| ------------ | ------------- |
| `widgetName` | `widgetLabel` |
| All others   | Unchanged     |

***

## User Data Format

### v2: XML (Multiple Files)

```
{skin_id}_mainmenu.DATA.xml
{skin_id}_submenu.DATA.xml
```

### v3: JSON (Single File)

```json
{
  "menus": {
    "mainmenu": {
      "items": [
        {
          "name": "movies",
          "label": "Movies",
          "actions": [{"action": "ActivateWindow(Videos,videodb://movies/)", "condition": ""}],
          "icon": "DefaultMovies.png",
          "properties": {
            "widget": "recent-movies",
            "widgetPath": "videodb://recentlyaddedmovies/",
            "widgetType": "movies",
            "background": "movie-fanart"
          }
        }
      ],
      "removed": ["weather"]
    }
  }
}
```

User data is stored in:
`userdata/addon_data/script.skinshortcuts/{skin_id}.userdata.json`

***

## Migration Checklist

### Required Steps

- [ ] Create `shortcuts/menus.xml`
  
  - [ ] Define all menus (`<menu>` elements)
  - [ ] Define all submenus (`<submenu>` elements)
  - [ ] Create groupings for shortcut picker
  - [ ] Configure icon sources
  - [ ] Set up subdialogs if using multiple widgets
  - [ ] Configure action overrides if needed

- [ ] Update dialog XML
  
  - [ ] Remove controls 101-103 (shortcut type selector)
  - [ ] Remove control 111 (available shortcuts list)
  - [ ] Remove control 308 (restore shortcuts)
  - [ ] Remove control 404 (set custom property)
  - [ ] Update control 311 (now restores deleted items, not thumbnail selector)
  - [ ] Update control 312 (now resets item, not widget picker)
  - [ ] Configure widget/background pickers via `<subdialog>` in menus.xml

- [ ] Update RunScript calls
  
  - [ ] Change `group=` to `menu=` in all RunScript parameters

### Optional Steps

- [ ] Create `shortcuts/widgets.xml`
  
  - [ ] Define widget groups
  - [ ] Define individual widgets
  - [ ] Add dynamic content sources

- [ ] Create `shortcuts/backgrounds.xml`
  
  - [ ] Define background types
  - [ ] Set up browse sources
  - [ ] Configure groups

- [ ] Create `shortcuts/properties.xml`
  
  - [ ] Define property schemas
  - [ ] Set up button mappings
  - [ ] Configure fallback values

- [ ] Create `shortcuts/templates.xml` (if using custom includes)
  
  - [ ] Rewrite templates for v3 syntax
  - [ ] Set up expressions, presets, property groups
  - [ ] Configure multi-output if needed

### Testing

- [ ] Test menu management dialog opens
- [ ] Test adding/removing/reordering items
- [ ] Test widget picker
- [ ] Test background picker
- [ ] Test property buttons
- [ ] Test submenu editing
- [ ] Verify includes file generates correctly
- [ ] Test all generated includes display correctly in skin

***

## Related Documentation

* [Schema Reference](schema.md) - Complete XML element reference
* [Menus](skinning/menus.md) - Menu configuration details
* [Widgets](skinning/widgets.md) - Widget configuration details
* [Backgrounds](skinning/backgrounds.md) - Background configuration details
* [Properties](skinning/properties.md) - Property configuration details
* [Templates](skinning/templates.md) - Template system details
* [Conditions](skinning/conditions.md) - Condition syntax reference
