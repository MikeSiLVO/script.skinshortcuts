# Skin Shortcuts v3 - Codebase Documentation Index

**Version:** 3.0.0-dev
**Total Files:** 35 Python source files
**Total Lines:** ~8,200

**Quick Start:** See [OVERVIEW.md](OVERVIEW.md)

---

## Documentation Files

### Core Modules (`core/`)
| File | Doc | Lines | Purpose |
|------|-----|-------|---------|
| conditions.py | [conditions.md](core/conditions.md) | ~190 | Condition evaluation |
| constants.py | [constants.md](core/constants.md) | ~85 | All constants |
| exceptions.py | [exceptions.md](core/exceptions.md) | ~40 | Exception hierarchy |
| localize.py | [localize.md](core/localize.md) | ~60 | Label localization |
| hashing.py | [hashing.md](core/hashing.md) | ~150 | Rebuild detection |
| userdata.py | [userdata.md](core/userdata.md) | ~260 | User data storage |
| manager.py | [manager.md](core/manager.md) | ~500 | Menu manager API |
| config.py | [config.md](core/config.md) | ~220 | Config loader |
| entry.py | [entry.md](core/entry.md) | ~340 | Entry point |

### Dialog Package (`dialog/`)
| File | Doc | Lines | Purpose |
|------|-----|-------|---------|
| Overview | [README.md](dialog/README.md) | - | Package overview |
| \_\_init\_\_.py | [init.md](dialog/init.md) | ~130 | Public API |
| base.py | [base.md](dialog/base.md) | ~640 | Core initialization, events |
| items.py | [items.md](dialog/items.md) | ~410 | Item operations |
| pickers.py | [pickers.md](dialog/pickers.md) | ~520 | Shortcut/widget pickers |
| properties.py | [properties.md](dialog/properties.md) | ~610 | Property management |
| subdialogs.py | [subdialogs.md](dialog/subdialogs.md) | ~260 | Subdialog handling |

### Models Package (`models/`)
| File | Doc | Lines | Purpose |
|------|-----|-------|---------|
| Overview | [README.md](models/README.md) | - | Package overview |
| menu.py | [menu.md](models/menu.md) | ~360 | Menu/item models |
| widget.py | [widget.md](models/widget.md) | ~80 | Widget models |
| background.py | [background.md](models/background.md) | ~96 | Background models |
| property.py | [property.md](models/property.md) | ~100 | Property schema models |
| template.py | [template.md](models/template.md) | ~260 | Template models |

### Loaders Package (`loaders/`)
| File | Doc | Lines | Purpose |
|------|-----|-------|---------|
| Overview | [README.md](loaders/README.md) | - | Package overview |
| base.py | [base.md](loaders/base.md) | ~150 | Base XML utilities |
| menu.py | [menu.md](loaders/menu.md) | ~480 | Menu config loader |
| widget.py | [widget.md](loaders/widget.md) | ~122 | Widget config loader |
| background.py | [background.md](loaders/background.md) | ~162 | Background loader |
| property.py | [property.md](loaders/property.md) | ~280 | Property schema loader |
| template.py | [template.md](loaders/template.md) | ~480 | Template schema loader |

### Builders Package (`builders/`)
| File | Doc | Lines | Purpose |
|------|-----|-------|---------|
| Overview | [README.md](builders/README.md) | - | Package overview |
| includes.py | [includes.md](builders/includes.md) | ~290 | Includes.xml builder |
| template.py | [template.md](builders/template.md) | ~850 | Template processor |

### Providers Package (`providers/`)
| File | Doc | Lines | Purpose |
|------|-----|-------|---------|
| Overview | [README.md](providers/README.md) | - | Package overview |
| content.py | [content.md](providers/content.md) | ~500 | Dynamic content resolver |

---

## Cross-Reference: Who Calls What

### Entry Points
```
RunScript(script.skinshortcuts,...)
    └── entry.main()
        ├── build_includes() → SkinConfig.load() → build_includes()
        ├── show_management_dialog() → ManagementDialog
        ├── reset_all_menus()
        └── clear_custom_menu()
```

### Configuration Loading
```
SkinConfig.load()
    ├── load_menu_config() → MenuConfig
    ├── load_widgets() → WidgetConfig
    ├── load_backgrounds() → BackgroundConfig
    ├── load_templates() → TemplateSchema
    ├── load_properties() → PropertySchema
    └── load_userdata() → UserData
        └── merge_menu() for each menu
```

### Includes Building
```
SkinConfig.build_includes()
    └── IncludesBuilder.write()
        ├── _build_menu_include()
        ├── _build_submenu_include()
        ├── _build_custom_widget_includes()
        └── TemplateBuilder.build() if templates exist
```

