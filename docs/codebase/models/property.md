# models/property.py

**Path:** `resources/lib/skinshortcuts/models/property.py`
**Lines:** 104
**Purpose:** Dataclass models for the property schema system (custom properties defined in properties.xml).

---

## Overview

Defines the property schema system which allows skins to declare custom properties that can be set on menu items. This enables skin-specific configuration beyond the built-in widget/background properties.

---

## Classes

### IconVariant (line 8)
Icon with optional visibility condition.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `path` | str | required | Icon path |
| `condition` | str | "" | Property condition for when to use this icon |

**Used by:** SchemaOption.icons

---

### SchemaOption (line 16)
An option for select-type properties.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `value` | str | required | Value stored when selected |
| `label` | str | required | Display label |
| `condition` | str | "" | Property condition for visibility |
| `icons` | list[IconVariant] | [] | Icons with conditions |

**Used by:** SchemaProperty.options, dialog/properties.py (property picker)

---

### ButtonMapping (line 26)
Button to property mapping from the `<buttons>` section.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `button_id` | int | required | Skin button ID |
| `property_name` | str | required | Property name to act on |
| `suffix` | bool | False | If True, append property_suffix at runtime |
| `title` | str | "" | Dialog title |
| `show_none` | bool | True | Whether to show "None" option |
| `show_icons` | bool | True | Show icons in select dialog (useDetails=True) |
| `type` | str | "" | "widget", "background", "toggle", or "options" - overrides property type |
| `requires` | str | "" | Property that must be set first - overrides property requires |

**Used by:** PropertySchema.buttons, dialog/properties.py

**Note:** `type` and `requires` on buttons take precedence over the property definition. This allows buttons to work without a matching property definition (e.g., toggle buttons).

---

### SchemaProperty (line 40)
A property definition from the schema.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | str | required | Property name |
| `template_only` | bool | False | If True, only used in templates (not editable) |
| `requires` | str | "" | Property name that must have a value first |
| `options` | list[SchemaOption] | [] | Available options for select type |
| `type` | str | "" | "widget", "background", "toggle", or "options" |

**Used by:** PropertySchema, dialog/properties.py, builders/template.py

---

### FallbackRule (line 51)
A single fallback rule with condition.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `value` | str | required | Fallback value |
| `condition` | str | "" | Property condition (empty = default/unconditional) |

**Used by:** PropertyFallback.rules

---

### PropertyFallback (line 59)
Fallback configuration for a property.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `property_name` | str | required | Property this fallback applies to |
| `rules` | list[FallbackRule] | [] | Fallback rules in order |

**Used by:** PropertySchema.fallbacks, builders/includes.py

---

### PropertySchema (line 67)
Complete property schema container.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `properties` | dict[str, SchemaProperty] | {} | All properties by name |
| `fallbacks` | dict[str, PropertyFallback] | {} | Fallback rules by property name |
| `buttons` | dict[int, ButtonMapping] | {} | Button mappings by button ID |

**Methods:**
- `get_property(name)` → SchemaProperty\|None - Get property by name (line 75)
- `get_button(button_id)` → ButtonMapping\|None - Get button mapping by ID (line 79)
- `get_property_for_button(button_id)` → tuple[SchemaProperty\|None, ButtonMapping\|None] - Get property and button mapping for a button ID (line 83)

**Used by:** config.py, dialog/properties.py, loaders/property.py, builders/includes.py

---

## Test Candidates

1. `PropertySchema.get_property()` lookup
2. `PropertySchema.get_property_for_button()` lookup
3. ButtonMapping suffix handling
