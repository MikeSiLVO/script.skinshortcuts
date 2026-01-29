# Menu Configuration

The `menus.xml` file defines menu structure, items, shortcut picker groupings, and dialog settings.

---

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

---

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

---

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
| `controltype` | No | Output as `<control type="X">` instead of `<item>` (e.g., `button`) |
| `id` | No | Starting control ID for `controltype` menus (default: 1) |

**Container binding:** When `container` is set, visibility conditions are generated for submenus and widgets based on focused item position.

**Control type menus:** When `controltype="button"`, items are output as `<control type="button">` elements instead of `<item>` elements. Use this for menus displayed in grouplists where you need individual button controls. Properties are not included in control output.

**Control IDs:** Use `id` to set the starting control ID for `controltype` menus. For example, `id="8000"` outputs controls with IDs 8000, 8001, 8002, etc. This avoids conflicts with other controls in the window. Ignored for regular item menus.

---

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

---

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

### Multiple Visibility Conditions

Multiple `<visible>` elements are combined with `+` (AND in Kodi):

```xml
<item name="sleep-timer">
  <label>Sleep Timer</label>
  <action>ActivateWindow(SleepTimerDialog)</action>
  <visible>System.CanPowerDown</visible>
  <visible>!System.HasAlarm(shutdowntimer)</visible>
</item>
```

Output:

```xml
<visible>System.CanPowerDown + !System.HasAlarm(shutdowntimer)</visible>
```

---

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

---

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
| `<skinshortcuts>` | Include reference (for controltype menus) |

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

### Include References

For `controltype` menus, insert include references into the output:

```xml
<defaults>
  <skinshortcuts include="ButtonTextures" />
  <action when="before">BeforeAction()</action>
  <action when="after">AfterAction()</action>
  <skinshortcuts include="ButtonExtras" condition="SomeCondition" />
</defaults>
```

| Attribute | Required | Description |
|-----------|----------|-------------|
| `include` | Yes | Name of include to reference |
| `condition` | No | Condition attribute on the output include element |

**Position matters:** Includes placed before `<action>` elements appear before onclick in output. Includes placed after appear after onclick.

Output:
```xml
<control type="button" id="1">
  <label>...</label>
  <include>ButtonTextures</include>
  <onclick>BeforeAction()</onclick>
  <onclick>ItemAction()</onclick>
  <onclick>AfterAction()</onclick>
  <include condition="SomeCondition">ButtonExtras</include>
</control>
```

Include references can also be added per-item:

```xml
<item name="special">
  <label>Special Button</label>
  <skinshortcuts include="BeforeStuff" />
  <action>SpecialAction()</action>
  <skinshortcuts include="AfterStuff" />
</item>
```

---

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

* `Window.Property(disableWidgets)` = `true` if disabled, empty if allowed
* `Window.Property(disableBackgrounds)` = `true` if disabled, empty if allowed
* `Window.Property(disableSubmenus)` = `true` if disabled, empty if allowed

> **See also:** [Management Dialog](management-dialog.md) for using these properties in your dialog skin

---

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

---

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
| `target` | Media context (see [Content Target Reference](#content-target-reference) below) |
| `folder` | Wrap items in a folder with this label |
| `path` | Custom path override |
| `label` | Label for the created menu item (used with `addons` source, see below) |
| `icon` | Custom icon |
| `condition` | Property condition (evaluated against item properties) |
| `visible` | Kodi visibility condition (evaluated at runtime) |

### Addon Browse Placeholder

For `source="addons"`, a "Create menu item to here" option appears at the top of the picker. This lets users create a shortcut to the addon category itself (e.g., "Video add-ons") even when no addons are installed.

The `label` attribute sets the menu item label when the user selects this option:

```xml
<group name="video-addons" label="$LOCALIZE[1037]" icon="DefaultAddonVideo.png">
    <content source="addons" label="$LOCALIZE[1037]" target="videos" />
</group>
```

| User action | Result |
|-------------|--------|
| Selects "Create menu item to here" | Menu item labeled "Video add-ons" ($LOCALIZE[1037]) |
| Selects a specific addon | Menu item labeled with addon name |

Without the `label` attribute, the menu item defaults to "Create menu item to here".

### Content Target Reference

Valid `target` values depend on the `source` attribute. Values are based on Kodi's JSON-RPC API and window names.

| Source | Valid Targets | Notes |
|--------|---------------|-------|
| `addons` | `video`, `videos`, `audio`, `music`, `image`, `pictures`, `executable`, `programs`, `game`, `games` | JSON-RPC values (`video`, `audio`, `image`, `executable`, `game`) and window names (`videos`, `music`, `pictures`, `programs`, `games`) both accepted |
| `sources` | `video`, `music`, `pictures`, `files`, `programs` | Matches Kodi's Files.Media values |
| `playlists` | `video`, `music` | Matches playlist directory names |
| `nodes` | `video`, `music` | Library node types |
| `pvr` | `tv`, `radio` | PVR channel types |
| `library` | See [Library Target Values](widgets.md#library-target-values) | Genre, year, studio, tag, actor queries |
| `favourites` | (none) | No target needed |
| `commands` | (none) | No target needed |
| `settings` | (none) | No target needed |

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

### User Input

Allow users to enter custom values via keyboard:

```xml
<input label="Custom action" type="text" for="action" />
```

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `label` | Yes | - | Display label in picker |
| `type` | No | `text` | Input method: `text`, `numeric`, `ipaddress`, `password` |
| `for` | No | `action` | What the value becomes: `action`, `label`, `path` |
| `condition` | No | - | Property condition |
| `visible` | No | - | Kodi visibility condition |
| `icon` | No | `DefaultFile.png` | Icon in picker |

### Browse Into Addons

When a shortcut has a browsable path (`plugin://` or `addons://`), selecting it opens a directory browser instead of immediately selecting. Users can navigate into subdirectories and select "Create menu item to here" to use the current location.

> **See also:** [Conditions](conditions.md) for `condition` and `visible` attribute syntax

---

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

---

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

> **See also:**
> - [Management Dialog](management-dialog.md#subdialogs) for implementing subdialog UI
> - [Templates - Dynamic Widgets Pattern](templates.md#dynamic-widgets-pattern) for using subdialogs with items templates

---

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

---

## Context Menu

Enable or disable context menu on items:

```xml
<contextmenu>true</contextmenu>
```

Default: `true`. Set to `false`, `no`, or `0` to disable.

---

[↑ Top](#menu-configuration) · [Skinning Docs](index.md)
