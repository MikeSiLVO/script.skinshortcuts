# Skin Shortcuts v3 Schema Reference

## File Overview

### Input Files (Skin Configuration)

Located in the skin's `shortcuts/` folder:

| File | Purpose |
|------|---------|
| `menus.xml` | Menu structure, items, groupings for shortcut picker |
| `widgets.xml` | Widget definitions and groupings for widget picker |
| `backgrounds.xml` | Background options for background picker |
| `properties.xml` | Property definitions, options, fallbacks, navigation |
| `overrides.xml` | Action overrides, warnings, global settings |

### Output File (Generated)

| File | Location | Purpose |
|------|----------|---------|
| `script-skinshortcuts-includes.xml` | Skin's resolution folder (e.g., `16x9/`) | Generated includes file containing all menu items, properties, and visibility conditions. Skin references this via `<include>` elements. |

The output file is regenerated when:
- User modifies menus through the management dialog
- Skin calls the build script
- User resets to defaults

### User Data

| File | Location | Purpose |
|------|----------|---------|
| `{skin_id}.userdata.json` | `userdata/addon_data/script.skinshortcuts/` | Stores user customizations (reordered items, changed labels, added shortcuts, widget/background assignments). Merged with skin defaults at build time. |

---

## menus.xml

Defines the menu structure for the skin, including main menus, submenus, and the shortcut picker groupings.

```xml
<menus>
  <!-- Main menu (has container for skin binding) -->
  <menu name="mainmenu" container="9000">
    <defaults>
      <allow widgets="true" backgrounds="true" submenus="true"/>
      <action when="before" condition="...">Action</action>
      <action when="after">Action</action>
    </defaults>
    <item name="movies" submenu="movies">
      <label>$LOCALIZE[20342]</label>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
      <action condition="!Library.HasContent(movies)">ActivateWindow(Videos,files)</action>
      <icon>DefaultMovies.png</icon>
      <thumb>path/to/thumb.png</thumb>
      <visible>Library.HasContent(movies)</visible>
    </item>
  </menu>

  <!-- Submenu (linked via item's submenu= attribute) -->
  <submenu name="movies" container="9001">
    <defaults>
      <allow widgets="true" backgrounds="true" submenus="false"/>
    </defaults>
    <item name="recent">
      <label>Recent</label>
      <action>ActivateWindow(Videos,videodb://recentlyaddedmovies/)</action>
    </item>
  </submenu>

  <!-- Groupings for shortcut picker -->
  <groupings>
    <group name="common" label="Common">
      <shortcut name="movies" label="Movies" type="video" icon="DefaultMovies.png">
        ActivateWindow(Videos,videodb://movies/)
      </shortcut>
      <shortcut name="playlist-browse" label="Browse Playlists" icon="DefaultPlaylist.png"
                path="special://videoplaylists/" browse="video"/>
      <group name="nested" label="Nested Group" condition="...">
        <shortcut .../>
      </group>
      <content source="playlists" target="video" folder="Video Playlists"/>
    </group>
  </groupings>
</menus>
```

### Element Reference

#### `<menus>`
Root element for menu definitions.

| Attribute | Required | Description |
|-----------|----------|-------------|
| — | — | No attributes |

| Child | Description |
|-------|-------------|
| `<menu>` | Main menu definition |
| `<submenu>` | Submenu definition |
| `<groupings>` | Shortcut picker structure |
| `<icons>` | Icon browser sources |
| `<contextmenu>` | Toggle context menu on/off |

---

#### `<menu>`
Defines a main menu. Main menus typically have a container ID for binding to a skin list control.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique identifier for the menu (e.g., "mainmenu") |
| `container` | No | Skin container ID where this menu's items are displayed (e.g., "9000"). When set, enables automatic visibility conditions for submenus and widgets based on which item is focused. |

| Child | Description |
|-------|-------------|
| `<defaults>` | Default settings applied to all items in this menu |
| `<item>` | Menu item definition |

