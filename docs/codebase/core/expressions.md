# expressions.py

**Path:** `resources/lib/skinshortcuts/expressions.py`
**Purpose:** $MATH and $IF expression parsing for templates.

***

## $MATH Expressions

Arithmetic with property variables.

```
$MATH[mainmenuid * 1000 + 600 + id]
```

**Operators:** `+`, `-`, `*`, `/`, `//`, `%`, `()`

### evaluate_math(expr, properties) → str

Evaluate expression, return result as string.

***

## $IF Expressions

Conditional value selection.

```
$IF[condition THEN trueValue]
$IF[condition THEN trueValue ELSE falseValue]
$IF[cond1 THEN val1 ELIF cond2 THEN val2 ELSE val3]
```

Uses same condition syntax as `conditions.py`.

### evaluate_if(expr, properties) → str

Evaluate conditions in order, return first matching value.

***

## Processing Functions

| Function | Description |
|----------|-------------|
| `process_math_expressions(text, props)` | Process all `$MATH[...]` in text |
| `process_if_expressions(text, props)` | Process all `$IF[...]` in text |
