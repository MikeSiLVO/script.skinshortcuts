# loaders/base.py

**Path:** `resources/lib/skinshortcuts/loaders/base.py`
**Purpose:** Shared XML parsing utilities for all loaders.

***

## Suffix Transform Functions

### apply_suffix_to_from(from_value, suffix) → str

Transform `from` attribute values by appending the suffix to the whole value. E.g. `"widgetPath"` + `".2"` → `"widgetPath.2"`. Returns the value unchanged when it is in `NO_SUFFIX_PROPERTIES` (conditions.py). No bracket/subscript parsing is performed.

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
