# builders/ Package

**Path:** `resources/lib/skinshortcuts/builders/`
**Purpose:** Generate includes.xml output from configuration.

***

## Modules

| File | Doc | Purpose |
|------|-----|---------|
| `includes.py` | [includes.md](includes.md) | Main includes.xml builder |
| `template.py` | [template.md](template.md) | Template processor |

***

## Build Pipeline

```
SkinConfig
    │
    ▼
IncludesBuilder.write()
    ├── _build_menu_include() → skinshortcuts-{menu}
    ├── _build_submenu_include() → skinshortcuts-{menu}-submenu
    ├── _build_custom_widget_includes() → skinshortcuts-{item}-customwidget{n}
    └── TemplateBuilder.build() → Template-based includes
            │
            ▼
script-skinshortcuts-includes.xml
```
