# Skin Shortcuts v3 - Codebase Documentation Index

**Version:** 3.0.0-dev

**Quick Start:** See [OVERVIEW.md](OVERVIEW.md)

***

## Documentation Files

### Core Modules (`core/`)

| File | Doc | Purpose |
|------|-----|---------|
| conditions.py | [conditions.md](core/conditions.md) | Condition evaluation |
| expressions.py | [expressions.md](core/expressions.md) | $MATH and $IF expressions |
| constants.py | [constants.md](core/constants.md) | All constants |
| exceptions.py | [exceptions.md](core/exceptions.md) | Exception hierarchy |
| localize.py | [localize.md](core/localize.md) | Label localization |
| hashing.py | [hashing.md](core/hashing.md) | Rebuild detection |
| userdata.py | [userdata.md](core/userdata.md) | User data storage |
| manager.py | [manager.md](core/manager.md) | Menu manager API |
| config.py | [config.md](core/config.md) | Config loader |
| entry.py | [entry.md](core/entry.md) | Entry point |

### Dialog Package (`dialog/`)

| File | Doc | Purpose |
|------|-----|---------|
| Overview | [README.md](dialog/README.md) | Package overview |
| `__init__.py` | [init.md](dialog/init.md) | Public API |
| base.py | [base.md](dialog/base.md) | Core initialization, events |
| items.py | [items.md](dialog/items.md) | Item operations |
| pickers.py | [pickers.md](dialog/pickers.md) | Shortcut/widget pickers |
| properties.py | [properties.md](dialog/properties.md) | Property management |
| subdialogs.py | [subdialogs.md](dialog/subdialogs.md) | Subdialog handling |

### Models Package (`models/`)

| File | Doc | Purpose |
|------|-----|---------|
| Overview | [README.md](models/README.md) | Package overview |
| menu.py | [menu.md](models/menu.md) | Menu/item models |
| widget.py | [widget.md](models/widget.md) | Widget models |
| background.py | [background.md](models/background.md) | Background models |
| property.py | [property.md](models/property.md) | Property schema models |
| template.py | [template.md](models/template.md) | Template models |

### Loaders Package (`loaders/`)

| File | Doc | Purpose |
|------|-----|---------|
| Overview | [README.md](loaders/README.md) | Package overview |
| base.py | [base.md](loaders/base.md) | Base XML utilities |
| menu.py | [menu.md](loaders/menu.md) | Menu config loader |
| widget.py | [widget.md](loaders/widget.md) | Widget config loader |
| background.py | [background.md](loaders/background.md) | Background loader |
| property.py | [property.md](loaders/property.md) | Property schema loader |
| template.py | [template.md](loaders/template.md) | Template schema loader |

### Builders Package (`builders/`)

| File | Doc | Purpose |
|------|-----|---------|
| Overview | [README.md](builders/README.md) | Package overview |
| includes.py | [includes.md](builders/includes.md) | Includes.xml builder |
| template.py | [template.md](builders/template.md) | Template processor |

### Providers Package (`providers/`)

| File | Doc | Purpose |
|------|-----|---------|
| Overview | [README.md](providers/README.md) | Package overview |
| content.py | [content.md](providers/content.md) | Dynamic content resolver |

***

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
    ├── load_menus() → MenuConfig
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

***

## Cross-Reference: Model Usage

### MenuItem

* **Created by:** loaders/menu.py, userdata.py, manager.py
* **Used by:** Menu, dialog/, builders/includes.py

### Widget

* **Created by:** loaders/widget.py, dialog/pickers.py
* **Used by:** config.py, dialog/, builders/includes.py

### Background

* **Created by:** loaders/background.py
* **Used by:** config.py, dialog/

### PropertySchema

* **Created by:** loaders/property.py
* **Used by:** config.py, dialog/, builders/template.py

### TemplateSchema

* **Created by:** loaders/template.py
* **Used by:** config.py, builders/template.py
* **Key components:** templates, submenus, items_templates, presets, property_groups, variable_definitions, variable_groups, includes, expressions

### UserData

* **Created by:** userdata.py (load_userdata)
* **Used by:** config.py, manager.py

***

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

***

## Quick Reference: File by Purpose

### "I need to..."

| Task | File(s) |
|------|---------|
| Parse menus.xml | loaders/menu.py |
| Parse widgets.xml | loaders/widget.py |
| Parse templates.xml | loaders/template.py |
| Build includes.xml | builders/includes.py |
| Process templates | builders/template.py |
| Handle items iteration | builders/template.py (_handle_skinshortcuts_items) |
| Show management dialog | dialog/ |
| Save user changes | userdata.py, manager.py |
| Check if rebuild needed | hashing.py |
| Resolve dynamic content | providers/content.py |
| Add new model class | models/\*.py |
| Add new exception | exceptions.py |
| Add new constant | constants.py |
| Evaluate conditions | conditions.py |
| Evaluate $MATH/$IF | expressions.py |