**Container binding:** When `container` is set, the builder generates visibility conditions like `Container(9000).ListItem.Property(id)` so submenus, widgets, and backgrounds automatically show/hide based on the focused menu item.

---

#### `<submenu>`
Defines a submenu. Submenus are linked to parent items via the `submenu` attribute on `<item>`. Structurally identical to `<menu>` but semantically indicates a secondary menu.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique identifier matching an item's `submenu` attribute |
| `container` | No | Skin container ID if submenu displays in a separate list control. When set, enables automatic visibility conditions for nested content. |

| Child | Description |
|-------|-------------|
| `<defaults>` | Default settings applied to all items in this submenu |
| `<item>` | Menu item definition |

**Note:** Submenus automatically receive visibility conditions based on the parent menu's focused item (e.g., the "movies" submenu shows when the "movies" item is focused in the main menu).

---

#### `<defaults>`
Container for default settings that apply to all items in the parent menu/submenu.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `widget` | No | Default widget ID for all items in this menu |
| `background` | No | Default background ID for all items in this menu |

| Child | Description |
|-------|-------------|
| `<allow>` | Feature toggles for this menu |
| `<action>` | Default action(s) applied to all items |
| `<property>` | Default custom property for all items |

**Example:** Set defaults for a submenu:
```xml
<defaults widget="recent-movies" background="movie-fanart">
  <allow widgets="true" backgrounds="true" submenus="false"/>
  <property name="widgetStyle">Panel</property>
</defaults>
```

---

#### `<allow>`
Controls which features are available for items in this menu.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `widgets` | No | Allow widget assignment on items (true/false, default: true) |
| `backgrounds` | No | Allow background assignment on items (true/false, default: true) |
| `submenus` | No | Allow submenu assignment on items (true/false, default: true) |

---

#### `<property>` (in defaults)
Sets a default custom property value for all items in the menu.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Property name |

| Content | Description |
|---------|-------------|
| text | Property value |

---

#### `<action>` (in defaults)
Defines an action that runs for all items in the menu. Useful for menus that need setup/cleanup actions.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `when` | No | When to run: "before" (before item action) or "after" (after item action). Default: "before" |
| `condition` | No | Kodi boolean condition - action only runs when true |

| Content | Description |
|---------|-------------|
| text | The Kodi action/command to execute |

**Example:** Close dialogs before any buttonmenu item action:
```xml
<defaults>
  <action when="before">Dialog.Close(all,true)</action>
</defaults>
```

---

#### `<item>`
Defines a menu item (shortcut).

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique identifier for the item within this menu |
| `submenu` | No | Name of a `<submenu>` to link as this item's submenu |
| `widget` | No | Widget ID to assign to this item |
| `background` | No | Background ID to assign to this item |
| `required` | No | If "true", item cannot be removed by user (default: false) |

| Child | Description |
|-------|-------------|
| `<label>` | Display text (supports $LOCALIZE[id]) |
| `<label2>` | Secondary label/type text |
| `<action>` | Action(s) to execute when selected |
| `<icon>` | Icon image path (default: DefaultShortcut.png) |
| `<thumb>` | Thumbnail image path |
| `<visible>` | Visibility condition |
| `<disabled>` | If "true", item is shown but not selectable |
| `<property>` | Custom property (name attribute required) |
| `<protect>` | Protection rule for the item (see below) |

**Example:** Full item with all options:
```xml
<item name="movies" submenu="movies" widget="recent-movies" background="movie-fanart" required="true">
  <label>$LOCALIZE[20342]</label>
  <label2>Video Library</label2>
  <action>ActivateWindow(Videos,videodb://movies/)</action>
  <action condition="!Library.HasContent(movies)">ActivateWindow(Videos,files)</action>
  <icon>special://skin/extras/icons/DefaultMovies.png</icon>
  <visible>Library.HasContent(movies)</visible>
  <property name="widgetStyle">Panel</property>
</item>
```

**Example:** Protected item with custom warning:
```xml
<item name="settings">
  <label>$LOCALIZE[5]</label>
  <action>ActivateWindow(Settings)</action>
  <protect type="all" heading="$LOCALIZE[19098]" message="$LOCALIZE[31377]"/>
</item>
```

