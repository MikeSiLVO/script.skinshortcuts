# View Locking

Configure automatic view selection based on content type.

---

## Table of Contents

* [Overview](#overview)
* [File Structure](#file-structure)
* [View Definitions](#view-definitions)
* [Content Rules](#content-rules)
* [Granular Content Detection](#granular-content-detection)
* [Generated Expressions](#generated-expressions)
* [RunScript Commands](#runscript-commands)
* [Window Properties](#window-properties)
* [Skin Integration](#skin-integration)

---

## Overview

View locking allows users to select which view (list, poster wall, etc.) to use for each content type. The script generates Kodi visibility expressions that skins use to show the correct view automatically.

Features:
- Separate library and plugin defaults
- User-customizable view selections
- Per-addon view overrides (any addon ID, not just plugins)
- Granular content detection using compound conditions

---

## File Structure

Create `views.xml` in your skin's shortcuts folder:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<views prefix="ShortcutView_">
  <!-- View definitions -->
  <view id="50" label="535" icon="special://skin/extras/icons/view_list.jpg" />
  <view id="51" label="31247" icon="special://skin/extras/icons/view_wall.jpg" />

  <!-- Content rules -->
  <rules>
    <content name="movies" label="$LOCALIZE[342]" library="51" plugin="50" icon="DefaultMovies.png">
      <visible>Container.Content(movies)</visible>
      <views>50, 51, 52</views>
    </content>
  </rules>
</views>
```

### Root Attributes

| Attribute | Required | Default | Description |
|-----------|----------|---------|-------------|
| `prefix` | No | `ShortcutView_` | Prefix for generated expression names |

---

## View Definitions

Define available views at the top of the file:

```xml
<view id="50" label="535" icon="special://skin/extras/icons/view_list.jpg" />
<view id="51" label="$LOCALIZE[31247]" icon="special://skin/extras/icons/view_wall.jpg" />
```

### Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | View identifier (typically matches view control ID) |
| `label` | Yes | Display label (supports `$LOCALIZE[id]` or numeric ID) |
| `icon` | No | Icon path for picker dialog |

---

## Content Rules

Define content types and their available views:

```xml
<rules>
  <content name="movies" label="$LOCALIZE[342]" library="51" plugin="50" icon="DefaultMovies.png">
    <visible>Container.Content(movies)</visible>
    <views>50, 51, 52, 53</views>
  </content>
</rules>
```

### Content Attributes

| Attribute | Required | Description |
|-----------|----------|-------------|
| `name` | Yes | Content identifier (used in userdata) |
| `label` | Yes | Display label for picker |
| `library` | Yes | Default view ID for library content |
| `plugin` | No | Default view ID for plugin content (falls back to library) |
| `icon` | No | Icon for picker dialog |

### Child Elements

| Element | Required | Description |
|---------|----------|-------------|
| `<visible>` | Yes | Kodi visibility condition for detecting this content |
| `<views>` | Yes | Comma-separated list of available view IDs |

---

## Granular Content Detection

The `<visible>` element accepts any valid Kodi visibility condition, enabling granular content detection beyond simple `Container.Content()` checks.

### Compound Conditions

Combine conditions to differentiate similar content:

```xml
<!-- Movies (excluding sets) -->
<content name="movies" label="Movies" library="51">
  <visible>Container.Content(movies) + !String.StartsWith(Container.FolderPath,videodb://movies/sets)</visible>
  <views>50, 51, 52</views>
</content>

<!-- Movie sets specifically -->
<content name="movies-sets" label="Movie Sets" library="52">
  <visible>Container.Content(movies) + String.StartsWith(Container.FolderPath,videodb://movies/sets)</visible>
  <views>50, 52</views>
</content>
```

### Window-Specific Rules

Differentiate content by window:

```xml
<!-- Video genres only (not music) -->
<content name="genres" label="Genres" library="50">
  <visible>!Window.IsVisible(MyMusicNav.xml) + Container.Content(genres)</visible>
  <views>50, 53</views>
</content>

<!-- Videos root (no content set) -->
<content name="none-videos" label="Videos (Root)" library="50">
  <visible>Container.Content() + Window.IsVisible(MyVideoNav.xml)</visible>
  <views>50</views>
</content>
```

### Video Versions

Handle video versions differently based on context:

```xml
<!-- Video versions in movie view -->
<content name="videoversions" label="Video Versions" library="51">
  <visible>Container.Content(videoversions) + !String.StartsWith(Container.FolderPath,videodb://movies/videoversions)</visible>
  <views>50, 51</views>
</content>

<!-- Video versions in dedicated DB folder -->
<content name="videodb-versions" label="Video Versions (DB)" library="50">
  <visible>Container.Content(videoversions) + String.StartsWith(Container.FolderPath,videodb://movies/videoversions)</visible>
  <views>50</views>
</content>
```

---

## Generated Expressions

The script generates expressions in the includes file.

### Per-View Expressions

| Expression | Description |
|------------|-------------|
| `{prefix}{ViewId}` | True when this view should be visible |
| `{prefix}{ViewId}_Include` | True if view is used by any content rule |

### Plugin Override Expressions

Generated only when plugin-specific overrides exist:

| Expression | Description |
|------------|-------------|
| `{prefix}{Content}_HasPluginOverride` | True if current plugin has a custom view |
| `{prefix}{Content}_IsGenericPlugin` | True if plugin without custom override |

---

## RunScript Commands

### View Browser

Open hierarchical view settings dialog:

```xml
<onclick>RunScript(script.skinshortcuts,type=viewselect)</onclick>
```

### Direct Picker

Open picker for specific content:

```xml
<onclick>RunScript(script.skinshortcuts,type=viewselect,content=movies)</onclick>
```

### Addon Override

Set view for specific addon:

```xml
<onclick>RunScript(script.skinshortcuts,type=viewselect,content=movies,plugin=plugin.video.example)</onclick>
```

### Reset Commands

```xml
<!-- Reset all view selections -->
<onclick>RunScript(script.skinshortcuts,type=resetviews)</onclick>
```

---

## Window Properties

| Property | Window | Description |
|----------|--------|-------------|
| `SkinShortcuts.ViewDialog` | Home | Set to `true` while view dialog is open |

---

## Skin Integration

### Conditional View Loading

Use `_Include` expressions to conditionally load views:

```xml
<include condition="$EXP[ShortcutView_50_Include]">View_50</include>
<include condition="$EXP[ShortcutView_51_Include]">View_51</include>
```

### View Visibility

Use main expressions for view visibility:

```xml
<control type="list" id="50">
  <visible>$EXP[ShortcutView_50]</visible>
  <!-- list content -->
</control>

<control type="panel" id="51">
  <visible>$EXP[ShortcutView_51]</visible>
  <!-- panel content -->
</control>
```

### Fallback for Unhandled Content

For content not covered by rules, show a default view:

```xml
<control type="list" id="50">
  <visible>$EXP[ShortcutView_50] | [!$EXP[ShortcutView_50] + !$EXP[ShortcutView_51] + ...]</visible>
</control>
```

---

## User Data

View selections are stored in userdata JSON:

```json
{
  "views": {
    "library": {
      "movies": "51",
      "tvshows": "52"
    },
    "plugins": {
      "movies": "50"
    },
    "plugin.video.example": {
      "movies": "53"
    }
  }
}
```

| Source | Description |
|--------|-------------|
| `library` | User's library view selections |
| `plugins` | Generic plugin/addon view selections |
| `{addon.id}` | Addon-specific overrides (e.g., `plugin.video.example`, `script.myaddon`) |

---

[↑ Top](#view-locking) · [Skinning Docs](index.md)
