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

  <!-- Context menu settings -->
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
| `build` | No | Build mode: `true` (default) or `auto`. When `auto`, only built if another menu item's action matches the `action` attribute |
| `action` | No | Action string for `build="auto"`. Menu is built when any item in another menu has this action |
| `type` | No | Menu type. `widgets` puts the dialog in [widget mode](widgets.md#widget-menus) |
| `submenuPath` | No | `all` emits the numbered `submenuPath.N` tail for widget submenus under this menu (see [Built-in Properties](builtin-properties.md#submenu-widget-path)) |
| `template_only` | No | `submenu` skips the combined `skinshortcuts-{name}-submenu` include for this menu. Distinct from `standalone`, which controls the per-template include on a `<submenu>` |

**Conditional building:** Use `build="auto"` with `action` for menus that serve specific windows (e.g., hub windows). The menu include is only generated when a menu item elsewhere uses the matching action:

```xml
<menu name="movie-hub" build="auto" action="ActivateWindow(1111)">
  <item name="recent">...</item>
</menu>
```

If no item in any other menu has `ActivateWindow(1111)` as its action, `skinshortcuts-movie-hub` is not generated. The match is case-insensitive.

**Container binding:** When `container` is set, visibility conditions are generated for submenus and widgets based on focused item position.

**Control type menus:** When `controltype="button"`, items are output as `<control type="button">` elements instead of `<item>` elements. Use this for menus displayed in grouplists where you need individual button controls. Properties are not included in control output.

**Control IDs:** Use `id` to set the starting control ID for `controltype` menus. For example, `id="8000"` outputs controls with IDs 8000, 8001, 8002, etc. Ignored for regular item menus.

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

Submenus use the same structure as `<menu>` (including all attributes). The only difference is:

* `<menu>`: Always generates an include (unless `build="auto"`)
* `<submenu>`: Only generates when an item has `submenu="{name}"`

The `type="widgets"` attribute is commonly used on submenus for per-item widget lists. See [Widget Menus](widgets.md#widget-menus).

### Attributes

In addition to the attributes shared with `<menu>`:

| Attribute | Default | Description |
|-----------|---------|-------------|
| `standalone` | `true` | When `false`, the per-template `skinshortcuts-{name}` include is not emitted. Submenu items still appear in the combined `skinshortcuts-{menu}-submenu` include. Use this when your skin only consumes submenus through the combined include and you want a cleaner generated output. |

`build`, `action` and `template_only` are only acted on for `<menu>`, so setting them here does nothing.

Link a submenu to an item:

```xml
<item name="movies" submenu="movies">
  <label>Movies</label>
  <action>ActivateWindow(Videos,videodb://movies/)</action>
</item>
```

### Auto-Link by Shortcut Name

When a user picks a shortcut, if a `<submenu>` shares its `name`, that submenu is attached to the new item automatically. No matching `<item submenu="...">` needs to exist in `<menu>`.

```xml
<shortcut name="movies" label="$LOCALIZE[342]" icon="DefaultMovies.png">
  <action>ActivateWindow(Videos,videodb://movies/titles/,return)</action>
</shortcut>

<submenu name="movies">
  <item name="recent">
    <label>$LOCALIZE[20387]</label>
    <action>ActivateWindow(Videos,videodb://recentlyaddedmovies/,return)</action>
  </item>
</submenu>
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
| `visible` | No | - | Kodi condition evaluated at config load (build time, inside Kodi). When it fails the item is omitted from both the management dialog and the generated include |
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
| `visible="..."` (attribute on `<item>`) | Config load (build time) | Omits the item from both the dialog and the generated include when the condition fails (e.g., hide playdisc when no disc drive) |
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

Each action is emitted as a separate `<onclick>` carrying its condition; Kodi runs every onclick whose condition passes, in output order (conditional actions first, then unconditional). For true fallback behavior, gate the primary action with a complementary condition so only one onclick fires.

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
  <item name="movies">...</item>
</menu>
```

### Child Elements

| Element | Description |
|---------|-------------|
| `<action>` | Default actions for all items |
| `<property>` | Default property values |
| `<skinshortcuts>` | Include reference inserted into item output (works for both regular item menus and controltype menus) |

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

Insert include references into the output (works for both regular item menus and controltype menus):

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

Items with `required="true"` cannot be deleted or disabled. Adding `required` to a deleted item also restores it.

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
| `type` | `all` | `delete`, `action`, `disable`, `all` | What to protect (`all` covers delete + action + disable) |
| `heading` | - | String | Dialog heading |
| `message` | - | String | Dialog message |

---

## Shortcut Groupings

Define shortcuts available in the picker dialog. The script provides none of its own, so the picker holds exactly what is defined here. [Starter Configuration](starter.md) has a full set to paste in and cut down.

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

### Menu-Specific Groupings

Use the `menu` attribute on `<groupings>` to define entirely different shortcut choices for a specific menu. A menu-specific `<groupings>` completely replaces the default when editing that menu.

```xml
<!-- Default groupings (used by any menu without a specific match) -->
<groupings>
  <group name="common" label="Common Shortcuts">
    ...
  </group>
</groupings>

<!-- Replaces default groupings when editing powermenu -->
<groupings menu="powermenu">
  <group name="power" label="Power Options">
    ...
  </group>
</groupings>
```

For finer control, use `visible` on individual `<group>` elements to show/hide groups based on which menu is being edited:

```xml
<groupings>
  <group name="common" label="Common Shortcuts">
    ...
  </group>
  <group name="power-only" label="Power Options" visible="String.IsEqual(Window.Property(menuname),powermenu)">
    ...
  </group>
</groupings>
```

### `<group>` Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier |
| `label` | Yes (unless `flat="true"`) | Display label for the folder header |
| `icon` | No | Group icon |
| `condition` | No | Property condition (evaluated against item properties) |
| `visible` | No | Kodi visibility condition (evaluated at runtime) |
| `flat` | No | When `true`, children appear inline at parent level instead of inside a folder |

### Flat Groups

A group with `flat="true"` has no folder header. Its children render at the parent level when the group's `condition` and `visible` both pass. Useful when one set of shortcuts should appear in some contexts and another set in others, without putting visibility conditions on every shortcut.

```xml
<groupings>
  <group name="power-shortcuts" flat="true" visible="String.IsEqual(Window.Property(menuname),powermenu)">
    <shortcut name="shutdown" label="$LOCALIZE[13005]" icon="DefaultShortcut.png">
      <action>ShutDown()</action>
    </shortcut>
    <shortcut name="reboot" label="$LOCALIZE[13013]" icon="DefaultShortcut.png">
      <action>Reboot</action>
    </shortcut>
  </group>
</groupings>
```

`label` and `icon` are unused when `flat="true"` and may be omitted.

For pickers invoked directly via `RunScript`, paired `prop=NAME,value=VALUE` arguments set a window property for the picker's lifetime and clear it on close; useful for driving flat group visibility from a specific button context. See [Window Property Pass-Through](management-dialog.md#window-property-pass-through).

### `<shortcut>` Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier |
| `label` | Yes | Display label |
| `icon` | No | Icon (default: `DefaultShortcut.png`) |
| `type` | No | Category label shown as secondary text |
| `condition` | No | Property condition |
| `visible` | No | Hides the shortcut from the picker when this Kodi condition is false |
| `browse` | No | Target window for browse mode (`videos`, `music`, `pictures`, `programs`) |

### `<shortcut>` Child Elements

| Element | Description |
|---------|-------------|
| `<action>` | Action string (for action mode). Multiple allowed. Supports `primary="true"` to set which action is used for display properties (defaults to the last action) |
| `<path>` | Content path (for browse mode) |
| `<visible>` | Kodi visibility condition baked into the resulting menu item when this shortcut is picked. Multiple elements are joined with ` + ` |

The attribute and child element are independent: the attribute gates picker visibility, the child element travels with the picked item.

```xml
<shortcut name="cancel-alarm" label="$LOCALIZE[20151]" icon="...">
  <action>CancelAlarm(shutdowntimer)</action>
  <visible>System.HasAlarm(shutdowntimer)</visible>
</shortcut>
```

### Shortcut Modes

**Action mode:** Direct action string

```xml
<shortcut name="movies" label="Movies">
  <action>ActivateWindow(Videos,videodb://movies/)</action>
</shortcut>
```

**Multiple actions:** Shortcuts can have multiple `<action>` elements. All actions are applied when the user picks the shortcut. The `action` and `path` listitem properties use the last action by default.

```xml
<shortcut name="movie-hub" label="Movie Hub">
  <action>SetProperty(HubMode,movies,Home)</action>
  <action>ActivateWindow(1111)</action>
</shortcut>
```

Use `primary="true"` to explicitly control which action is used for the display properties:

```xml
<shortcut name="movie-hub" label="Movie Hub">
  <action>SetProperty(HubMode,movies,Home)</action>
  <action primary="true">ActivateWindow(1111)</action>
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
<content source="addons" target="executable" />
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

The row always reads "Create menu item to here", but the label and icon it commits come from the `<content>` element, so the menu item can name itself:

```xml
<group name="video-addons" label="$LOCALIZE[1037]" icon="DefaultAddonVideo.png">
    <content source="addons" label="$LOCALIZE[1037]" target="videos" />
</group>
```

| User action | Result |
|-------------|--------|
| Selects "Create menu item to here" | Menu item labeled "Video add-ons" ($LOCALIZE[1037]) |
| Selects a specific addon | Menu item labeled with addon name |

The label falls back through `label`, then `folder`, then the enclosing group's label, and the icon through `icon` then the group's icon. Set nothing anywhere and the menu item is labeled "Create menu item to here" with a folder icon.

### Content Target Reference

Valid `target` values depend on the `source` attribute. Values are based on Kodi's JSON-RPC API and window names.

| Source | Valid Targets | Notes |
|--------|---------------|-------|
| `addons` | `video`, `videos`, `audio`, `music`, `image`, `pictures`, `executable`, `programs`, `game`, `games` | JSON-RPC values (`video`, `audio`, `image`, `executable`, `game`) and window names (`videos`, `music`, `pictures`, `programs`, `games`) both accepted |
| `sources` | `video`, `music`, `pictures`, `files`, `programs` | Matches Kodi's Files.Media values |
| `playlists` | `video`, `music` | Matches playlist directory names |
| `nodes` | `video`, `music`, `library` | Library node types; `library` shows Videos and Music as two browsable entries to drill into |
| `pvr` | `tv`, `radio` | PVR channel types |
| `library` | See [Library Target Values](widgets.md#library-target-values) | Genre, year, studio, tag, actor queries |
| `favourites` | (none) | No target needed |
| `commands` | (none) | No target needed |
| `settings` | (none) | No target needed |

#### `nodes` and `sources` overlap for music

Kodi's music library has a built-in "Sources" node, so `source="nodes" target="music"` lists it alongside Genres, Artists, and the rest. That node opens Kodi's database view of scanned sources. `source="sources" target="music"` is a separate feature: it lists each configured media source as its own browsable shortcut. The video library has no equivalent node, so this only comes up for music. A skin that offers both produces two similarly named entries with different behaviour; pick whichever fits the menu, or expose both deliberately.

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

### Browse Into

A shortcut is only browsable in the picker when it explicitly opts in via the `browse` attribute combined with a `<path>` element. Selecting a browsable shortcut opens a directory browser so users can pick a sub-location; the first entry ("Create menu item to here") uses the current location as-is.

```xml
<shortcut name="movie-genres" label="Genres" icon="DefaultGenre.png" browse="videos">
  <path>videodb://movies/genres/</path>
</shortcut>
```

Shortcuts that specify only `<action>` (even an `ActivateWindow` to a browsable path) are fire-and-forget, so no browse-into is offered. Dynamic `<content source="addons">` resolves plugin-source addons as browsable automatically (`RunAddon` executables stay single-click), and `<content source="sources">` resolves user-defined media sources as browsable.

### Source Library Views

After browsing a `<content source="sources">` shortcut to a location, the user chooses how it opens: Files view (the plain folder), or a library view of that path. The offered views are detected from what the source has scanned:

| Source content | Views |
|----------------|-------|
| Movies | Movies |
| TV shows | TV Shows, Episodes |
| Music videos | Music Videos |
| Music | Songs, Albums, Artists |

A view can show content in the path or everything except it, with a chosen sort order. A library view writes a smart playlist to `addon_data/script.skinshortcuts/playlists/{skin}/` and points the shortcut at it; editing the shortcut overwrites that file and deleting it removes the file on save. A source with no scanned library content offers Files view only.

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
| `mode` | No | Value set in `Window.Property(skinshortcuts-dialog)`. Required unless `menu` is set or at least one `<onclose>` action is present |
| `menu` | No | Menu to open directly without mode change. Supports `{item}` and `{customWidget}` placeholders |
| `setfocus` | No | Control ID to focus when subdialog opens |
| `suffix` | No | Property suffix for widget slots (e.g., `.2`). Set in `Window.Property(skinshortcuts-suffix)` |

**Direct menu opening:** Use `menu` without `mode` to open a custom widget menu directly:

```xml
<subdialog buttonID="850" menu="{customWidget}" suffix=".2" />
```

This opens the custom widget menu for slot 2 immediately when button 850 is clicked, without changing dialog mode or spawning an intermediate subdialog.

### `<onclose>` Attributes

| Attribute | Description |
|-----------|-------------|
| `action` | Action type: `menu` |
| `menu` | Menu name for `action="menu"`. Supports `{item}` and `{customWidget}` / `{customWidget.N}` placeholders |
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

## Icon Overrides

Substitute Kodi's generic `Default*.png` icons (e.g., `DefaultFolder.png`, `DefaultMovies.png`) with skin-specific replacements. Useful when your skin has a curated icon set under `extras/icons/` and you want script-generated entries to use them instead of Kodi's defaults.

```xml
<overrides>
  <icons>
    <source>special://skin/extras/icons/</source>
    <icon replace="DefaultFolder.png">files.png</icon>
  </icons>
</overrides>
```

Resolution:

1. The active `<source>` is the first one whose `visible` condition passes (or the first source without a `visible` attribute). Sources must be declared explicitly in the override block; the root `<icons>` picker source is not reused automatically, since a skin's icon picker folder is usually a flat collection of icons rather than a substitution map.
2. **Convention scan**: any `Default*.png` file found in the active source is automatically registered as an override pointing at itself. Drop replacement icons into your icons folder with matching filenames to skip listing them individually.
3. **Explicit overrides**: `<icon replace="X">Y</icon>` declarations win over convention. The replacement path Y is resolved relative to the active source unless it's absolute (starts with `special://` or `/`). With no `<source>` declared, relative Y values are dropped and logged.

### Switching Icon Sets

Point `<source>` at a variable to swap sets without rebuilding:

```xml
<overrides>
  <icons>
    <source>$VAR[MyIconSet]</source>
    <icon replace="DefaultFolder.png">files.png</icon>
  </icons>
</overrides>
```

```xml
<variable name="MyIconSet">
  <value condition="Skin.HasSetting(theme.dark)">special://skin/extras/icons-dark/</value>
  <value>special://skin/extras/icons-light/</value>
</variable>
```

The build keeps the variable in the paths it writes, so Kodi picks the folder when it
draws and a change takes effect on the next skin reload. End every value with a slash.

The folder may sit anywhere the skin can draw from, including inside `media/` where it is
packed into `Textures.xbt`. Address a packed folder the way Kodi does, relative to
`media/`, so `views/icons/` rather than a full path.

### Scope

Overrides apply only to icons the script generates as a default (when no `icon=` attribute is set on a shortcut, when content sources stamp generic icons, when the browse picker falls back to a type-aware default). Icons declared explicitly via `icon="..."` stay literal: `icon="DefaultFolder.png"` is taken as a deliberate choice.

---

## Context Menu

The context action (`C` on a keyboard, the menu button on a remote) opens a menu of actions for the selected item.

```xml
<contextmenu>true</contextmenu>
```

Default `true` when the `<contextmenu>` element is absent. Set its text to `false` to disable it. Any other text is treated as `true` and logged.

### Where It Opens

By default the context action works anywhere in the management dialog. Set `enableon` to a comma separated list of control IDs to limit it to those controls when focused:

```xml
<contextmenu enableon="211,212" />
```

List every control the menu should open on, including the ones a subdialog focuses. A value with no usable control IDs is ignored, and the menu opens anywhere.

### Rows

With no `<button>` children, the menu shows the built-in rows: Edit Label, Edit Action, Change Icon, Edit Submenu, Delete.

Add `<button>` children to replace that set. Each row clicks the dialog button with that ID, so it reaches built-in buttons, [property buttons](properties.md#button-mappings) and [subdialogs](management-dialog.md#subdialogs) alike, whether or not your dialog draws that button as a control:

```xml
<contextmenu enableon="211">
  <button id="305" label="$ADDON[script.skinshortcuts 32171]" />
  <button id="307" label="$ADDON[script.skinshortcuts 32172]" />
  <button id="306" label="$ADDON[script.skinshortcuts 32173]" />
  <button id="313" />
  <button id="800" label="$LOCALIZE[31000]" condition="widgetType=custom" />
  <button id="302" label="$LOCALIZE[117]" />
</contextmenu>
```

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Button to click when the row is chosen |
| `label` | No | Row label. Defaults to the script's own label for [built-in button IDs](management-dialog.md#built-in-buttons) |
| `condition` | No | [Property condition](conditions.md), checked against the selected item |
| `visible` | No | [Kodi condition](conditions.md#kodi-visibility-conditions) |

Rows are listed in the order written. A row is dropped when its `condition` or `visible` fails, when nothing routes its `id`, or when it has no `label` and no built-in default. When every row is dropped, the context action opens nothing.

The `disabled` state of the item is available to `condition` as `disabled=True` or `disabled=False`. Button 313 already picks its own default label from that state, so it only needs a `label` when you want different wording.

In a subdialog, `condition` reads the item the subdialog is editing and follows its property suffix, so `condition="widgetType=custom"` checks `widgetType.2` in a `.2` slot. Only `=` and `~` comparisons are suffixed; write `EMPTY`, `IN` and bare property checks against the slot you mean.

`condition` reads stored values, so a property left unset reads empty even when a [fallback](properties.md#fallbacks) would supply a value. `visible` is evaluated by Kodi against container 211, which carries the fallback-resolved value and does not track the edited item in a subdialog. Gate subdialog rows on `Window.Property(skinshortcuts-dialog)` rather than on `Container(211).ListItem`.

### What Overrides What

| Setting | Default | Overridden by |
|---------|---------|---------------|
| On or off | On | Element text `false` |
| Where it opens | Anywhere in the dialog | `enableon` |
| Rows | Built-in five | Any `<button>` children |
| Row label | Script label for built-in IDs, otherwise none | `label` |

---

[↑ Top](#menu-configuration) · [Skinning Docs](index.md)