---

#### `<protect>`
Protects a menu item from accidental deletion or modification by showing a confirmation dialog.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `type` | No | What to protect: "delete" (deletion only), "action" (action changes only), or "all" (both). Default: "all" |
| `heading` | No | Dialog heading text (supports $LOCALIZE[id]) |
| `message` | No | Dialog message text (supports $LOCALIZE[id]) |

**Example:** Protect Settings from any modification:
```xml
<item name="settings">
  <label>$LOCALIZE[13000]</label>
  <action>ActivateWindow(Settings)</action>
  <protect type="all" heading="$LOCALIZE[19098]" message="$LOCALIZE[31377]"/>
</item>
```

**Example:** Only warn before deleting (allow action changes):
```xml
<item name="important">
  <label>Important Item</label>
  <action>ActivateWindow(Videos)</action>
  <protect type="delete" heading="Warning" message="Are you sure you want to remove this?"/>
</item>
```

---

#### `<action>` (in item)
Defines an action for the menu item. Multiple actions execute in sequence. Conditional actions provide fallback behavior.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `condition` | No | Kodi boolean condition - action only used when true |

| Content | Description |
|---------|-------------|
| text | The Kodi action/command to execute |

**Example:** Primary action with fallback when library is empty:
```xml
<action>ActivateWindow(Videos,videodb://movies/)</action>
<action condition="!Library.HasContent(movies)">ActivateWindow(Videos,files)</action>
```

---

#### `<label>`
Display text for the item.

| Content | Description |
|---------|-------------|
| text | Label text. Use `$LOCALIZE[id]` for localized strings |

---

#### `<icon>`
Icon image for the item.

| Content | Description |
|---------|-------------|
| text | Path to icon image (e.g., "special://skin/extras/icons/DefaultMovies.png") |

---

#### `<thumb>`
Thumbnail image for the item (optional, separate from icon).

| Content | Description |
|---------|-------------|
| text | Path to thumbnail image |

---

#### `<visible>`
Visibility condition for the item. Item only shows when condition is true.

| Content | Description |
|---------|-------------|
| text | Kodi boolean condition |

---

#### `<groupings>`
Container for shortcut picker groups. Defines what shortcuts are available when users customize menus.

| Attribute | Required | Description |
|-----------|----------|-------------|
| — | — | No attributes |

| Child | Description |
|-------|-------------|
| `<group>` | Shortcut group |

---

#### `<group>`
A category of shortcuts in the picker. Can contain shortcuts, nested groups, and dynamic content.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique identifier for the group |
| `label` | Yes | Display label (supports $LOCALIZE[id]) |
| `condition` | No | Kodi boolean condition - group only shows when true |
| `icon` | No | Icon for the group |

| Child | Description |
|-------|-------------|
| `<shortcut>` | Static shortcut option |
| `<group>` | Nested sub-group |
| `<content>` | Dynamic content reference |

---

#### `<shortcut>`
A shortcut option in the picker.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique identifier |
| `label` | Yes | Display label (supports $LOCALIZE[id]) |
| `type` | No | Category label shown as secondary text (e.g., "Movies") |
| `icon` | No | Icon image path |
| `condition` | No | Kodi boolean condition - shortcut only shows when true |
| `path` | No | Path for browse mode (used with `browse` attribute) |
| `browse` | No | Target window for browse mode: "video", "music", "pictures", "programs" |

| Content | Description |
|---------|-------------|
| text | The Kodi action to execute (ignored if `browse` is set) |

**Standard shortcut:**
```xml
<shortcut name="movies" label="Movies" type="video" icon="DefaultMovies.png">
  ActivateWindow(Videos,videodb://movies/)
</shortcut>
```

**Browse mode shortcut** (opens path in specified window):
```xml
<shortcut name="playlists" label="Video Playlists" icon="DefaultPlaylist.png"
          path="special://videoplaylists/" browse="video"/>
```

---

