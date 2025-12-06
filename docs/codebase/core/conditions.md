# conditions.py

**Path:** `resources/lib/skinshortcuts/conditions.py`
**Lines:** 192
**Purpose:** Condition evaluation utilities for property-based conditions.

---

## Overview

Evaluates property conditions using a simple expression language. Used throughout the codebase for filtering options, applying fallbacks, and template conditionals.

---

## Expression Language

| Syntax | Meaning | Example |
|--------|---------|---------|
| `prop=value` | Equality | `widgetType=movies` |
| `prop~value` | Contains | `widgetPath~library` |
| `cond1 + cond2` | AND | `widgetType=movies + widgetPath~library` |
| `cond1 \| cond2` | OR | `widgetType=movies \| widgetType=tvshows` |
| `!cond` | NOT | `!widgetType=custom` |
| `[cond]` | Grouping | `![widgetType=movies \| widgetType=tvshows]` |
| `prop=v1 \| v2 \| v3` | Compact OR | Expands to `prop=v1 \| prop=v2 \| prop=v3` |

---

## Functions

### evaluate_condition(condition, properties) → bool (line 109)
Main entry point - evaluate a condition against property values.

**Parameters:**
- `condition` - Condition string to evaluate
- `properties` - Dict of property name → value to check against

**Returns:** True if condition matches, False otherwise. Empty/None conditions return True.

**Used by:**
- `dialog/base.py` - Fallback evaluation
- `dialog/properties.py` - Option filtering
- `dialog/pickers.py` - Shortcut filtering
- `dialog/subdialogs.py` - Onclose condition evaluation
- `builders/template.py` - Template conditionals
- `loaders/__init__.py` - Re-exported for backwards compatibility

---

### expand_compact_or(condition) → str (line 21)
Expand compact OR syntax to full form.

**Example:**
```
"widgetType=movies | episodes | tvshows"
→ "widgetType=movies | widgetType=episodes | widgetType=tvshows"
```

---

## Internal Functions

### _split_preserving_brackets(text, delimiter) → list[str] (line 57)
Split text by delimiter but preserve content inside brackets.

### _expand_or_segment(segment) → str (line 82)
Expand a single OR segment.

### _evaluate_expanded(condition, properties) → bool (line 125)
Evaluate an expanded condition (handles AND, OR, NOT, grouping).

### _evaluate_single(condition, properties) → bool (line 151)
Evaluate a single atomic condition (property=value or property~value).

---

## Test Candidates

1. `evaluate_condition()` with equality (`=`)
2. `evaluate_condition()` with contains (`~`)
3. `evaluate_condition()` with AND (`+`)
4. `evaluate_condition()` with OR (`|`)
5. `evaluate_condition()` with NOT (`!`)
6. `evaluate_condition()` with grouping (`[]`)
7. `expand_compact_or()` expansion
8. Edge cases: empty conditions, missing properties
