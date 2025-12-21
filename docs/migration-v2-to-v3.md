# Skin Shortcuts v2 to v3 Migration Cheat Sheet

**v3 is a complete rewrite and is NOT backward compatible with v2.**

***

## Quick Reference: File Changes

| v2 | v3 | Notes |
|----|----|----|
| `overrides.xml` (monolithic) | Split into multiple files | See below |
| User XML files | `{skin_dir}.userdata.json` | JSON format |

### New File Structure

```
shortcuts/
├── menus.xml        (required)
├── widgets.xml      (optional)
├── backgrounds.xml  (optional)
├── properties.xml   (optional)
└── templates.xml    (optional)
```

***

## menus.xml (replaces most of overrides.xml)

### v2

```xml
<overrides>
  <group name="common">
    <shortcut label="Movies">ActivateWindow(Videos,videodb://movies/)</shortcut>
  </group>
  <propertydefault labelID="movies">widget:recent-movies</propertydefault>
  <widgetdefault labelID="movies">recent-movies</widgetdefault>
</overrides>
```

### v3

```xml
<menus>
  <menu name="mainmenu">
    <defaults widget="recent-movies"/>
    <item name="movies" submenu="movies" widget="recent-movies">
      <label>$LOCALIZE[20342]</label>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
      <icon>DefaultMovies.png</icon>
    </item>
  </menu>

  <groupings>
    <group name="common" label="Common">
      <shortcut name="movies" label="Movies" icon="DefaultMovies.png">
        <action>ActivateWindow(Videos,videodb://movies/)</action>
      </shortcut>
    </group>
  </groupings>
</menus>
```

### Key Changes

| v2 | v3 |
|----|----|
| `<group>` (top-level) | `<groupings>` → `<group>` |
| `<shortcut label="...">action</shortcut>` | `<shortcut name="..." label="..."><action>...</action></shortcut>` |
| `<widgetdefault>` | `<item widget="...">` or `<defaults widget="...">` |
| `<backgrounddefault>` | `<item background="...">` or `<defaults background="...">` |
| `<propertydefault>` | `<defaults><property name="...">` |
| N/A | `<submenu name="...">` for explicit submenus |

***

## widgets.xml (new file)

### v2 (in overrides.xml)

```xml
<widget label="Recent Movies" name="recent-movies" type="movies">
  special://videoplaylists/RecentMovies.xsp
</widget>
<widget-groupings>
  <node label="Movies">
    <widget>recent-movies</widget>
  </node>
</widget-groupings>
```

### v3

```xml
<widgets>
  <group name="movies" label="Movies" icon="DefaultMovies.png">
    <widget name="recent" label="Recently Added" type="movies">
      <path>videodb://recentlyaddedmovies/</path>
    </widget>
    <content source="playlists" target="videos"/>
  </group>
</widgets>
```

### Widget Types

`movies`, `tvshows`, `episodes`, `musicvideos`, `albums`, `artists`, `songs`, `pictures`, `pvr`, `games`, `addons`, `custom`

***

## backgrounds.xml (new file)

### v2 (in overrides.xml)

```xml
<background label="Movie Fanart">$INFO[Window(Home).Property(MovieFanart)]</background>
<backgroundBrowse>True</backgroundBrowse>
```

### v3

```xml
<backgrounds>
  <background name="movie-fanart" label="Movie Fanart" type="property">
    <path>$INFO[Window(Home).Property(MovieFanart)]</path>
  </background>

  <background name="custom" label="Custom" type="browse">
    <source label="Browse...">browse</source>
  </background>
</backgrounds>
```

### Background Types

| Type | Description |
|------|-------------|
| `static` | Single image file |
| `property` | Kodi info label |
| `browse` | User selects image |
| `multi` | User selects folder |
| `playlist` | Images from playlist |
| `live` | Dynamic library content |

***

## properties.xml (new file)

### v2 (in overrides.xml)

```xml
<propertySettings property="widgetStyle" buttonID="350" title="Style"/>
<property property="widgetStyle" label="Panel">Panel</property>
<propertyfallback property="widgetStyle" attribute="widgetType" value="movies">Panel</propertyfallback>
```

### v3

```xml
<properties>
  <property name="widgetStyle" type="options">
    <options>
      <option value="Panel" label="Panel"/>
      <option value="Wide" label="Wide" condition="widgetType=movies"/>
    </options>
  </property>

  <buttons>
    <button id="350" property="widgetStyle" title="Style"/>
  </buttons>

  <fallbacks>
    <fallback property="widgetStyle">
      <when condition="widgetType=movies">Panel</when>
      <default>Panel</default>
    </fallback>
  </fallbacks>
</properties>
```

### Property Types

| Type | Behavior |
|------|----------|
| `options` | Select from list |
| `toggle` | True/empty toggle |
| `widget` | Widget picker |
| `background` | Background picker |

***

## RunScript Parameters

| v2 | v3 |
|----|----|
| `group=mainmenu` | `menu=mainmenu` |
| `type=buildxml` | `type=buildxml` (unchanged) |
| `type=resetall` | `type=resetall` (unchanged) |
| N/A | `type=clear&menu=...` (new) |

***

## Management Dialog Controls

### Unchanged

| ID | Function |
|----|----------|
| 211 | Menu items list |
| 301-307 | Add/Delete/Move/Label/Icon/Action |
| 309 | Widget picker |
| 310 | Background picker |
| 313 | Toggle disabled |
| 401 | Choose shortcut |
| 405 | Edit submenu |

### Removed in v3

| ID | v2 Function |
|----|-------------|
| 101-103 | Shortcut type selector |
| 111 | Available shortcuts list |
| 308 | Restore shortcuts |
| 311 | Thumbnail selector |
| 404 | Set custom property |

***

## Window Properties (on dialog)

| Property | Description |
|----------|-------------|
| `groupname` | Current menu ID |
| `allowWidgets` | Widgets enabled |
| `allowBackgrounds` | Backgrounds enabled |
| `allowSubmenus` | Submenus enabled |
| `skinshortcuts-hasdeleted` | Has deleted items |

### Home Window Properties

| Property | Description |
|----------|-------------|
| `skinshortcuts-dialog` | Subdialog mode |
| `skinshortcuts-suffix` | Property suffix |

***

## Property Name Changes

| v2 | v3 |
|----|----|
| `widgetName` | `widgetLabel` |
| All others | Unchanged |

***

## User Data Format

### v2: XML (skin-specific format)

### v3: JSON

```json
{
  "menus": {
    "mainmenu": {
      "items": [
        {
          "name": "movies",
          "label": "Movies",
          "actions": [{"action": "...", "condition": ""}],
          "properties": {"widget": "recent-movies"}
        }
      ],
      "removed": ["weather"]
    }
  }
}
```

***

## Migration Checklist

* [ ] Create `menus.xml` with menu/submenu/groupings structure
* [ ] Move widgets to `widgets.xml`
* [ ] Move backgrounds to `backgrounds.xml`
* [ ] Move properties/buttons/fallbacks to `properties.xml`
* [ ] Update dialog XML (remove controls 101-103, 111, 308, 311, 404)
* [ ] Change `group=` to `menu=` in RunScript calls
* \[ ] Test all pickers and property buttons
* \[ ] Verify includes output matches expectations
