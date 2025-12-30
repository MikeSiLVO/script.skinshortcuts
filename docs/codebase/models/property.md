# models/property.py

**Path:** `resources/lib/skinshortcuts/models/property.py`
**Purpose:** Dataclasses for property schema system.

***

## Overview

Allows skins to declare custom properties for menu items beyond built-in widget/background properties.

***

## Classes

### PropertySchema

Top-level container.

| Field | Type | Description |
|-------|------|-------------|
| `properties` | dict[str, SchemaProperty] | Properties by name |
| `fallbacks` | dict[str, PropertyFallback] | Fallback rules by property |
| `buttons` | dict[int, ButtonMapping] | Button mappings by ID |

**Methods:** `get_property()`, `get_button()`, `get_property_for_button()`

### SchemaProperty

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Property name |
| `template_only` | bool | Only used in templates |
| `requires` | str | Property that must be set first |
| `options` | list[SchemaOption] | Options for select type |
| `type` | str | widget, background, toggle, or options |

### ButtonMapping

| Field | Type | Description |
|-------|------|-------------|
| `button_id` | int | Skin button ID |
| `property_name` | str | Property to act on |
| `suffix` | bool | Append property_suffix at runtime |
| `title` | str | Dialog title |
| `show_none`, `show_icons` | bool | Dialog options |
| `type`, `requires` | str | Override property type/requires |

### SchemaOption

| Field | Type | Description |
|-------|------|-------------|
| `value`, `label` | str | Value and display |
| `condition` | str | Visibility condition |
| `icons` | list[IconVariant] | Icons with conditions |

### PropertyFallback

| Field | Type | Description |
|-------|------|-------------|
| `property_name` | str | Property this applies to |
| `rules` | list[FallbackRule] | Fallback rules in order |
