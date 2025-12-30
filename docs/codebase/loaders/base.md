# loaders/base.py

**Path:** `resources/lib/skinshortcuts/loaders/base.py`
**Purpose:** Shared XML parsing utilities for all loaders.

***

## Constants

### NO_SUFFIX_PROPERTIES

Properties that never get suffix transforms: `name`, `default`, `menu`, `index`, `id`, `idprefix`

***

## Suffix Transform Functions

### apply_suffix_transform(text, suffix) → str

Transform property names in conditions. `"widgetType=custom"` + `".2"` → `"widgetType.2=custom"`

Skips NO_SUFFIX_PROPERTIES and preserves values after operators.

### apply_suffix_to_from(from_value, suffix) → str

Transform `from` attribute values. Handles bracket syntax: `"preset[attr]"` → `"preset.2[attr]"`

***

## XML Parsing Functions

| Function | Purpose |
|----------|---------|
| `parse_xml(path, expected_root, error_class)` | Parse and validate XML root element |
| `get_text(elem, child, default="")` | Get child element text content |
| `get_attr(elem, attr, default="")` | Get attribute value |
| `get_int(elem, child, default=None)` | Get child element as integer |
| `get_bool(elem, attr, default=False)` | Get attribute as boolean |
| `parse_content(elem)` | Parse `<content>` reference element |
