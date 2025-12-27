# conditions.py

**Path:** `resources/lib/skinshortcuts/conditions.py`
**Purpose:** Condition evaluation utilities for property-based conditions.

***

## Overview

Evaluates property conditions using a simple expression language. Used throughout the codebase for filtering options, applying fallbacks, and template conditionals.

***

## Expression Language

Supports both symbol and keyword forms for all operators.

### Comparison Operators

| Symbol | Keyword | Meaning | Example |
|--------|---------|---------|---------|
| *(none)* | - | Truthy (has value) | `widgetPath` |
| `=` | `EQUALS` | Equality | `widgetType=movies` or `widgetType EQUALS movies` |
| `=` (empty) | - | Empty string check | `suffix=` |
| `~` | `CONTAINS` | Contains substring | `widgetPath~library` or `widgetPath CONTAINS library` |
| - | `EMPTY` | Is empty/not set | `widgetPath EMPTY` |
| - | `IN` | Value in list | `widgetType IN movies,episodes,tvshows` |

### Logical Operators

| Symbol | Keyword | Meaning | Example |
|--------|---------|---------|---------|
| `+` | `AND` | Logical AND | `cond1 + cond2` or `cond1 AND cond2` |
| `\|` | `OR` | Logical OR | `cond1 \| cond2` or `cond1 OR cond2` |
| `!` | `NOT` | Negation | `!cond` or `NOT cond` |
| `[]` | - | Grouping | `![cond1 \| cond2]` |

### Compact OR

```text
prop=v1 | v2 | v3  →  prop=v1 | prop=v2 | prop=v3
```

**Note:** Negation applies to the immediately following term. `!a + b` evaluates as `(!a) AND b`, not `!(a + b)`. Use brackets for grouped negation: `![a + b]`.

***

## Functions

### evaluate_condition(condition, properties) → bool

Main entry point - evaluate a condition against property values.

**Parameters:**

* `condition` - Condition string to evaluate
* `properties` - Dict of property name → value to check against

**Returns:** True if condition matches, False otherwise. Empty/None conditions return True.

**Process:**

1. Normalize keywords to symbols (`AND`→`+`, `OR`→`|`, etc.)
2. Expand compact OR syntax
3. Evaluate expanded condition recursively

**Used by:**

* `dialog/` modules - Option filtering, fallbacks
* `builders/template.py` - Template conditionals
* `expressions.py` - $IF expression evaluation
* `loaders/__init__.py` - Re-exported for convenience

***

### expand_compact_or(condition) → str

Expand compact OR syntax to full form.

**Example:**

```text
"widgetType=movies | episodes | tvshows"
→ "widgetType=movies | widgetType=episodes | widgetType=tvshows"
```

***

## Internal Functions

### `_normalize_keywords(condition)` → str

Convert keyword operators to symbol equivalents. Uses word boundaries to avoid replacing within values.

**Conversions:** `AND`→`+`, `OR`→`|`, `NOT`→`!`, `EQUALS`→`=`, `CONTAINS`→`~`

### `_split_preserving_brackets(text, delimiter)` → list[str]

Split text by delimiter but preserve content inside brackets.

### `_expand_or_segment(segment)` → str

Expand a single OR segment with property cascading.

### `_evaluate_expanded(condition, properties)` → bool

Evaluate an expanded condition. Handles AND, OR, NOT, and grouping recursively.

### `_evaluate_single(condition, properties)` → bool

Evaluate a single atomic condition:

* `property` → True if property has non-empty value (truthy)
* `property EMPTY` → True if property is empty/not set
* `property IN a,b,c` → True if property value is in list
* `property=value` → True if property equals value
* `property~value` → True if property contains value

***

## Related Modules

* `expressions.py` - Uses `evaluate_condition()` for $IF expressions
* `builders/template.py` - Uses for template/preset conditionals
* `dialog/` modules - Uses for option filtering
