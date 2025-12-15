# loaders/base.py

**Path:** `resources/lib/skinshortcuts/loaders/base.py`
**Lines:** 152
**Purpose:** Base loader functionality and XML parsing utilities shared by all loaders.

---

## Overview

Provides common XML parsing functions and suffix transformation utilities used across all loader modules.

---

## Constants

### NO_SUFFIX_PROPERTIES (line 15)
Properties that should never have suffix transforms applied.

Values: `name`, `default`, `menu`, `index`, `id`, `idprefix`

**Used by:** `apply_suffix_transform()`, `apply_suffix_to_from()`

---

## Functions

### apply_suffix_transform(text, suffix) (line 28)
Apply suffix transform to property names in conditions.

**Parameters:**
- `text` - Condition string like `"widgetType=custom"`
- `suffix` - Suffix to apply like `".2"`

**Returns:** Transformed string like `"widgetType.2=custom"`

**Behavior:**
- Transforms property names before `=` or `~` operators
- Preserves values after operators
- Skips properties in `NO_SUFFIX_PROPERTIES`

**Used by:** builders/template.py, loaders/template.py

---

### apply_suffix_to_from(from_value, suffix) (line 47)
Apply suffix to a `from` attribute value.

**Parameters:**
- `from_value` - Property name like `"widgetPath"`
- `suffix` - Suffix to apply like `".2"`

**Returns:** Transformed string like `"widgetPath.2"`

**Special cases:**
- Bracket syntax: `"preset[attr]"` → `"preset.2[attr]"`
- Dot syntax (old preset lookups): Not transformed
- NO_SUFFIX_PROPERTIES: Not transformed

**Used by:** builders/template.py

---

### parse_xml(path, expected_root, error_class) (line 76)
Parse XML file and validate root element.

**Parameters:**
- `path` - Path to XML file
- `expected_root` - Expected root element name
- `error_class` - ConfigError subclass to raise

**Returns:** ET.Element root

**Raises:** `error_class` if file not found, parse error, or wrong root element

**Used by:** All loader modules

---

### get_text(elem, child, default="") (line 96)
Get text content of child element.

**Parameters:**
- `elem` - Parent ET.Element
- `child` - Child tag name
- `default` - Default if not found

**Returns:** Stripped text content or default

**Used by:** All loader modules

---

### get_attr(elem, attr, default="") (line 104)
Get attribute value from element.

**Parameters:**
- `elem` - ET.Element
- `attr` - Attribute name
- `default` - Default if not found

**Returns:** Stripped attribute value or default

**Used by:** All loader modules

---

### get_int(elem, child, default=None) (line 109)
Get integer from child element text.

**Parameters:**
- `elem` - Parent ET.Element
- `child` - Child tag name
- `default` - Default if not found or invalid

**Returns:** Integer value or default

**Used by:** loaders/widget.py, loaders/menu.py

---

### get_bool(elem, attr, default=False) (line 120)
Get boolean from attribute value.

**Parameters:**
- `elem` - ET.Element
- `attr` - Attribute name
- `default` - Default if not found

**Returns:** True if value is "true" (case-insensitive)

**Used by:** loaders/menu.py, loaders/widget.py

---

### parse_content(elem) (line 128)
Parse a content reference element.

**Parameters:**
- `elem` - ET.Element with content attributes

**Returns:** Content model or None if no source attribute

**Parses attributes:** source, target, path, condition, visible, icon, label, folder

**Used by:** loaders/menu.py, loaders/widget.py, loaders/background.py

---

## Dead Code Analysis

All functions appear to be in active use.

---

## Test Candidates

1. `apply_suffix_transform()` with various operators and NO_SUFFIX_PROPERTIES
2. `apply_suffix_to_from()` with bracket syntax and dot syntax
3. `parse_xml()` error handling (file not found, parse error, wrong root)
4. `get_bool()` with various truthy/falsy values
5. `parse_content()` with complete and minimal attributes
