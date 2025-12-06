# Suffix System Audit

## Purpose of Suffix

The suffix system (e.g., `.2`) allows a single menu item to have multiple widget slots. Instead of defining separate properties for each slot, we use a suffix to namespace them:

- Widget 1: `widget`, `widgetPath`, `widgetStyle`, `widgetArt`
- Widget 2: `widget.2`, `widgetPath.2`, `widgetStyle.2`, `widgetArt.2`

This allows reusing the same dialog UI, templates, and property definitions for multiple widgets.

---

## Suffix Usage by Area

### 1. Subdialog Definition (menu.xml)

**File:** `models/menu.py:329`, `loaders/menu.py:163-174`

**What:** `SubDialog.suffix` attribute parsed from `<subdialog suffix=".2">`

**Why:** Tells the dialog system which property namespace to use when this subdialog is opened.

**Example:**
```xml
<subdialog mode="widget2" suffix=".2">
```

---

### 2. Dialog Context

**File:** `dialog/base.py:126, 144-158, 161-172, 222-228, 557-563`

**What:**
- `self.property_suffix` - stored on dialog instance
- `_suffixed_name(name)` - helper to apply suffix to a base name
- `_get_item_property(item, name)` - always applies suffix via `_suffixed_name`
- `skinshortcuts-suffix` window property for skin visibility conditions

**Why:** When in widget2 subdialog, all property operations should target `.2` properties.

**Problem:** `_get_item_property` ALWAYS applies suffix, but sometimes caller already has suffixed name.

---

### 3. Button Schema

**File:** `models/property.py:32`, `loaders/property.py:347-361`

**What:** `ButtonMapping.suffix: bool` - parsed from `<button suffix="true">`

**Why:** Tells the button handler whether this button should be context-aware. When `suffix=True`, button 309 acts on `widget.2` in widget2 mode vs `widget` in widget1 mode.

---

### 4. Property Button Handler

**File:** `dialog/properties.py:119-135`

**What:** Applies `self.property_suffix` to property name and requires attribute when `button.suffix=True`

**Why:** Determines the effective property name based on button config and dialog context.

**Code:**
```python
if button.suffix and self.property_suffix:
    requires_name = f"{requires_name}{self.property_suffix}"
    prop_name = f"{prop.name}{self.property_suffix}"
```

---

### 5. Widget/Background Property Setters

**File:** `dialog/properties.py:222-242, 248-265`

**What:** Parses prefix to extract suffix, builds related property names with suffix

**Why:** When setting `widget.2`, also need to set `widgetPath.2`, `widgetLabel.2`, etc.

**Code:**
```python
# Parse prefix: "widget.2" -> ("widget", ".2")
if "." in prefix:
    base, suffix = prefix.rsplit(".", 1)
    suffix = f".{suffix}"
related = {
    f"{base}Label{suffix}": ...,
    f"{base}Path{suffix}": ...,
}
```

**Problem:** This duplicates suffix logic. The prefix already contains the suffix, and this re-extracts it.

---

### 6. Item Property Storage

**File:** `dialog/items.py:346-404`

**What:** `_set_item_property(item, name, value, related, apply_suffix=True)`

**Why:** Stores properties on menu items. Has `apply_suffix` flag because sometimes caller provides base name (wants auto-suffix) and sometimes provides already-suffixed name.

**Problem:** Dual mode with flag is confusing. Currently most callers pass `apply_suffix=False` because they've already applied suffix.

---

### 7. Template Building (Build Time)

**File:** `builders/template.py:183-186, 233-266, 415-432, 458-477, 520-538`
**File:** `loaders/base.py:28-73`

**What:**
- `apply_suffix_transform(condition, suffix)` - transforms `widgetArt=Poster` to `widgetArt.2=Poster`
- `apply_suffix_to_from(from_value, suffix)` - transforms `widgetPath` to `widgetPath.2`
- Used in property groups, presets, variable groups

**Why:** Templates define widget UI once, then reuse for Widget 1 and Widget 2 by applying suffix transforms. The skin's templates.xml has entries like:
```xml
<variableGroup name="listWidgetVars" suffix=".2"/>
<preset name="panelArtDimensions.2"/>
```

This is BUILD-TIME suffix application for template reuse.

---

### 8. Property Include Expansion

**File:** `loaders/property.py:261-291`

**What:** When expanding `<include content="ArtOptions" suffix=".2"/>`, applies suffix transform to condition attributes.

**Why:** Allows reusing option definitions with transformed conditions.

---

### 9. Template Schema References

**File:** `models/template.py:91, 104, 184`, `loaders/template.py:424-460`

**What:** `PropertyGroupReference.suffix`, `PresetReference.suffix`, `VariableGroupReference.suffix`

**Why:** Template references can specify suffix for Widget 1/2 reuse.

---

## Two Distinct Suffix Contexts

### A. Dialog Runtime Suffix (property_suffix)

**When:** User is in widget2 subdialog mode
**What:** `self.property_suffix = ".2"`
**Purpose:** Property reads/writes target `.2` properties
**Affected:** Button handlers, property getters/setters

### B. Build-Time Suffix (template suffix)

**When:** Building includes from templates
**What:** `suffix=".2"` on template references
**Purpose:** Transform conditions/from attributes for Widget 2 template output
**Affected:** Template builder, property/variable groups, presets

These are related but distinct:
- Runtime suffix determines which properties the dialog edits
- Build-time suffix determines how templates generate XML for Widget 2

---

## Current Problems

### 1. Mixed Responsibility in `_set_item_property`

The `apply_suffix` parameter exists because:
- Some callers use base names and want auto-suffixing
- Some callers already have suffixed names

This dual mode is confusing and error-prone.

### 2. `_get_item_property` Always Suffixes

But sometimes we have an already-suffixed name and want to read it directly. Callers work around this with `item.properties.get(prop_name, "")`.

### 3. Suffix Parsing in Widget Setters

`_set_widget_properties` parses the prefix to extract base/suffix, then rebuilds related property names. This is redundant if we had a better suffix system.

### 4. No Clear Contract

It's unclear at each layer whether names are:
- Base names (need suffix applied)
- Suffixed names (ready to use)
- Context-dependent (use dialog's suffix)

---

## Proposed Unified Approach

### Option A: Caller Always Provides Final Names

- Remove `apply_suffix` parameter from `_set_item_property`
- Remove auto-suffix from `_get_item_property`
- Callers responsible for building final property names
- `_suffixed_name()` stays as helper for when needed

**Pros:** Simple, predictable, no dual modes
**Cons:** More work for callers, must be consistent

### Option B: Storage Layer Always Applies Suffix

- `_set_item_property` and `_get_item_property` always use `self.property_suffix`
- Callers always use base names
- Need way to handle non-suffixed properties (background has `suffix="false"`)

**Pros:** Centralized suffix logic
**Cons:** Need to handle suffix="false" buttons differently

### Option C: Button Carries Suffix Context

- Button handler determines suffix once
- Pass `effective_suffix` (empty or ".2") to all downstream
- All methods accept `suffix` parameter instead of using `self.property_suffix`

**Pros:** Explicit suffix passing, clear data flow
**Cons:** More parameters to thread through

---

## Recommendation

**Option A** seems cleanest:

1. Storage layer (`_set_item_property`, `_get_item_property`) just stores/retrieves exact names given
2. Callers build the correct property name using helpers when needed
3. `_suffixed_name(base)` helper converts base name to suffixed based on `self.property_suffix`
4. Button handler determines the effective name once and passes it down

This makes the data flow explicit and removes the confusing dual mode.
