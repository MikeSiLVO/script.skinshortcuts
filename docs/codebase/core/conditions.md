# conditions.py

**Path:** `resources/lib/skinshortcuts/conditions.py`
**Purpose:** Property-based condition evaluation.

***

## Overview

Evaluates conditions using a simple expression language. Used for option filtering, fallbacks, and template conditionals.

***

## evaluate_condition(condition, properties) → bool

Main entry point. Returns True if condition matches (empty conditions return True). A comparison splits at its first `=` or `~`, so the value may contain either.

***

## lookup(name, *sources) → str | None

A property value by exact name across the sources in order, then ignoring case in the same order; `None` when absent. Every property read in conditions and the template builder goes through it.

***

## suffix_property(name, suffix) → str

Appends the suffix to one property name: `"widgetPath"` + `".2"` → `"widgetPath.2"`. Template `from` values and iterate `$PROPERTY[...]` references go through it, as does every name `suffix_condition` rewrites. Leaves alone:

- `NO_SUFFIX_PROPERTIES` built-ins (`name`, `label`, `disabled`, `default`, `menu`, `index`, `id`, `idprefix`, `suffix`), in any case
- names that already carry a `.N` slot

***

## suffix_condition(condition, suffix) → str

Suffixes every property name the evaluator would read: `=`, `~`, `EMPTY`, `IN` and bare checks. Normalizes keywords and expands compact OR first, then walks the same split the evaluator uses. Names go through `suffix_property`; also left alone:

- unexpanded `$...[...]` references
- `{NOSUFFIX:...}` content, returned wrapped in brackets

***

## Expression Language

### Comparison Operators

| Symbol | Keyword | Example |
|--------|---------|---------|
| *(none)* | - | `widgetPath` (truthy check) |
| `=` | `EQUALS` | `widgetType=movies` (a `true`/`false` right side compares case-insensitively) |
| `~` | `CONTAINS` | `widgetPath~library` |
| - | `EMPTY` | `widgetPath EMPTY` |
| - | `IN` | `widgetType IN movies,episodes,tvshows` |

### Logical Operators

| Symbol | Keyword | Example |
|--------|---------|---------|
| `+` | `AND` | `cond1 + cond2` |
| `\|` | `OR` | `cond1 \| cond2` |
| `!` | `NOT` | `!cond` |
| `[]` | - | `![cond1 \| cond2]` (grouping) |

### Compact OR

`prop=v1 | v2 | v3` expands to `prop=v1 | prop=v2 | prop=v3`

**Note:** `!a + b` evaluates as `(!a) AND b`. Use brackets for grouped negation.