### Dialog Flow
```
ManagementDialog.onInit()
    ├── MenuManager (creates or uses shared)
    ├── PropertySchema (loads or uses shared)
    └── _load_items() → _display_items()

ManagementDialog.onClick()
    ├── _add_item() / _delete_item() / _move_item()
    ├── _set_label() / _set_icon() / _set_action()
    ├── _choose_shortcut() → _pick_from_groups()
    ├── _handle_property_button()
    │   ├── _handle_widget_property() → _pick_widget_from_groups()
    │   ├── _handle_background_property() → _nested_picker()
    │   └── _handle_options_property()
    ├── _edit_submenu() → spawn child dialog
    └── _spawn_subdialog() → _handle_onclose()

ManagementDialog.close()
    └── manager.save() if root and has_changes
```

---

## Cross-Reference: Model Usage

### MenuItem
- **Created by:** loaders/menu.py, userdata.py, manager.py
- **Used by:** Menu, dialog/, builders/includes.py

### Widget
- **Created by:** loaders/widget.py, dialog/pickers.py
- **Used by:** config.py, dialog/, builders/includes.py

### Background
- **Created by:** loaders/background.py
- **Used by:** config.py, dialog/

### PropertySchema
- **Created by:** loaders/property.py
- **Used by:** config.py, dialog/, builders/template.py

### TemplateSchema
- **Created by:** loaders/template.py
- **Used by:** config.py, builders/template.py

### UserData
- **Created by:** userdata.py (load_userdata)
- **Used by:** config.py, manager.py

---

## Dead Code Analysis

No confirmed dead code remains. Previous dead code has been cleaned up:
- ~~`constants.py: USER_DATA_FILE`~~ (removed)
- ~~`exceptions.py: GroupingsConfigError`~~ (removed)
- ~~`exceptions.py: ValidationError`~~ (removed)
- ~~`exceptions.py: BuildError`~~ (removed)

### Standalone Helper Functions

| Location | Item | Notes |
|----------|------|-------|
| loaders/widget.py | `load_widget_groupings()` | Used by `dialog/properties.py` for widget picker |

---

## Duplication Analysis

### Minimal Duplication Found

1. **Playlist scanning** - Consolidated into `providers/content.scan_playlist_files()`.

2. **Condition evaluation** - Used consistently via `conditions.py.evaluate_condition()`.

3. **Suffix transforms** - `loaders/base.py.apply_suffix_transform()` is the single source.

---

## Future Test Priorities

When adding tests to the codebase, these are the recommended priorities:

### High Priority (Core Logic)
1. `userdata.merge_menu()` - menu merging with overrides
2. `conditions.evaluate_condition()` - condition parsing
3. `builders/template._build_context()` - context assembly
4. `config._apply_action_overrides()` - action replacement

### Medium Priority (Pickers/UI)
5. `dialog/pickers._pick_from_groups()` - navigation logic
6. `dialog/items._set_item_property()` - property management
7. `dialog/subdialogs._handle_onclose()` - onclose flow

### Lower Priority (I/O)
8. `hashing.needs_rebuild()` - hash comparison
9. `localize.resolve_label()` - string resolution
10. `providers/content.resolve()` - content resolution

**Note:** Most tests require mocking Kodi APIs (xbmc, xbmcgui, xbmcvfs).

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                        entry.py                               │
│                  (RunScript entry point)                      │
└─────────────────────────┬────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ dialog/  │    │config.py │    │hashing.py│
    │   (UI)   │    │ (loader) │    │(rebuild) │
    └────┬─────┘    └────┬─────┘    └──────────┘
         │               │
         ▼               ▼
    ┌──────────┐    ┌──────────────────────────┐
    │manager.py│    │       loaders/           │
    │  (API)   │    │ menu, widget, background │
    └────┬─────┘    │ property, template       │
         │          └────────────┬─────────────┘
         ▼                       │
    ┌──────────┐                 ▼
    │userdata  │    ┌──────────────────────────┐
    │  .py     │    │        models/           │
    └──────────┘    │ Menu, Widget, Background │
                    │ PropertySchema, Template │
                    └────────────┬─────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │       builders/          │
                    │ includes.py, template.py │
                    └──────────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │  script-skinshortcuts-   │
                    │      includes.xml        │
                    └──────────────────────────┘
```

---

## Quick Reference: File by Purpose

### "I need to..."

| Task | File(s) |
|------|---------|
| Parse menus.xml | loaders/menu.py |
| Parse widgets.xml | loaders/widget.py |
| Parse templates.xml | loaders/template.py |
| Build includes.xml | builders/includes.py |
| Process templates | builders/template.py |
| Show management dialog | dialog/ |
| Save user changes | userdata.py, manager.py |
| Check if rebuild needed | hashing.py |
| Resolve dynamic content | providers/content.py |
| Add new model class | models/*.py |
| Add new exception | exceptions.py |
| Add new constant | constants.py |
| Evaluate conditions | conditions.py |
