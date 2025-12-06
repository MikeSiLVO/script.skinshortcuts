# builders/template.py

**Path:** `resources/lib/skinshortcuts/builders/template.py`
**Lines:** 785
**Purpose:** Build Kodi include XML from templates.xml and menu data.

---

## Overview

The TemplateBuilder is the most complex part of the build system. It processes templates defined in templates.xml, iterating over menu items and generating controls, properties, and variables with substitutions.

---

## Regex Patterns (lines 31-33)

| Pattern | Purpose |
|---------|---------|
| `_PROPERTY_PATTERN` | Matches `$PROPERTY[name]` |
| `_INCLUDE_PATTERN` | Matches `$INCLUDE[name]` |
| `_EXP_PATTERN` | Matches `$EXP[name]` (expressions) |

---

## TemplateBuilder Class (line 36)

### __init__(schema, menus, container="9000", property_schema=None) (line 39)
Initialize builder.

**Parameters:**
- `schema` - TemplateSchema from templates.xml
- `menus` - list[Menu] to build from
- `container` - Container ID for visibility conditions (default "9000")
- `property_schema` - Optional PropertySchema for fallbacks

---

### build() → ET.Element (line 53)
Build all template includes and variables.

**Behavior:**
- Templates with same include name are merged
- Variables are output at root level (siblings to includes)
- Empty includes get a `<description>` element to avoid Kodi log warnings
- Output: `<includes>` containing `<variable>` and `<include>` elements

**Used by:** builders/includes.py

---

### write(path, indent=True) (line 762)
Write template includes to file.

---

## Context Building

### _build_context(template, item, idx, menu) (line 127)
Build property context for a menu item.

**Context contains:**
1. Menu default properties
2. Item properties (override defaults)
3. Built-in properties: `index`, `name`, `menu`, `idprefix`, `id`
4. Fallback values
5. Template properties
6. Template vars
7. Preset values
8. Property group values

---

### _apply_fallbacks(item, context) (line 476)
Apply property fallbacks for missing properties from PropertySchema.

---

### _resolve_property(prop, item, context) (line 291)
Resolve a property value.

**Modes:**
- Condition check first
- `from_source` - Get from another property
- Literal value with `$PROPERTY[...]` substitution

---

### _resolve_var(var, item, context) (line 330)
Resolve a var (first matching value wins).

---

### _get_from_source(source, item, context) (line 346)
Get value from a source.

**Sources:**
- Preset lookup: `preset[attr]` or `preset.attr`
- Built-ins: `index`, `name`, `menu`, `id`, `idprefix`
- Context values
- Item properties

---

### _lookup_preset(preset, attr, item, context) (line 380)
Look up a value from a preset by evaluating conditions.

---

### _apply_property_group(prop_group, item, context, suffix="") (line 397)
Apply properties from a property group to context.

Supports suffix transforms for Widget 1/2 reuse.

---

### _apply_preset(ref, item, context) (line 436)
Apply preset values directly as properties.

Evaluates conditions and sets all matched row values.

---

## Variable Building

### _build_variable(var_def, context, item) (line 189)
Build a Kodi `<variable>` element from a VariableDefinition.

**Behavior:**
- Checks variable condition (if any)
- Uses `output` attribute or original name for output name
- Substitutes `$PROPERTY[...]` in name and all content

---

### _build_variable_group(group_ref, context, item, variables_list) (line 226)
Build variables from a variableGroup reference.

**Behavior:**
- Checks group-level condition
- Processes nested variableGroup references first (recursively)
- Applies suffix transforms to conditions
- Builds each matching variable from global definitions

---

### _substitute_variable_content(elem, context, item) (line 283)
Substitute `$PROPERTY[...]` in variable content recursively.

---

## Control Processing

### _process_controls(controls, context, item, menu) (line 573)
Process controls XML, applying substitutions.

Returns deep copy with all substitutions applied.

---

### _process_element(elem, context, item, menu) (line 589)
Recursively process an element.

**Handles:**
- `<skinshortcuts>visibility</skinshortcuts>` → `<visible>` condition
- `<skinshortcuts include="name"/>` → Expanded include
- `<skinshortcuts include="name" condition="propName"/>` → Conditional include (only expanded if property exists)
- `$PROPERTY[...]` substitution in text/attributes

---

### _handle_include_substitution(elem, context, item, menu) (line 649)
Handle `$INCLUDE[...]` substitutions.

**Behavior:**
- If include is defined in templates.xml, expand inline
- Otherwise, output literal Kodi `<include>name</include>` element

---

### _handle_skinshortcuts_include(elem, context, item, menu) (line 703)
Handle `<skinshortcuts include="..."/>` element replacements.

**Conditional includes:**
Elements marked for removal (condition not met) are cleaned up after processing.

---

### _substitute_text(text, context, item, menu) (line 740)
Substitute `$PROPERTY[...]` in text.

---

## Condition Evaluation

### _check_conditions(conditions, item) (line 526)
Check if all template conditions match (ANDed together).

---

### _eval_condition(condition, item, context) (line 541)
Evaluate a condition with expression expansion.

Uses `evaluate_condition()` from loaders/property.py.

---

### _expand_expressions(condition) (line 560)
Expand `$EXP[name]` references recursively.

---

### _apply_suffix_to_condition(condition, suffix) (line 505)
Apply suffix to property names in condition for Widget 1/2 reuse.

---

## Dead Code Analysis

All code appears to be in active use.

---

## Test Candidates

1. `_build_context()` property precedence ordering
2. `_resolve_property()` with from_source and conditions
3. `_apply_preset()` with conditions and suffix
4. `_expand_expressions()` recursive expansion
5. `_process_controls()` with various substitution patterns
6. `_handle_include_substitution()` template vs literal include output
7. Variable building with suffix transforms