#### `<content>`
Dynamic content that resolves to shortcuts at runtime (playlists, addons, sources, etc.).

| Attribute | Required | Description |
|-----------|----------|-------------|
| `source` | Yes | Content type (see values below) |
| `target` | No | Media type context (see values below) |
| `path` | No | Custom path override |
| `condition` | No | Kodi boolean condition |
| `icon` | No | Icon override for resolved items |
| `label` | No | Label override |
| `folder` | No | Wrap resolved items in a folder with this label |

**source values:**
- `playlists` - User playlists
- `addons` - Installed addons
- `sources` - File sources
- `favourites` - User favourites
- `pvr` - PVR channels/recordings
- `commands` - System commands (quit, restart, etc.)
- `settings` - Settings shortcuts

**target values:**
- `video` / `videos` - Video context
- `music` / `audio` - Music context
- `pictures` / `images` - Picture context
- `programs` / `executable` - Program/addon context
- `tv` - Live TV
- `radio` - Radio

**Example:** Add video playlists as a folder in the picker:
```xml
<content source="playlists" target="video" folder="Video Playlists"/>
```

---

#### `<icons>`
Defines browse locations for the icon picker (button 306). Supports simple (single path) and advanced (multiple conditional sources) modes.

**Simple mode** (single path, no picker):
```xml
<icons>special://skin/extras/icons/</icons>
```

**Advanced mode** (multiple sources with conditions):
```xml
<icons>
  <source label="Colored Icons" condition="Skin.HasSetting(UseColoredIcons)">special://skin/extras/icons/colored/</source>
  <source label="Monochrome Icons" condition="!Skin.HasSetting(UseColoredIcons)">special://skin/extras/icons/mono/</source>
  <source label="Browse...">browse</source>
</icons>
```

| Child | Description |
|-------|-------------|
| `<source>` | Icon browse source |
| (text) | Simple mode: single path to use directly |

---

#### `<source>` (in icons)
Defines an icon browse location.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `label` | No | Display label in source picker |
| `condition` | No | Kodi boolean condition - source only shows when true |
| `icon` | No | Icon for the source in picker |

| Content | Description |
|---------|-------------|
| text | Path to browse from, or "browse" for free file browser |

---

#### `<contextmenu>`
Enables or disables the context menu (shown when user presses context/menu button on a list item). Enabled by default.

**Enable (default):**
```xml
<contextmenu>true</contextmenu>
```

**Disable:**
```xml
<contextmenu>false</contextmenu>
```

| Content | Description |
|---------|-------------|
| text | "true" (default), "false", "yes", "no", "1", "0" |

---

## widgets.xml

Defines widgets and widget picker groupings.

```xml
<widgets showGetMore="false">
  <!-- Direct widget definitions -->
  <widget name="recent-movies" label="Recent Movies" type="movies">
    <path>videodb://recentlyaddedmovies/</path>
    <target>videos</target>
    <icon>DefaultMovies.png</icon>
    <condition>Library.HasContent(movies)</condition>
    <limit>25</limit>
    <sortby>dateadded</sortby>
    <sortorder>descending</sortorder>
  </widget>

  <!-- Widget groupings for picker -->
  <groupings>
    <group name="movies" label="Movies">
      <widget name="recent" label="Recent" type="movies" icon="..." condition="...">
        <path>videodb://recentlyaddedmovies/</path>
        <target>videos</target>
      </widget>
      <group name="nested" label="Nested" condition="...">
        <widget .../>
      </group>
      <content source="playlists" target="video" folder="Playlists"/>
    </group>
  </groupings>
</widgets>
```

### Element Reference

#### `<widgets>`
Root element for widget definitions.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `showGetMore` | No | Show "Get More..." option in picker to browse addon repository (true/false, default: true) |

| Child | Description |
|-------|-------------|
| `<widget>` | Widget definition |
| `<groupings>` | Widget picker structure |

---

#### `<widget>`
Defines a widget that can be assigned to menu items.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique identifier |
| `label` | Yes | Display label |
| `type` | No | Widget type for skin logic (e.g., "movies", "tvshows", "episodes", "albums") |
| `target` | No | Target window type (can also be child element) |
| `icon` | No | Icon image path (can also be child element) |
| `condition` | No | Kodi boolean condition (can also be child element) |

