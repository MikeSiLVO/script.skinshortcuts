# Menu Configuration

## Table of Contents

- [Structure](#structure)
- [Menu vs Submenu](#menu-vs-submenu)
- [Menu Element](#menu-element)
- [Item Element](#item-element)
- [Actions](#actions)
- [Defaults](#defaults)

## Structure

`shortcuts/menus.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <!-- Main menu - builds as skinshortcuts-mainmenu include -->
  <menu name="mainmenu" container="9000">
    <defaults>
      <allow widgets="true" backgrounds="true" submenus="true"/>
    </defaults>
    <item name="movies" submenu="movies">
      <label>$LOCALIZE[20342]</label>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
      <icon>DefaultMovies.png</icon>
    </item>
  </menu>

  <!-- Submenu - only builds when referenced by parent item -->
  <submenu name="movies">
    <defaults>
      <allow widgets="false" backgrounds="false" submenus="false"/>
    </defaults>
    <item name="recent-movies">
      <label>Recent Movies</label>
      <action>ActivateWindow(Videos,videodb://recentlyaddedmovies/)</action>
    </item>
  </submenu>

  <!-- Standalone menu (not a submenu) - builds as skinshortcuts-buttonmenu -->
  <menu name="buttonmenu">
    <defaults>
      <allow widgets="false" backgrounds="false" submenus="false"/>
      <action when="before">Dialog.Close(all,true)</action>
    </defaults>
    <item name="quit">
      <label>$LOCALIZE[13012]</label>
      <action>Quit()</action>
    </item>
  </menu>
</menus>
```

## Menu vs Submenu

| Tag | Builds Include | Use Case |
|-----|----------------|----------|
| `<menu>` | Always (as `skinshortcuts-{name}`) | Main menus, standalone menus like button menus |
| `<submenu>` | Only when referenced by a parent item's `submenu` attribute | Submenus linked to parent items |

**Important:** If a submenu's parent item is deleted, the submenu becomes orphaned and won't be built. Use `<menu>` for menus that should always exist.

## Menu Element

### `<menu>` and `<submenu>`

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Unique menu identifier |
| `container` | No | Container ID for visibility conditions (e.g., `9000`) |

### `<defaults>`

Container for default settings applied to all items in the menu.

| Child | Description |
|-------|-------------|
| `<allow>` | Feature toggles (widgets, backgrounds, submenus) |
| `<action>` | Default action(s) with `when` attribute |
| `<property>` | Default property values |

### `<allow>`

Controls which features are available in the management dialog.

```xml
<allow widgets="true" backgrounds="true" submenus="true"/>
```

| Attribute | Default | Description |
|-----------|---------|-------------|
| `widgets` | `true` | Users can assign widgets |
| `backgrounds` | `true` | Users can assign backgrounds |
| `submenus` | `true` | Users can edit submenus |

### Default Actions

Actions that run for all items in the menu:

```xml
<defaults>
  <action when="before">Dialog.Close(all,true)</action>
  <action when="after" condition="...">SetProperty(...)</action>
</defaults>
```

| Attribute | Description |
|-----------|-------------|
| `when` | `before` (runs before item action) or `after` (runs after) |
| `condition` | Optional Kodi boolean condition |

## Item Element

### Attributes

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `name` | Yes | - | Unique item identifier |
| `submenu` | No | - | Name of linked submenu |
| `required` | No | `false` | Cannot be deleted by user |

### Child Elements

| Element | Required | Description |
|---------|----------|-------------|
| `<label>` | Yes | Display text (supports `$LOCALIZE[id]`) |
| `<label2>` | No | Secondary label |
| `<action>` | Yes | Action(s) to execute |
| `<icon>` | No | Icon path (default: `DefaultShortcut.png`) |
| `<thumb>` | No | Thumbnail image |
| `<visible>` | No | Kodi visibility condition |
| `<property>` | No | Custom property (requires `name` attribute) |
| `<protect>` | No | Protection rule (see Protected Items below) |

### Full Example

```xml
<item name="movies" submenu="movies" required="true">
  <label>$LOCALIZE[20342]</label>
  <label2>Video Library</label2>
  <action>ActivateWindow(Videos,videodb://movies/)</action>
  <action condition="!Library.HasContent(movies)">ActivateWindow(Videos,files)</action>
  <icon>special://skin/extras/icons/movies.png</icon>
  <visible>Library.HasContent(movies)</visible>
  <property name="widgetStyle">Panel</property>
</item>
```

### Protected Items

Use `required="true"` to completely prevent deletion, or `<protect>` to show a confirmation dialog.

```xml
<!-- Cannot be deleted at all -->
<item name="settings" required="true">
  <label>Settings</label>
  <action>ActivateWindow(Settings)</action>
</item>

<!-- Confirm before any modification (delete or action change) -->
<item name="skin-settings">
  <label>$LOCALIZE[20077]</label>
  <action>ActivateWindow(SkinSettings)</action>
  <protect type="all" heading="$LOCALIZE[19098]" message="$LOCALIZE[31377]"/>
</item>

<!-- Confirm only before deletion -->
<item name="important">
  <label>Important Item</label>
  <action>ActivateWindow(Videos)</action>
  <protect type="delete" heading="Warning" message="Are you sure?"/>
</item>
```

#### `<protect>` Attributes

| Attribute | Default | Description |
|-----------|---------|-------------|
| `type` | `all` | "delete", "action", or "all" |
| `heading` | - | Dialog heading (supports `$LOCALIZE[id]`) |
| `message` | - | Dialog message (supports `$LOCALIZE[id]`) |

## Actions

### Single Action

```xml
<item name="movies">
  <label>Movies</label>
  <action>ActivateWindow(Videos,videodb://movies/)</action>
</item>
```

### Multiple Actions

Actions execute in sequence:

```xml
<item name="skin-settings">
  <label>Skin Settings</label>
  <action>Dialog.Close(all,true)</action>
  <action>ActivateWindow(SkinSettings)</action>
</item>
```

### Conditional Actions

Conditional actions provide fallback behavior:

```xml
<item name="movies">
  <label>Movies</label>
  <action>ActivateWindow(Videos,videodb://movies/)</action>
  <action condition="!Library.HasContent(movies)">ActivateWindow(Videos,files)</action>
</item>
```

The conditional action runs when its condition is true; otherwise the unconditional action runs.

## Defaults

### Item-Level Defaults

Set default widget, background, or properties on an item:

```xml
<item name="movies">
  <label>Movies</label>
  <action>ActivateWindow(Videos,videodb://movies/)</action>
  <property name="widget">recent-movies</property>
  <property name="widgetStyle">Panel</property>
  <property name="background">movie-fanart</property>
</item>
```

### Menu-Level Defaults

Apply to all items in the menu:

```xml
<menu name="mainmenu">
  <defaults>
    <allow widgets="true" backgrounds="true" submenus="true"/>
    <property name="widgetStyle">List</property>
  </defaults>
  <item .../>
</menu>
```
