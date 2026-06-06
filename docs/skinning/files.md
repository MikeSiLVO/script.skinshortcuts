# File Overview

Configuration files and their purposes.

---

## Table of Contents

* [Configuration Files](#configuration-files)
* [Generated Output](#generated-output)
* [User Data](#user-data)

---

## Configuration Files

All configuration files go in `shortcuts/` under your skin root.

```
skin.name/
└── shortcuts/
    ├── menus.xml
    ├── widgets.xml
    ├── backgrounds.xml
    ├── properties.xml
    ├── templates.xml
    └── views.xml
```

### menus.xml

**Required.** Defines menu structure and items.

| Section | Purpose |
|---------|---------|
| `<menu>` | Main menu definitions |
| `<submenu>` | Submenu definitions |
| `<groupings>` | Shortcut picker categories |
| `<icons>` | Icon picker sources |
| `<dialogs>` | Subdialog definitions |
| `<overrides>` | Action replacements |
| `<contextmenu>` | Context menu toggle |

See [Menus](menus.md) for full reference.

### widgets.xml

**Optional.** Defines widgets for the widget picker.

| Section | Purpose |
|---------|---------|
| `<widget>` | Widget definitions |
| `<groupings>` | Widget picker categories |

See [Widgets](widgets.md) for full reference.

### backgrounds.xml

**Optional.** Defines backgrounds for the background picker.

| Section | Purpose |
|---------|---------|
| `<background>` | Background definitions |

See [Backgrounds](backgrounds.md) for full reference.

### properties.xml

**Optional.** Defines custom properties and button mappings.

| Section | Purpose |
|---------|---------|
| `<includes>` | Reusable option sets |
| `<property>` | Property definitions |
| `<buttons>` | Button-to-property mappings |
| `<fallbacks>` | Default value rules |

See [Properties](properties.md) for full reference.

### templates.xml

**Optional.** Defines output templates for includes.

| Section | Purpose |
|---------|---------|
| `<expressions>` | Named condition expressions |
| `<propertyGroups>` | Reusable property sets |
| `<presets>` | Lookup tables |
| `<includes>` | Control snippets |
| `<variables>` | Kodi variable definitions |
| `<template>` | Main templates |
| `<submenu>` | Submenu templates |

See [Templates](templates.md) for full reference.

### views.xml

**Optional.** Defines view locking configuration.

| Section | Purpose |
|---------|---------|
| `<view>` | View definitions |
| `<rules>` | Content type rules |

See [Views](views.md) for full reference.

---

## Generated Output

The script generates includes in each resolution folder defined in your skin's `addon.xml`.

```
skin.name/
├── 16x9/
│   └── script-skinshortcuts-includes.xml
├── 21x9/
│   └── script-skinshortcuts-includes.xml
└── addon.xml
```

### Include Naming

| Pattern | Example |
|---------|---------|
| Menu: `skinshortcuts-{menu}` | `skinshortcuts-mainmenu` |
| Combined submenu: `skinshortcuts-{menu}-submenu` | `skinshortcuts-mainmenu-submenu` |
| Custom widget: `skinshortcuts-{item}-customwidget{n}` | `skinshortcuts-movies-customwidget`, `skinshortcuts-movies-customwidget2` |
| Template: `skinshortcuts-template-{include}` | `skinshortcuts-template-Widgets` |
| Submenu template: `skinshortcuts-{include}` | `skinshortcuts-Submenu` |

### Using Includes

```xml
<control type="list" id="9000">
  <content>
    <include>skinshortcuts-mainmenu</include>
  </content>
</control>
```

> **See also:** [Templates](templates.md) for controlling include output structure

---

## User Data

User customizations are stored in Kodi's addon_data folder.

```
userdata/
└── addon_data/
    └── script.skinshortcuts/
        ├── skin.name.userdata.json
        └── skin.name.hashes        # internal rebuild cache (config + userdata hashes)
```

The `.hashes` file is managed by the script and rewritten on every build; do not edit it. A `type=buildxml,force=true` rebuild bypasses the cache and rebuilds even when the hashes match.

### Format

JSON file containing menu overrides:

```json
{
  "menus": {
    "mainmenu": {
      "items": [
        {
          "name": "movies",
          "label": "My Movies",
          "position": 0
        }
      ],
      "removed": ["tvshows"]
    }
  },
  "views": {
    "library": { "movies": "51" },
    "plugins": { "movies": "50" }
  }
}
```

### Reset

Delete the userdata file and rebuild:

```xml
<onclick>RunScript(script.skinshortcuts,type=resetall)</onclick>
```

Or programmatically:

```python
# Delete: userdata/addon_data/script.skinshortcuts/skin.name.userdata.json
# Then: RunScript(script.skinshortcuts,type=buildxml,force=true)
```

---

[↑ Top](#file-overview) · [Skinning Docs](index.md)