| Child | Description |
|-------|-------------|
| `<path>` | Content path for the widget |
| `<target>` | Target window: "videos", "music", "pictures", "programs" |
| `<icon>` | Icon image path |
| `<condition>` | Visibility condition |
| `<limit>` | Maximum number of items |
| `<sortby>` | Sort field |
| `<sortorder>` | Sort direction: "ascending" or "descending" |

---

#### `<groupings>` (widgets)
Container for widget picker groups.

| Child | Description |
|-------|-------------|
| `<group>` | Widget group |

---

#### `<group>` (widgets)
A category of widgets in the picker.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique identifier |
| `label` | Yes | Display label |
| `condition` | No | Kodi boolean condition |

| Child | Description |
|-------|-------------|
| `<widget>` | Widget option |
| `<group>` | Nested sub-group |
| `<content>` | Dynamic content reference |

---

## backgrounds.xml

Defines background options for the background picker.

```xml
<backgrounds>
  <!-- Property-based (info label) -->
  <background name="movie-fanart" label="Movie Fanart" type="property">
    <path>$INFO[Container(9000).ListItem.Art(fanart)]</path>
    <icon>DefaultMovies.png</icon>
    <condition>Library.HasContent(movies)</condition>
  </background>

  <!-- Playlist-based -->
  <background name="playlist" label="Playlist" type="playlist">
    <icon>DefaultPlaylist.png</icon>
    <source label="Video Playlists" icon="...">special://videoplaylists/</source>
    <source label="Music Playlists">special://musicplaylists/</source>
  </background>

  <!-- Live background -->
  <background name="live-movies" label="Live: Random Movies" type="live">
    <path>random movies</path>
    <icon>DefaultMovies.png</icon>
    <condition>Library.HasContent(movies)</condition>
  </background>

  <!-- Live playlist -->
  <background name="live-playlist" label="Live: Playlist" type="live-playlist">
    <icon>DefaultPlaylist.png</icon>
    <source label="Video Playlists">special://videoplaylists/</source>
  </background>

  <!-- Browse for single image -->
  <background name="custom" label="Custom Image" type="browse">
    <icon>DefaultPicture.png</icon>
    <source label="Skin Backgrounds">special://skin/backgrounds/</source>
    <source label="Browse...">browse</source>
  </background>

  <!-- Browse for folder (multi/slideshow) -->
  <background name="folder" label="Image Folder" type="multi">
    <icon>DefaultFolder.png</icon>
    <source label="My Backgrounds">special://profile/backgrounds/</source>
    <source label="Browse...">browse</source>
  </background>
</backgrounds>
```

### Element Reference

#### `<backgrounds>`
Root element for background definitions.

| Attribute | Required | Description |
|-----------|----------|-------------|
| — | — | No attributes |

| Child | Description |
|-------|-------------|
| `<background>` | Background option |

---

#### `<background>`
Defines a background option.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Unique identifier |
| `label` | Yes | Display label |
| `type` | Yes | Background type (see values below) |

| Child | Description |
|-------|-------------|
| `<path>` | Path or info label (for property/live types) |
| `<icon>` | Icon image path |
| `<condition>` | Visibility condition |
| `<source>` | Playlist source (for playlist/live-playlist types) |

**type values:**
- `property` - Uses an info label that resolves to an image path
- `playlist` - User selects a playlist, images from playlist items
- `live` - Dynamic background from library content
- `live-playlist` - Dynamic background from a user-selected playlist
- `browse` - User browses for a single image file
- `multi` - User browses for a folder (slideshow)

---

#### `<source>` (playlist types)
Defines a playlist source location for playlist/live-playlist type backgrounds.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `label` | Yes | Display label for this source |
| `icon` | No | Icon for this source |

| Content | Description |
|---------|-------------|
| text | Path to playlist folder |

---

