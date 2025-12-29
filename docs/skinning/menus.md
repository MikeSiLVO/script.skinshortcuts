# Menu Configuration

The `menus.xml` file defines menu structure, items, shortcut picker groupings, and dialog settings.

***

## Table of Contents

* [File Structure](#file-structure)
* [Menu Element](#menu-element)
* [Submenu Element](#submenu-element)
* [Item Element](#item-element)
* [Actions](#actions)
* [Defaults](#defaults)
* [Allow Settings](#allow-settings)
* [Protection](#protection)
* [Shortcut Groupings](#shortcut-groupings)
* [Icon Sources](#icon-sources)
* [Subdialogs](#subdialogs)
* [Action Overrides](#action-overrides)
* [Context Menu](#context-menu)

***

## File Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <!-- Main menus -->
  <menu name="mainmenu" container="9000">...</menu>
  <menu name="buttonmenu">...</menu>

  <!-- Submenus (only built when referenced) -->
  <submenu name="movies">...</submenu>

  <!-- Shortcut picker groupings -->
  <groupings>...</groupings>

  <!-- Icon picker sources -->
  <icons>...</icons>

  <!-- Subdialog definitions -->
  <dialogs>...</dialogs>

  <!-- Action overrides -->
  <overrides>...</overrides>

  <!-- Context menu toggle -->
  <contextmenu>true</contextmenu>
</menus>
```

***

## Menu Element

Defines a standalone menu that generates an include.

```xml
<menu name="mainmenu" container="9000">
  <defaults>...</defaults>
  <item name="movies">...</item>
  <item name="settings">...</item>
</menu>
```

### Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier. Generated include is `skinshortcuts-{name}` |
| `container` | No | List control ID for visibility conditions |

**Container binding:** When `container` is set, visibility conditions are generated for submenus and widgets based on focused item position.

***

## Submenu Element

Defines a menu that is only built when referenced by a parent item.

```xml
<submenu name="movies">
  <allow widgets="false" backgrounds="false" submenus="false" />
  <item name="all-movies">
    <label>All Movies</label>
    <action>ActivateWindow(Videos,videodb://movies/)</action>
  </item>
</submenu>
```

Submenus use the same structure as `<menu>`. The only difference is:

* `<menu>`: Always generates an include
* `<submenu>`: Only generates when an item has `submenu="{name}"`

Link a submenu to an item:

```xml
<item name="movies" submenu="movies">
  <label>Movies</label>
  <action>ActivateWindow(Videos,videodb://movies/)</action>
</item>
```

***

## Item Element

Defines a menu item.

```xml
<item name="movies" submenu="movies" required="true">
  <label>$LOCALIZE[342]</label>
  <label2>Video Library</label2>
  <action>ActivateWindow(Videos,videodb://movies/)</action>
  <icon>DefaultMovies.png</icon>
  <thumb>special://skin/extras/thumbs/movies.png</thumb>
  <visible>Library.HasContent(movies)</visible>
  <property name="customProp">value</property>
</item>
```

### Attributes

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `name` | Yes | - | Unique item identifier |
| `submenu` | No | - | Submenu name to link |
| `required` | No | `false` | If `true`, cannot be deleted |
| `visible` | No | - | Kodi condition for dialog visibility filtering (hides item in management dialog) |
| `widget` | No | - | Shorthand for `<property name="widget">` |
| `background` | No | - | Shorthand for `<property name="background">` |

### Child Elements

| Element | Required | Default | Description |
|---------|----------|---------|-------------|
| `<label>` | Yes | - | Display text. Supports `$LOCALIZE[id]` |
| `<label2>` | No | - | Secondary label |
| `<action>` | Yes | - | Action(s) to execute. Multiple allowed |
| `<icon>` | No | `DefaultShortcut.png` | Icon path |
| `<thumb>` | No | - | Thumbnail path |
| `<visible>` | No | - | Visibility condition for generated output |
| `<disabled>` | No | - | Set to `true` to gray out item |
| `<property>` | No | - | Custom property (requires `name` attribute) |
| `<protect>` | No | - | Protection rule |

### Two Types of Visibility

| Attribute/Element | Where Applied | Purpose |
|-------------------|---------------|---------|
| `visible="..."` (attribute on `<item>`) | Management dialog | Hides item from dialog when condition fails (e.g., hide playdisc when no disc drive) |
| `<visible>` (child element) | Generated include | Output as `<visible>` in the include file |

***

## Actions

### Single Action

```xml
<item name="movies">
  <label>Movies</label>
  <action>ActivateWindow(Videos,videodb://movies/)</action>
</item>
```

### Multiple Actions

Execute in sequence:

```xml
<item name="skin-settings">
  <label>Skin Settings</label>
  <action>Dialog.Close(all,true)</action>
  <action>ActivateWindow(SkinSettings)</action>
</item>
```

### Conditional Actions

Use the `condition` attribute for fallback behavior:

```xml
<item name="movies">
  <label>Movies</label>
  <action>ActivateWindow(Videos,videodb://movies/)</action>
  <action condition="!Library.HasContent(movies)">ActivateWindow(Videos,files)</action>
</item>
```

The first matching action executes. Unconditional actions always match.

***

## Defaults

Menu-level defaults apply to all items in the menu.

```xml
<menu name="mainmenu">
  <allow widgets="true" backgrounds="true" submenus="true" />
  <defaults>
    <action when="before">Dialog.Close(all,true)</action>
    <property name="widgetStyle">Panel</property>
  </defaults>
  <item .../>
</menu>
```

### Child Elements

| Element | Description |
|---------|-------------|
| `<action>` | Default actions for all items |
| `<property>` | Default property values |

The `<defaults>` element also supports `widget` and `background` attributes as shorthand:

```xml
<defaults widget="default-widget" background="default-bg">
  <property name="otherProp">value</property>
</defaults>
```

### Default Actions

```xml
<defaults>
  <action when="before">Dialog.Close(all,true)</action>
  <action when="after" condition="...">SetProperty(...)</action>
</defaults>
```

| Attribute | Values | Description |
|-----------|--------|-------------|
| `when` | `before`, `after` | When to run relative to item action |
| `condition` | Kodi condition | Only run when condition is true |

***

## Allow Settings

Controls which features are available in the management dialog. This is a direct child of `<menu>` or `<submenu>`, not inside `<defaults>`.

```xml
<menu name="mainmenu">
  <allow widgets="true" backgrounds="true" submenus="true" />
  ...
</menu>
```

| Attribute | Default | Description |
|-----------|---------|-------------|
| `widgets` | `true` | Allow widget assignment |
| `backgrounds` | `true` | Allow background assignment |
| `submenus` | `true` | Allow submenu editing |

These set window properties that your dialog skin can use for button visibility:

* `Window.Property(allowWidgets)` = `true` or `false`
* `Window.Property(allowBackgrounds)` = `true` or `false`
* `Window.Property(allowSubmenus)` = `true` or `false`

***

## Protection

Protect items from accidental changes.

### Prevent Deletion/Disabling

```xml
<item name="settings" required="true">
  <label>Settings</label>
  <action>ActivateWindow(Settings)</action>
</item>
```

Items with `required="true"` cannot be deleted or disabled. If a user previously deleted a required item, it will be automatically restored when the skinner adds the `required` attribute.

### Confirmation Dialog

```xml
<item name="skin-settings">
  <label>Skin Settings</label>
  <action>ActivateWindow(SkinSettings)</action>
  <protect type="all" heading="$LOCALIZE[19098]" message="$LOCALIZE[31377]" />
</item>
```

### `<protect>` Attributes

| Attribute | Default | Values | Description |
|-----------|---------|--------|-------------|
| `type` | `all` | `delete`, `action`, `all` | What to protect |
| `heading` | - | String | Dialog heading |
| `message` | - | String | Dialog message |

***

## Shortcut Groupings

Define shortcuts available in the picker dialog.

```xml
<groupings>
  <group name="common" label="Common Shortcuts" icon="DefaultShortcut.png">
    <shortcut name="movies" label="Movies" icon="DefaultMovies.png" type="Video">
      <action>ActivateWindow(Videos,videodb://movies/)</action>
    </shortcut>

    <shortcut name="playlists" label="Browse Playlists" icon="DefaultPlaylist.png" browse="videos" visible="Library.HasContent(movies)">
      <path>special://profile/playlists/video/</path>
    </shortcut>

    <group name="addons" label="Add-ons" condition="...">
      <!-- Nested group -->
    </group>

    <content source="playlists" target="videos" folder="Video Playlists" />
  </group>
</groupings>
```

### `<group>` Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier |
| `label` | Yes | Display label |
| `icon` | No | Group icon |
| `condition` | No | Property condition (evaluated against item properties) |
| `visible` | No | Kodi visibility condition (evaluated at runtime) |

### `<shortcut>` Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier |
| `label` | Yes | Display label |
| `icon` | No | Icon (default: `DefaultShortcut.png`) |
| `type` | No | Category label shown as secondary text |
| `condition` | No | Property condition |
| `visible` | No | Kodi visibility condition |
| `browse` | No | Target window for browse mode (`videos`, `music`, `pictures`, `programs`) |

### `<shortcut>` Child Elements

| Element | Description |
|---------|-------------|
| `<action>` | Action string (for action mode) |
| `<path>` | Content path (for browse mode) |

### Shortcut Modes

**Action mode:** Direct action string

```xml
<shortcut name="movies" label="Movies">
  <action>ActivateWindow(Videos,videodb://movies/)</action>
</shortcut>
```

**Browse mode:** Opens path in target window

```xml
<shortcut name="browse-videos" label="Browse Videos" browse="videos">
  <path>special://profile/playlists/video/</path>
</shortcut>
```

### Dynamic Content

Add dynamic content from system sources:

```xml
<content source="playlists" target="videos" folder="Video Playlists" />
<content source="addons" target="videos" />
<content source="favourites" />
<content source="sources" target="videos" />
```

| Attribute | Description |
|-----------|-------------|
| `source` | Content type: `playlists`, `addons`, `sources`, `favourites`, `pvr`, `commands`, `settings`, `library`, `nodes` |
| `target` | Media context: `videos`, `music`, `pictures`, `programs`, `tv`, `radio`. For `library` source, see [Library Target Values](widgets.md#library-target-values). For `nodes` source, see [Nodes Target Values](widgets.md#nodes-target-values) |
| `folder` | Wrap items in a folder with this label |
| `path` | Custom path override |
| `label` | Custom label for the content group |
| `icon` | Custom icon for the content group |
| `condition` | Property condition (evaluated against item properties) |
| `visible` | Kodi visibility condition (evaluated at runtime) |

### Playlist Filtering

When `source="playlists"`, the `target` attribute filters smart playlists (.xsp) by type:

| Target | Includes playlist types |
|--------|-------------------------|
| `video` | movies, tvshows, episodes, musicvideos |
| `music` | songs, albums, artists |
| (omitted) | All types including mixed |

### Playlist Action Choice

When the user selects a playlist shortcut, a dialog offers action choices:

* **Display** - Opens the playlist in the library view (ActivateWindow)
* **Play** - Plays the playlist immediately (PlayMedia)
* **Party Mode** - Starts party mode shuffle (music playlists only)

***

## Icon Sources

Define browse locations for the icon picker (button 306).

### Simple Mode

Single path:

```xml
<icons>special://skin/extras/icons/</icons>
```

### Advanced Mode

Multiple conditional sources:

```xml
<icons>
  <source label="Colored Icons" visible="Skin.HasSetting(UseColoredIcons)">
    special://skin/extras/icons/colored/
  </source>
  <source label="Monochrome Icons" visible="!Skin.HasSetting(UseColoredIcons)">
    special://skin/extras/icons/mono/
  </source>
  <source label="Browse..." icon="DefaultFolder.png">browse</source>
</icons>
```

| Attribute | Description |
|-----------|-------------|
| `label` | Display label in picker |
| `condition` | Property condition (evaluated against item properties) |
| `visible` | Kodi visibility condition (evaluated at runtime) |
| `icon` | Icon for this source |

Use `browse` as the path for free file browser.

***

## Subdialogs

Define subdialogs triggered by button clicks. Used for multi-widget support.

```xml
<dialogs>
  <subdialog buttonID="800" mode="widget1" setfocus="309">
    <onclose condition="widgetType=custom" action="menu" menu="{item}.customwidget" />
  </subdialog>
  <subdialog buttonID="801" mode="widget2" setfocus="309" suffix=".2">
    <onclose condition="widgetType.2=custom" action="menu" menu="{item}.customwidget.2" />
  </subdialog>
</dialogs>
```

### `<subdialog>` Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `buttonID` | Yes | Button ID that triggers this subdialog |
| `mode` | Yes | Value set in `Window(Home).Property(skinshortcuts-dialog)` |
| `setfocus` | No | Control ID to focus when subdialog opens |
| `suffix` | No | Property suffix for widget slots (e.g., `.2`). Set in `Window(Home).Property(skinshortcuts-suffix)` |

### `<onclose>` Attributes

| Attribute | Description |
|-----------|-------------|
| `action` | Action type: `menu` |
| `menu` | Menu name for `action="menu"`. Supports `{item}` placeholder |
| `condition` | Condition evaluated against item properties |

***

## Action Overrides

Replace deprecated or changed actions:

```xml
<overrides>
  <action replace="ActivateWindow(favourites)">ActivateWindow(favouritesbrowser)</action>
</overrides>
```

| Attribute | Description |
|-----------|-------------|
| `replace` | Action string to find |

The element text is the replacement action.

***

## Context Menu

Enable or disable context menu on items:

```xml
<contextmenu>true</contextmenu>
```

Default: `true`. Set to `false`, `no`, or `0` to disable.

***

## Quick Navigation

[Back to Top](#menu-configuration)

**Sections:** [File Structure](#file-structure) | [Menu Element](#menu-element) | [Submenu Element](#submenu-element) | [Item Element](#item-element) | [Actions](#actions) | [Defaults](#defaults) | [Allow Settings](#allow-settings) | [Protection](#protection) | [Shortcut Groupings](#shortcut-groupings) | [Icon Sources](#icon-sources) | [Subdialogs](#subdialogs) | [Action Overrides](#action-overrides) | [Context Menu](#context-menu)

**Related Docs:** [Widgets](widgets.md) | [Backgrounds](backgrounds.md) | [Properties](properties.md) | [Templates](templates.md) | [Conditions](conditions.md)
