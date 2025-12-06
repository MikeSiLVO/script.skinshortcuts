# Getting Started

## Table of Contents

- [File Setup](#file-setup)
- [Menu Definition](#menu-definition)
- [Widget Definition](#widget-definition)
- [Background Definition](#background-definition)
- [Building Includes](#building-includes)
- [Display Menu](#display-menu)
- [Available Properties](#available-properties)

## File Setup

Create `shortcuts/` folder in skin root:

```
skin.name/
└── shortcuts/
    ├── menus.xml        # Menu structure and items
    ├── widgets.xml      # Widget definitions
    ├── backgrounds.xml  # Background options
    ├── properties.xml   # Property definitions for management dialog
    └── templates.xml    # Template definitions (optional)
```

## Menu Definition

`shortcuts/menus.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <!-- Main menu -->
  <menu name="mainmenu" container="9000">
    <defaults>
      <allow widgets="true" backgrounds="true" submenus="true"/>
    </defaults>

    <item name="movies" submenu="movies">
      <label>$LOCALIZE[20342]</label>
      <action>ActivateWindow(Videos,videodb://movies/titles/,return)</action>
      <icon>DefaultMovies.png</icon>
      <visible>Library.HasContent(movies)</visible>
    </item>

    <item name="tvshows" submenu="tvshows">
      <label>$LOCALIZE[20343]</label>
      <action>ActivateWindow(Videos,videodb://tvshows/titles/,return)</action>
      <icon>DefaultTVShows.png</icon>
      <visible>Library.HasContent(tvshows)</visible>
    </item>

    <item name="settings" required="true">
      <label>$LOCALIZE[10004]</label>
      <action>ActivateWindow(Settings)</action>
      <icon>DefaultAddonProgram.png</icon>
    </item>
  </menu>

  <!-- Submenu for movies -->
  <submenu name="movies">
    <defaults>
      <allow widgets="false" backgrounds="false" submenus="false"/>
    </defaults>

    <item name="all-movies">
      <label>$LOCALIZE[342]</label>
      <action>ActivateWindow(Videos,videodb://movies/titles/,return)</action>
      <icon>DefaultMovies.png</icon>
    </item>

    <item name="recent-movies">
      <label>$LOCALIZE[20386]</label>
      <action>ActivateWindow(Videos,videodb://recentlyaddedmovies/,return)</action>
      <icon>DefaultRecentlyAddedMovies.png</icon>
    </item>
  </submenu>
</menus>
```

**Key differences:**
- `<menu>` creates a standalone include (e.g., `skinshortcuts-mainmenu`)
- `<submenu>` only builds when referenced by a parent item's `submenu` attribute
- `<defaults>` contains `<allow>` settings and default actions/properties

## Widget Definition

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

  <widget name="recent-episodes" label="$LOCALIZE[20387]" type="episodes">
    <path>videodb://recentlyaddedepisodes/</path>
    <target>videos</target>
    <icon>DefaultRecentlyAddedEpisodes.png</icon>
    <condition>Library.HasContent(tvshows)</condition>
  </widget>

  <!-- Widget groupings for picker dialog -->
  <groupings>
    <group name="movies" label="Movies">
      <widget name="recent" label="Recently Added" type="movies">
        <path>videodb://recentlyaddedmovies/</path>
        <target>videos</target>
      </widget>
    </group>
  </groupings>
</widgets>
```

## Background Definition

`shortcuts/backgrounds.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
  <!-- Property-based (info label) -->
  <background name="movie-fanart" label="Movie Fanart" type="property">
    <path>$INFO[Container(9000).ListItem.Art(fanart)]</path>
    <icon>DefaultMovies.png</icon>
    <condition>Library.HasContent(movies)</condition>
  </background>

  <!-- Browse for single image -->
  <background name="custom-image" label="Custom Image" type="browse">
    <icon>DefaultPicture.png</icon>
    <source label="Skin Backgrounds">special://skin/backgrounds/</source>
    <source label="Browse...">browse</source>
  </background>

  <!-- Browse for folder (slideshow) -->
  <background name="custom-folder" label="Image Folder" type="multi">
    <icon>DefaultFolder.png</icon>
    <source label="Browse...">browse</source>
  </background>
</backgrounds>
```

## Building Includes

Trigger a rebuild:

```xml
<onclick>RunScript(script.skinshortcuts,type=buildxml)</onclick>
```

Or with force rebuild:

```xml
<onclick>RunScript(script.skinshortcuts,type=buildxml&amp;force=true)</onclick>
```

Output is written to `script-skinshortcuts-includes.xml` in the skin's resolution folder(s).

## Display Menu

Use the generated include in your skin:

```xml
<control type="list" id="9000">
  <itemlayout>
    <control type="image">
      <texture>$INFO[ListItem.Icon]</texture>
    </control>
    <control type="label">
      <label>$INFO[ListItem.Label]</label>
    </control>
  </itemlayout>
  <focusedlayout>
    <!-- focus styling -->
  </focusedlayout>
  <content>
    <include>skinshortcuts-mainmenu</include>
  </content>
</control>
```

Include naming: `skinshortcuts-{menu_name}`

## Available Properties

Properties available on menu items via `ListItem.Property(name)`:

| Property | Description |
|----------|-------------|
| `id` | Item's numeric ID (1-based position) |
| `name` | Item's name attribute |
| `menu` | Parent menu's name |
| `path` | Primary action |
| `submenuVisibility` | Submenu name (if linked) |
| `hasSubmenu` | "True" if item has submenu |

### Widget Properties

| Property | Description |
|----------|-------------|
| `widget` | Widget ID |
| `widgetPath` | Widget content path |
| `widgetType` | Widget content type |
| `widgetTarget` | Widget target window |
| `widgetName` | Widget display name |

### Background Properties

| Property | Description |
|----------|-------------|
| `background` | Background ID |
| `backgroundPath` | Background image path |
| `backgroundName` | Background display name |

### Custom Properties

Any custom properties set via `<property name="X">` on items or through the management dialog are available as `ListItem.Property(X)`.