#### `<source>` (browse/multi types)
Defines browse locations for browse/multi type backgrounds. Each background can have multiple conditional sources.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `label` | No | Display label in source picker |
| `condition` | No | Kodi boolean condition - source only shows when true |
| `icon` | No | Icon for this source |

| Content | Description |
|---------|-------------|
| text | Path to browse from, or "browse" for free file browser |

**Example:** Browse background with conditional sources:
```xml
<background name="custom-fanart" label="Custom Fanart" type="browse">
  <source label="HD Fanart" condition="Skin.HasSetting(UseHDBackgrounds)">special://skin/backgrounds/hd/</source>
  <source label="SD Fanart" condition="!Skin.HasSetting(UseHDBackgrounds)">special://skin/backgrounds/sd/</source>
  <source label="Browse...">browse</source>
</background>
```

**Example:** Multi/slideshow background:
```xml
<background name="slideshow" label="Slideshow Folder" type="multi">
  <source label="My Slideshows">special://profile/slideshows/</source>
  <source label="Browse...">browse</source>
</background>
```

---

## properties.xml

Defines property schemas for the management dialog - what properties are available, their options, UI controls, fallbacks, and navigation.

```xml
<properties>
  <!-- Reusable includes -->
  <include name="StyleOptions">
    <option value="List" label="$LOCALIZE[535]"/>
    <option value="Panel" label="$LOCALIZE[31712]"/>
  </include>

  <!-- Property definition -->
  <property name="widgetStyle">
    <control buttonID="1001" title="$LOCALIZE[31701]" showNone="false" showicons="true"/>
    <requires property="widgetPath"/>
    <options>
      <include content="StyleOptions"/>
      <option value="Custom" label="Custom" condition="widgetType=custom"/>
    </options>
  </property>

  <!-- Property with suffix support -->
  <property name="widgetArt.2">
    <control buttonID="2004" title="$LOCALIZE[31706]"/>
    <requires property="widgetStyle.2"/>
    <options>
      <include content="ArtOptions" suffix=".2"/>
    </options>
  </property>

  <!-- Toggle property -->
  <property name="widgetHide" type="toggle">
    <control buttonID="1022" title="$LOCALIZE[31289]"/>
    <requires property="widgetStyle"/>
  </property>

  <!-- Widget picker property -->
  <property name="widget" type="widget">
    <control buttonID="309" title="$LOCALIZE[31000]"/>
  </property>

  <!-- Background picker property -->
  <property name="background" type="background">
    <control buttonID="310" title="$LOCALIZE[31053]"/>
  </property>

  <!-- Template-only (not shown in UI) -->
  <property name="widgetPath" templateonly="true"/>

  <!-- Fallbacks -->
  <fallbacks>
    <fallback property="widgetArt">
      <when condition="widgetType=albums | songs">Square Poster</when>
      <default>Poster</default>
    </fallback>
  </fallbacks>

  <!-- Navigation -->
  <navigation>
    <onback from="1001,1002,1003" to="800"/>
    <onback from="2001,2002,2003" to="801"/>
  </navigation>
</properties>
```

### Element Reference

#### `<properties>`
Root element for property definitions.

| Attribute | Required | Description |
|-----------|----------|-------------|
| — | — | No attributes |

| Child | Description |
|-------|-------------|
| `<include>` | Reusable content definition |
| `<property>` | Property definition |
| `<fallbacks>` | Fallback value definitions |
| `<navigation>` | Navigation mappings |

---

#### `<include>` (definition)
Defines reusable content that can be referenced elsewhere.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Name to reference this include |

| Child | Description |
|-------|-------------|
| `<option>` | Option definitions |
| `<when>` | Conditional fallback rules |
| `<default>` | Default fallback value |

---

#### `<include/>` (reference)
References and expands a defined include. Self-closing tag.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `content` | Yes | Name of the include to expand |
| `suffix` | No | Suffix to append to property names in conditions (e.g., ".2") |

