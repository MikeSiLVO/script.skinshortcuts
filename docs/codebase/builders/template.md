# builders/template.py

**Path:** `resources/lib/skinshortcuts/builders/template.py`
**Lines:** 828
**Purpose:** Build Kodi include XML from templates.xml and menu data.

---

## Overview

The TemplateBuilder is the most complex part of the build system. It processes templates defined in templates.xml, iterating over menu items and generating controls, properties, and variables with substitutions.

---

## Regex Patterns (lines 31-33)

| Pattern | Purpose |
|---------|---------|
| `_PROPERTY_PATTERN` | Matches `$PROPERTY[name]` |
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

### _collect_assigned_templates() → set[str] (line 53)
Collect template include names assigned to menu items.

**Behavior:**
- Scans all menu item properties for `$INCLUDE[skinshortcuts-template-*]` pattern
- Used by `templateonly="auto"` to skip unassigned templates
- Returns set of include names (e.g., `skinshortcuts-template-MovieWidgets`)

---

### build() → ET.Element (line 73)
Build all template includes and variables.

**Behavior:**
- Templates with same include name are merged
- Variables are output at root level (siblings to includes)
- Empty includes get a `<description>` element to avoid Kodi log warnings
- `templateonly="true"` templates are never output
- `templateonly="auto"` templates are skipped if not in `_assigned_templates`
- Output: `<includes>` containing `<variable>` and `<include>` elements

**Used by:** builders/includes.py

---

### _build_template_into(template, include, variables_list) (line 126)
Build template controls and variables for all matching menu items.

**Behavior:**
- Iterates all menus and items
- Skips disabled items
- Checks template conditions
- Builds context, controls, and variables per item

---

### write(path, indent=True) (line 826)
Write template includes to file.

---

## Context Building

### _build_context(template, item, idx, menu) (line 171)
Build property context for a menu item.

**Context built in order:**
1. Menu default properties + item properties (merged, item overrides defaults)
2. Built-in properties: `index`, `name`, `menu`, `idprefix`, `id`
3. Fallback values (applied early so template conditions can use them)
4. Template properties
5. Template vars
6. Preset references (set raw values from lookup tables)
7. Property group references (may transform/derive from preset values)

---

### _apply_fallbacks(item, context) (line 525)
Apply property fallbacks for missing properties from PropertySchema.

**Behavior:**
- Collects suffixes in use (e.g., `.2`, `.3`)
- Applies fallback rules for each suffix variant
- Transforms conditions to use suffixed property names

---

### _resolve_property(prop, item, context) (line 340)
Resolve a property value.

**Modes:**
- Condition check first (skip if not met)
- `from_source` - Get from another property
- Literal value with `$PROPERTY[...]` substitution

---

### _substitute_property_refs(text, item, context) (line 361)
Substitute `$PROPERTY[...]` in text during context building.

Checks context first, then item properties.

---

### _resolve_var(var, item, context) (line 379)
Resolve a var (first matching condition wins).

---

### _get_from_source(source, item, context) (line 395)
Get value from a source (built-in, item property, or preset).

**Source resolution order:**
1. Preset lookup: `preset[attr]` or `preset.attr`
2. Built-ins: `index`, `name`, `menu`, `id`, `idprefix`
3. Context values
4. Item properties

---

### _lookup_preset(preset, attr, item, context) (line 429)
Look up a value from a preset by evaluating conditions.

First matching condition wins. Default row (no condition) is fallback.

---

### _apply_property_group(prop_group, item, context, suffix="") (line 446)
Apply properties from a property group to context.

**Behavior:**
- Applies suffix transforms to `from_source` and conditions
- Only sets property if not already in context (first match wins)
- Supports suffix transforms for Widget 1/2 reuse

---

### _apply_preset(ref, item, context) (line 485)
Apply preset values directly as properties.

**Behavior:**
- Suffix is applied to CONDITIONS, not preset name
- Evaluates conditions and sets all matched row values
- Only sets if not already in context

---

## Variable Building

### _build_variable(var_def, context, item) (line 223)
Build a Kodi `<variable>` element from a VariableDefinition.

**Behavior:**
- Checks variable condition (if any)
- Uses `output` attribute or original name for output name
- Substitutes `$PROPERTY[...]` in name and all content

---

### _build_variable_group(group_ref, context, item, variables_list) (line 260)
Build variables from a variableGroup reference.

**Behavior:**
- Checks group-level condition
- Processes nested variableGroup references first (recursively)
- Applies suffix transforms to conditions
- Builds each matching variable from global definitions

---

### _substitute_variable_content(elem, context, item) (line 317)
Substitute `$PROPERTY[...]` in variable content recursively.

Processes text, tail, attributes, and children.

---

## Control Processing

### _process_controls(controls, context, item, menu) (line 642)
Process controls XML, applying substitutions.

Returns deep copy with all substitutions applied.

---

### _process_element(elem, context, item, menu) (line 659)
Recursively process an element.

**Handles:**
- `<skinshortcuts>visibility</skinshortcuts>` → `<visible>` condition
- `<skinshortcuts include="name"/>` → Expanded include (unwrapped)
- `<skinshortcuts include="name" wrap="true"/>` → Expanded as Kodi `<include>` element
- `<skinshortcuts include="name" condition="propName"/>` → Conditional include (only expanded if property exists)
- `$PROPERTY[...]` substitution in text/attributes
- `$INCLUDE[...]` in text → Kodi `<include>` element

---

### _handle_include_substitution(elem) (line 733)
Convert `$INCLUDE[...]` in element text to Kodi `<include>` child elements.

**Behavior:**
- Searches element text for `$INCLUDE[name]` pattern
- Creates a Kodi `<include>name</include>` child element
- Used for template includes assigned via widget paths (e.g., `$INCLUDE[skinshortcuts-template-*]`)

---

### _handle_skinshortcuts_include(elem, context, item, menu) (line 750)
Handle `<skinshortcuts include="..."/>` element replacements.

**Behavior:**
- Finds children marked with `_skinshortcuts_include` attribute
- If `wrap="true"` was set, outputs as Kodi `<include name="...">` element
- Otherwise, unwraps and inserts the include's children directly
- Elements marked for removal (condition not met) are cleaned up after processing

---

### _substitute_text(text, context, item, menu) (line 804)
Substitute `$PROPERTY[...]` in text.

Checks context first, then item properties.

---

## Condition Evaluation

### _apply_suffix_to_condition(condition, suffix) (line 574)
Apply suffix to property names in condition for Widget 1/2 reuse.

Does not suffix built-ins (`index`, `name`, `menu`, `id`, `idprefix`).

---

### _check_conditions(conditions, item) (line 595)
Check if all template conditions match (ANDed together).

---

### _get_property_value(prop_name, item, context) (line 599)
Get a property value, checking context first then item properties.

---

### _eval_condition(condition, item, context) (line 610)
Evaluate a condition against a menu item.

**Behavior:**
- Expands expressions first (`$EXP[name]`)
- Merges context with item properties (context takes precedence)
- Uses `evaluate_condition()` from conditions module

---

### _expand_expressions(condition) (line 629)
Expand `$EXP[name]` references in a condition.

Recursively expands nested expressions.

---

## Test Candidates

1. `_build_context()` property precedence ordering
2. `_resolve_property()` with from_source and conditions
3. `_apply_preset()` with conditions and suffix
4. `_expand_expressions()` recursive expansion
5. `_process_controls()` with various substitution patterns
6. `_handle_skinshortcuts_include()` with wrap vs unwrap
7. Variable building with suffix transforms
8. `_apply_fallbacks()` with suffix transforms
