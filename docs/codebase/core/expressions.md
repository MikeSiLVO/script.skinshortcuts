# expressions.py

**Path:** `resources/lib/skinshortcuts/expressions.py`
**Purpose:** Expression parsing for $MATH and $IF template features.

***

## Overview

Provides dynamic expression evaluation for templates:

* **$MATH** - Arithmetic expressions with property variables
* **$IF** - Conditional expressions using the condition parser

These replace v2's `$PYTHON` feature with a more readable, skin-friendly syntax that doesn't require an external dependency.

***

## $MATH Expressions

### Syntax

```xml
$MATH[expression]
```

Property values are automatically available as variables and converted to numbers.

### Supported Operations

| Operator | Meaning | Example |
|----------|---------|---------|
| `+` | Addition | `id + 100` |
| `-` | Subtraction | `id - 1` |
| `*` | Multiplication | `mainmenuid * 1000` |
| `/` | Division | `width / 2` |
| `//` | Floor division | `total // count` |
| `%` | Modulo | `index % 2` |
| `()` | Grouping | `(id - 1) * 100` |

### Examples

```xml
$MATH[mainmenuid * 1000 + 600 + id]
$MATH[index * 100 + 50]
$MATH[(columns - 1) * spacing]
```

***

## $IF Expressions

### Syntax

```xml
$IF[condition THEN trueValue]
$IF[condition THEN trueValue ELSE falseValue]
$IF[cond1 THEN val1 ELIF cond2 THEN val2 ELSE val3]
```

### Condition Syntax

Uses the same syntax as `conditions.py`:

* `=` or `EQUALS` - equality
* `~` or `CONTAINS` - substring
* `EMPTY` - empty check
* `IN` - list membership
* `+`/`AND`, `|`/`OR`, `!`/`NOT` - logical operators

### Examples

```xml
$IF[widgetArt~Thumb THEN true ELSE false]
$IF[widgetPath~? THEN & ELSE ?]
$IF[widgetType IN movies,episodes THEN videos ELSE music]
$IF[widgetPath NOT EMPTY THEN $PROPERTY[widgetPath] ELSE default]
```

***

## Classes

### MathEvaluator

Recursive descent parser for arithmetic expressions.

**Constructor:**

* `__init__(variables)` - Initialize with property dict

**Methods:**

* `evaluate(expr)` - Parse and evaluate expression, return result as string

**Parsing methods (internal):**

* `_parse_expression` - Handle `+`, `-` (lowest precedence)
* `_parse_term` - Handle `*`, `/`, `//`, `%`
* `_parse_unary` - Handle unary `-`, `+`
* `_parse_primary` - Handle numbers, variables, parentheses
* `_parse_number` - Parse numeric literal
* `_parse_variable` - Parse variable name and lookup value

**Error handling:** Returns original expression text on parse errors or math errors (division by zero).

***

## Functions

### evaluate_math(expr, properties) → str

Evaluate a $MATH expression.

**Parameters:**

* `expr` - Expression inside `$MATH[...]` (without wrapper)
* `properties` - Property values available as variables

**Returns:** Computed result as string (integers preferred over floats).

### evaluate_if(expr, properties) → str

Evaluate a $IF expression.

**Parameters:**

* `expr` - Expression inside `$IF[...]` (without wrapper)
* `properties` - Property values for condition evaluation

**Returns:** Selected value based on condition evaluation.

**Process:**

1. Parse THEN/ELIF/ELSE structure
2. Extract condition-value pairs
3. Evaluate conditions in order using `evaluate_condition()`
4. Return first matching value, or else value, or empty string

### process_math_expressions(text, properties) → str

Process all `$MATH[...]` expressions in text.

### process_if_expressions(text, properties) → str

Process all `$IF[...]` expressions in text.

***

## Integration

Used by `builders/template.py` in `_substitute_text`:

1. Process `$MATH[...]`
2. Process `$IF[...]`
3. Process `$PROPERTY[...]`
4. Process `$INCLUDE[...]`

***

## Related Modules

* `conditions.py` - Provides `evaluate_condition()` for $IF
* `builders/template.py` - Integrates expression processing