**Example:** Reuse options with suffix transform:
```xml
<include name="ArtOptions">
  <option value="Poster" label="Poster" condition="!widgetType=weather"/>
</include>

<!-- In property definition -->
<options>
  <include content="ArtOptions" suffix=".2"/>
  <!-- Expands with condition="!widgetType.2=weather" -->
</options>
```

---

#### `<property>`
Defines a property that can be set on menu items.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Property name (e.g., "widgetStyle", "widgetStyle.2") |
| `type` | No | Special property type: "toggle", "widget", "background" |
| `templateonly` | No | If "true", property is excluded from menu item output (used only by templates) |

| Child | Description |
|-------|-------------|
| `<control>` | UI control settings |
| `<requires>` | Dependency on another property |
| `<options>` | Available values |

**type values:**
- (empty) - Standard property with option picker
- `toggle` - Boolean toggle, sets "True" or clears value
- `widget` - Opens widget picker, auto-populates widgetName, widgetPath, widgetType, widgetTarget
- `background` - Opens background picker, auto-populates backgroundName, backgroundPath

---

#### `<control>`
UI control settings for the property.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `buttonID` | Yes | Skin button ID that triggers this property picker |
| `title` | No | Dialog title (supports $LOCALIZE[id]) |
| `showNone` | No | Show "None" option to clear value (true/false, default: true) |
| `showicons` | No | Show icons in picker dialog (true/false, default: true) |

---

#### `<requires>`
Makes this property depend on another property having a value.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `property` | Yes | Name of required property |

**Example:** Only show widgetStyle options when a widget is selected:
```xml
<property name="widgetStyle">
  <requires property="widgetPath"/>
</property>
```

---

#### `<options>`
Container for property value options.

| Child | Description |
|-------|-------------|
| `<option>` | Single option |
| `<include/>` | Include reference |

---

#### `<option>`
A single value option for a property.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `value` | Yes | The value stored when selected |
| `label` | Yes | Display label (supports $LOCALIZE[id]) |
| `condition` | No | Kodi-style condition - option only shows when true |

| Child | Description |
|-------|-------------|
| `<icon>` | Icon variant(s) |

---

#### `<icon>` (in option)
Icon for an option. Multiple icons can provide variants based on conditions.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `condition` | No | Condition for this icon variant (e.g., "widgetArt=Poster") |

| Content | Description |
|---------|-------------|
| text | Icon image path |

**Example:** Different icons based on art type:
```xml
<option value="Glass" label="Glass">
  <icon condition="widgetArt=Poster">cases/glass/portrait.png</icon>
  <icon condition="widgetArt=Banner">cases/glass/banner.png</icon>
  <icon>cases/glass/landscape.png</icon>  <!-- default -->
</option>
```

---

#### `<fallbacks>`
Container for property fallback definitions.

| Child | Description |
|-------|-------------|
| `<fallback>` | Fallback definition |

---

#### `<fallback>`
Defines default values for a property when not explicitly set.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `property` | Yes | Property name to provide fallback for |

| Child | Description |
|-------|-------------|
| `<when>` | Conditional fallback value |
| `<default>` | Default fallback value |
| `<include/>` | Include reference |

---

#### `<when>` (in fallback)
Conditional fallback value.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `condition` | Yes | Condition for this fallback |

| Content | Description |
|---------|-------------|
| text | Fallback value when condition is true |

---

#### `<default>` (in fallback)
Default fallback value when no conditions match.

| Content | Description |
|---------|-------------|
| text | Default fallback value |

**Example:**
```xml
<fallback property="widgetArt">
  <when condition="widgetType=albums | songs | artists">Square Poster</when>
  <default>Poster</default>
</fallback>
```

---

#### `<navigation>`
Container for navigation mappings.

| Child | Description |
|-------|-------------|
| `<onback>` | Back navigation mapping |

---

#### `<onback>`
Maps control IDs to back navigation targets.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `from` | Yes | Comma-separated list of control IDs |
| `to` | Yes | Target control ID when back is pressed |

**Example:** Return to container 800 when back pressed from widget controls:
```xml
<onback from="1001,1002,1003,1004" to="800"/>
```

---

## overrides.xml

