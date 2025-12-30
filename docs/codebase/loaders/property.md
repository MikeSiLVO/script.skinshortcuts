# loaders/property.py

**Path:** `resources/lib/skinshortcuts/loaders/property.py`
**Purpose:** Load property schema from properties.xml with include expansion.

***

## Overview

Parses properties.xml defining custom properties, button mappings, and fallback rules.

**Note:** Condition evaluation is in `conditions.py`.

***

## Public Functions

### load_properties(path) → PropertySchema

Load property schema. Returns PropertySchema containing:
- `properties` - dict of SchemaProperty by name
- `fallbacks` - dict of PropertyFallback by property name
- `buttons` - dict of ButtonMapping by button ID

***

## PropertyLoader Class

### load() → PropertySchema

Parse the property schema with include expansion.

***

## Internal Parsers

| Function | Parses |
|----------|--------|
| `_parse_includes` | `<include name="...">` definitions |
| `_expand_include` | `<include content="..." />` references with suffix |
| `_parse_property` | Property with name, type, requires, options |
| `_parse_button` | Button with id, property, suffix, title |
| `_parse_options` | Options list with includes |
| `_parse_option` | Option with value, label, condition, icons |
| `_parse_fallback` | Fallback with when conditions and default |

**Include suffix:** Suffix transforms condition attributes when expanding includes.

**Button suffix inheritance:** Buttons inherit suffix from parent `<buttons>` or `<group>`.

***

## XML Reference

See [skinning/properties.md](../../skinning/properties.md) for full XML documentation.
