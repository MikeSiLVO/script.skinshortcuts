<img src="https://raw.githubusercontent.com/mikesilvo164/script.skinshortcuts/master/resources/media/icon.png" width="256" height="256" alt="Skin Shortcuts">

# Skin Shortcuts

[![Build Status](https://img.shields.io/endpoint.svg?url=https%3A%2F%2Factions-badge.atrox.dev%2Fmikesilvo164%2Fscript.skinshortcuts%2Fbadge&logo=none)](https://actions-badge.atrox.dev/mikesilvo164/script.skinshortcuts/goto)
![License](https://img.shields.io/badge/license-GPL--2.0--only-success.svg)
![Kodi Version](https://img.shields.io/badge/kodi-matrix%2B-success.svg)

Skin Shortcuts enables user-customizable menus for Kodi skins. Users can add, remove, reorder menu items, assign widgets, backgrounds, and more through a management dialog that you design.

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [File Structure](#file-structure)
- [Documentation](#documentation)
- [How It Works](#how-it-works)
- [License](#license)

---

## Overview

Skin Shortcuts bridges the gap between skin developers and users by providing:

- **Customizable Menus**: Users modify menus without editing XML
- **Widget System**: Assign dynamic content to menu items
- **Background System**: Per-item background images
- **View Locking**: Automatic view selection by content type
- **Template Engine**: Generate complex skin includes from simple definitions
- **Property System**: Extensible custom properties with picker dialogs

---

## Quick Start

### 1. Create Configuration Files

Create a `shortcuts/` folder in your skin root with these files:

```
skin.name/
└── shortcuts/
    ├── menus.xml         # Menu structure and items
    ├── widgets.xml       # Widget definitions (optional)
    ├── backgrounds.xml   # Background options (optional)
    ├── properties.xml    # Custom property schemas (optional)
    ├── templates.xml     # Output templates (optional)
    └── views.xml         # View locking rules (optional)
```

### 2. Define a Menu

`shortcuts/menus.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="movies">
      <label>$LOCALIZE[342]</label>
      <action>ActivateWindow(Videos,videodb://movies/)</action>
      <icon>DefaultMovies.png</icon>
    </item>
    <item name="settings">
      <label>$LOCALIZE[10004]</label>
      <action>ActivateWindow(Settings)</action>
      <icon>DefaultAddonProgram.png</icon>
    </item>
  </menu>
</menus>
```

### 3. Open the Management Dialog

```xml
<onclick>RunScript(script.skinshortcuts,type=manage&amp;menu=mainmenu)</onclick>
```

### 4. Display the Menu

Use the generated include in your skin:

```xml
<control type="list" id="9000">
  <content>
    <include>skinshortcuts-mainmenu</include>
  </content>
</control>
```

---

## File Structure

```
skin.name/
└── shortcuts/
    ├── menus.xml         # Menus, items, and shortcut picker groupings
    ├── widgets.xml       # Widget definitions and picker groupings
    ├── backgrounds.xml   # Background options
    ├── properties.xml    # Custom property schemas
    ├── templates.xml     # Template definitions for include generation
    └── views.xml         # View locking rules and content detection
```

**Generated Output:**

```
skin.name/
└── 16x9/
    └── script-skinshortcuts-includes.xml
```

**User Data:**

```
userdata/addon_data/script.skinshortcuts/
└── skin.name.userdata.json
```

---

## Documentation

### Getting Started

| Document | Description |
|----------|-------------|
| [Getting Started](docs/skinning/getting-started.md) | Setup walkthrough and basic integration |
| [File Overview](docs/skinning/files.md) | Configuration file structure |

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

---

## How It Works

1. **Skin defines defaults** in XML configuration files
2. **User customizes** through the management dialog
3. **Script generates** `script-skinshortcuts-includes.xml`
4. **Skin uses** the generated includes

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────────────────┐
│ Skin Config     │     │ User Data        │     │ Generated Output            │
│ (shortcuts/)    │  +  │ (.userdata.json) │  →  │ (script-skinshortcuts-*.xml)│
└─────────────────┘     └──────────────────┘     └─────────────────────────────┘
```

The script merges skin defaults with user customizations and outputs includes that your skin references. When users modify menus, only their changes are stored - the rest comes from your defaults.

---

## License

GPL-2.0-only