Global settings, action overrides for deprecated actions, and warning dialogs.

```xml
<overrides>
  <!-- Global settings -->
  <alwaysRestore>true</alwaysRestore>

  <!-- Action override (replace deprecated/changed actions) -->
  <override action="ActivateWindow(favourites)">
    <action>ActivateWindow(favouritesbrowser)</action>
  </override>

  <!-- Multi-action override -->
  <override action="RebootFromNand">
    <action>System.ExecWait("/usr/sbin/rebootfromnand")</action>
    <action>Reboot()</action>
  </override>

  <!-- Warning dialog -->
  <warn heading="19098" message="31377">ActivateWindow(Settings)</warn>
</overrides>
```

### Element Reference

#### `<overrides>`
Root element for overrides and global settings.

| Attribute | Required | Description |
|-----------|----------|-------------|
| — | — | No attributes |

| Child | Description |
|-------|-------------|
| `<alwaysRestore>` | Always restore user menu setting |
| `<override>` | Action override |
| `<warn>` | Warning dialog |

---

#### `<alwaysRestore>`
Controls whether user menu customizations are always restored on load.

| Content | Description |
|---------|-------------|
| text | "true" or "false" |

---

#### `<override>`
Replaces one action with another. Used for migrating deprecated Kodi actions or platform-specific replacements.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `action` | Yes | The action to match and replace |

| Child | Description |
|-------|-------------|
| `<action>` | Replacement action(s) |

**Example:** Replace deprecated favourites window:
```xml
<override action="ActivateWindow(favourites)">
  <action>ActivateWindow(favouritesbrowser)</action>
</override>
```

**Example:** Multi-action replacement:
```xml
<override action="RebootFromNand">
  <action>System.ExecWait("/usr/sbin/rebootfromnand")</action>
  <action>Reboot()</action>
</override>
```

---

#### `<warn>`
Shows a confirmation dialog before executing an action.

| Attribute | Required | Description |
|-----------|----------|-------------|
| `heading` | Yes | Dialog heading (localize string ID) |
| `message` | Yes | Dialog message (localize string ID) |

| Content | Description |
|---------|-------------|
| text | The action that triggers this warning |

**Example:**
```xml
<warn heading="19098" message="31377">ActivateWindow(Settings)</warn>
```

---

## Condition Syntax

Conditions are used throughout the schema for visibility and conditional logic.

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

Property name carries forward:
```
widgetType=movies | episodes | tvshows
```
Expands to:
```
widgetType=movies | widgetType=episodes | widgetType=tvshows
```

### Examples

```xml
<!-- Simple equality -->
condition="widgetType=movies"

<!-- Negation -->
condition="!widgetType=weather"

<!-- OR -->
condition="widgetType=movies | tvshows | episodes"

<!-- AND -->
condition="widget=library + widgetType=movies"

<!-- Contains -->
condition="widgetPath~skin.helper"

<!-- Complex with grouping -->
condition="[widget=library | playlist] + [widgetType=movies | tvshows]"

<!-- Negated group -->
condition="![widgetType=weather | system | addon]"
```

---

## Common Patterns

### Localized Labels
```xml
<label>$LOCALIZE[20342]</label>
label="$LOCALIZE[20342]"
```

### Conditional Actions (Fallbacks)
```xml
<action>ActivateWindow(Videos,videodb://movies/)</action>
<action condition="!Library.HasContent(movies)">ActivateWindow(Videos,files)</action>
```

### Default Menu Actions
```xml
<defaults>
  <action when="before">Dialog.Close(all,true)</action>
  <action when="after" condition="...">SetProperty(...)</action>
</defaults>
```

### Dynamic Content
```xml
<content source="playlists" target="video"/>
<content source="addons" target="video" folder="Video Add-ons"/>
<content source="favourites"/>
```

### Include with Suffix
```xml
<include name="Options">
  <option value="A" condition="prop=x"/>
</include>

<options>
  <include content="Options" suffix=".2"/>
  <!-- Becomes: condition="prop.2=x" -->
</options>
```
