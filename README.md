# Skin Shortcuts

[![Code checks](https://github.com/MikeSiLVO/script.skinshortcuts/actions/workflows/checks.yml/badge.svg)](https://github.com/MikeSiLVO/script.skinshortcuts/actions/workflows/checks.yml)
![License](https://img.shields.io/badge/license-GPL--2.0--only-success.svg)
![Kodi Version](https://img.shields.io/badge/kodi-piers%2B-success.svg)

Skin Shortcuts enables user-customizable menus for Kodi skins. Users can add, remove, reorder menu items, assign widgets, backgrounds, and more through a management dialog that you design.

## Overview

- **Customizable Menus**: Users modify menus without editing XML
- **Widget System**: Assign dynamic content to menu items
- **Background System**: Per-item background images
- **View Locking**: Automatic view selection by content type
- **Template Engine**: Generate complex skin includes from simple definitions
- **Property System**: Extensible custom properties with picker dialogs

The script merges skin defaults with the user's changes and writes includes your skin references. Only the user's changes are stored.

```
skin defaults          user customizations           generated includes
(shortcuts/*.xml)   +   (skin.name.userdata.json)  =  (script-skinshortcuts-includes.xml)
```

## Documentation

### Getting Started

| Document | Description |
|----------|-------------|
| [Getting Started](docs/skinning/getting-started.md) | Setup walkthrough and basic integration |
| [File Overview](docs/skinning/files.md) | Configuration file structure |
| [Migrating from v2](docs/migration-v2-to-v3.md) | Porting a v2 Skin Shortcuts skin to v3 |

### Configuration Files

| Document | Description |
|----------|-------------|
| [Menus](docs/skinning/menus.md) | Menu structure, items, submenus, shortcut picker |
| [Widgets](docs/skinning/widgets.md) | Widget definitions and picker configuration |
| [Backgrounds](docs/skinning/backgrounds.md) | Background types and sources |
| [Properties](docs/skinning/properties.md) | Custom property schemas, options, fallbacks |
| [Templates](docs/skinning/templates.md) | Template system for include generation |
| [Views](docs/skinning/views.md) | View locking and automatic view selection |

### Dialog Integration

| Document | Description |
|----------|-------------|
| [Management Dialog](docs/skinning/management-dialog.md) | Dialog controls, properties, window setup |

### Reference

| Document | Description |
|----------|-------------|
| [Conditions](docs/skinning/conditions.md) | Condition syntax for properties and visibility |
| [Built-in Properties](docs/skinning/builtin-properties.md) | Properties available on menu items |
| [Troubleshooting](docs/skinning/troubleshooting.md) | Error notifications and getting a debug log |

## Quick Start

**1. Define a menu** in `shortcuts/menus.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies">
      <label>$LOCALIZE[342]</label>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
      <icon>DefaultMovies.png</icon>
    </item>
  </menu>
</menus>
```

**2. Add a button** to open the management dialog:

```xml
<onclick>RunScript(script.skinshortcuts,type=manage,menu=mainmenu)</onclick>
```

**3. Display the menu** using the generated include:

```xml
<control type="list" id="9000">
  <content>
    <include>skinshortcuts-mainmenu</include>
  </content>
</control>
```

See [Getting Started](docs/skinning/getting-started.md) for the full walkthrough.
