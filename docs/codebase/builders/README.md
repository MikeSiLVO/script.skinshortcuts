# builders/ Package

**Path:** `resources/lib/skinshortcuts/builders/`
**Purpose:** Generate includes.xml output from configuration.

***

## Overview

The builders package generates the `script-skinshortcuts-includes.xml` file that Kodi skins include. This file contains all menu data as Kodi-compatible XML includes.

***

## Modules

| File | Doc | Lines | Purpose |
|------|-----|-------|---------|
| `__init__.py` | | ~10 | Re-exports builders |
| `includes.py` | [builders-includes.md](builders-includes.md) | 291 | Main includes.xml builder |
| `template.py` | [builders-template.md](builders-template.md) | 785 | Template processor |

***

## Build Pipeline

```
SkinConfig
    │
    ▼
IncludesBuilder.write()
    │
    ├── _build_menu_include() ──────► <include name="skinshortcuts-mainmenu">
    │
    ├── _build_submenu_include() ───► <include name="skinshortcuts-mainmenu-submenu">
    │
    ├── _build_custom_widget_includes() ► <include name="skinshortcuts-widget-...">
    │
    └── TemplateBuilder.build() ────► Template-based includes (if templates.xml exists)
            │
            ▼
script-skinshortcuts-includes.xml
```

***

## IncludesBuilder (`includes.py`)

Generates standard menu includes:

* Menu items with all properties
* Submenu items
* Custom widget lists
* Property values as XML attributes

### Key Methods

* `write(output_path)` - Write complete includes.xml
* `_build_menu_include(menu)` - Build include for a menu
* `_build_submenu_include(menu)` - Build submenu include
* `_build_custom_widget_includes()` - Build custom widget includes

***

## TemplateBuilder (`template.py`)

Processes templates.xml to generate custom include structures:

* Conditional element inclusion
* Property value substitution
* Visibility condition building
* Other element pass-through

### Key Methods

* `build()` - Process all templates
* `_build_template(template)` - Process single template
* `_build_context(item, menu)` - Build context for template processing
* `_evaluate_element(elem, context)` - Process template element

***

## Output Format

```xml
<?xml version="1.0" encoding="UTF-8"?>
<includes>
    <include name="skinshortcuts-mainmenu">
        <item>
            <label>Movies</label>
            <onclick>ActivateWindow(Videos,videodb://movies/)</onclick>
            <property name="widget">RecentMovies</property>
            ...
        </item>
    </include>
    <include name="skinshortcuts-mainmenu-submenu">
        ...
    </include>
</includes>
```
