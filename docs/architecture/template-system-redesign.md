# Template System Redesign

## Starting Point

### What We Have (Integration Points)

**Menus** (`menus.xml` / `models/menu.py`)
- Menus contain items
- Items have properties (key-value pairs set by user via dialog)
- Items belong to a menu with an ID
- Menus can have a container ID for visibility binding

**Backgrounds** (`models/background.py`)
- Background definitions with conditions
- Applied based on menu item properties

**Properties** (`properties.xml` / `models/property.py`)
- Schema defining what properties exist
- Options available for each property
- Fallback rules

**Output**
- Kodi XML includes (controls, variables)
- Generated per skin build

---

## Core Question

**What problem does the template system solve?**

> Given a set of menus with items that have properties, generate Kodi XML (includes, controls, variables) based on those properties.

---

## Requirements

1. **Generate Kodi XML** - controls, variables, includes
2. **Condition-based** - only generate when item properties match conditions
3. **Property substitution** - insert property values into generated XML
4. **No duplication** - define once, reuse with variations
5. **Skin-agnostic** - no hardcoded skin-specific values in the system
6. **Flexible** - works for any use case (widgets, backgrounds, navigation, info panels, etc.)

---

## Conceptual Model

### What is a Template?

A template is a **recipe** for generating Kodi XML.

It answers:
1. **When** - under what conditions should this be built?
2. **What** - what XML should be generated?
3. **How** - how should values be resolved and substituted?

### What inputs does a Template receive?

- **Menu** - the menu being processed
- **Item** - the menu item being processed
- **Item Properties** - key-value pairs from the item
- **Context** - additional values (index, computed IDs, etc.)

### What does a Template output?

- **Kodi XML elements** - controls, variables, includes
- Inserted into a named include (e.g., `<include name="widget1">`)

---

## Design Principles

### Guiding Philosophy: Mirror Kodi's Skinning Engine

Kodi skinners already know:
- `<variable>` - conditional value selection (first match wins)
- `<include>` - reusable XML chunks with parameters
- `<visible>` / `condition=` - conditional rendering
- `$VAR[name]`, `$INFO[...]`, `$PARAM[...]` - value substitution

**The template system should feel like an extension of Kodi skinning, not a separate language.**

---

### Principle 1: Write Once, Use Anywhere

A skinner should never duplicate code for slot variations.

**Bad** (current state):
```xml
<expression name="square">widgetArt=Square Poster</expression>
<expression name="square.2">widgetArt.2=Square Poster</expression>  <!-- duplicate! -->

<preset name="dimensions">...</preset>
<preset name="dimensions.2">...</preset>  <!-- duplicate! -->
```

**Good** (goal):
```xml
<expression name="square">widgetArt=Square Poster</expression>
<!-- System auto-applies suffix when building for slot 2 -->

<preset name="dimensions">
  <values condition="..." top="100" top.2="50"/>  <!-- slot-specific values inline -->
</preset>
```

---

### Principle 2: Conditions Work Like Kodi

Use familiar Kodi condition syntax where possible:
- `property=value` for equality
- `property` for existence check
- `!condition` for negation
- `condition1 + condition2` for AND
- `condition1 | condition2` for OR

---

### Principle 3: Values Flow Down, Not Up

- Global definitions (presets, expressions, variables) available to all templates
- Template-local definitions override/extend globals
- No complex inheritance chains - just simple scope

---

### Principle 4: Slots Are Context, Not Copies

A slot is a **context modifier** that affects how properties are read:
- Slot 1: reads `widgetArt`, uses `top`
- Slot 2: reads `widgetArt.2`, uses `top.2` (fallback to `top`)

The template code stays identical - the context changes.

---

### Principle 5: System Provides Machinery, Skinner Provides Content

**System provides:**
- XML parsing and generation
- Property substitution (`$PROPERTY[name]`)
- Condition evaluation
- Slot/suffix handling
- Output file writing

**Skinner provides:**
- All template definitions
- All preset values
- All condition logic
- All output names
- All control structures

**No hardcoded skin-specific values in the system.**

---

## Open Questions

### Q1: How are templates organized?

Options:
a) One templates.xml file with all templates
b) Multiple files (`templates/*.xml`)
c) Templates embedded in menus.xml

### Q2: How does a template know which menu/items to process?

Options:
a) Template declares which menu it processes (`menu="mainmenu"`)
b) Template processes all menus, conditions filter items
c) Menu declares which templates apply to it

### Q3: How are slots declared?

Options:
a) On the template (`slot="1"` or `slot="1,2"`)
b) Separate slot definitions that reference templates
c) Implicit from property names used

### Q4: What is the relationship between template and output include?

Options:
a) 1:1 - each template generates one include
b) N:1 - multiple templates can contribute to one include
c) 1:N - one template can generate multiple includes

### Q5: How should aggregate builds work?

Some outputs need data from ALL items (e.g., preload container with all paths).

Options:
a) Special template mode (`build="aggregate"`)
b) Separate aggregate template type
c) Post-processing step

---

## Strawman Syntax

```xml
<templates>
  <!-- Reusable value definitions -->
  <preset name="dimensions">
    <values condition="artType=poster" width="200" height="300" top="100" top.2="50"/>
    <values condition="artType=landscape" width="400" height="225" top="150" top.2="75"/>
    <values width="400" height="225" top="150" top.2="75"/>
  </preset>

  <!-- Template definition -->
  <template name="panel" include="HomePanel" slot="1,2">
    <!-- When to build -->
    <condition>panelPath</condition>
    <condition>panelStyle=Panel</condition>

    <!-- Values to resolve -->
    <preset name="dimensions"/>

    <!-- What to generate -->
    <controls>
      <control type="panel" id="$PROPERTY[id]">
        <top>$PROPERTY[top]</top>
        <width>$PROPERTY[width]</width>
        <height>$PROPERTY[height]</height>
        <content>$PROPERTY[panelPath]</content>
      </control>
    </controls>
  </template>
</templates>
```

---

## Next Steps

1. Answer open questions through discussion
2. Define concrete syntax
3. Define data model
4. Define builder algorithm
5. Implement
6. Migrate existing templates

---

## Discussion Notes

### Decision 1: Template Structure (v2 vs v3)

**Problem with v3:** Variables are defined globally, then referenced via `<variableGroup>` in templates. This separates the definition from its build context.

```xml
<!-- v3 (current - problematic) -->
<templates>
    <variables>
        <!-- Definitions here, globally -->
        <variable name="PosterVar">...</variable>

        <!-- Groups reference them -->
        <variableGroup name="artworkVars">
            <variable name="PosterVar" condition="widgetArt=Poster"/>
        </variableGroup>
    </variables>

    <template include="widget1">
        <variableGroup name="artworkVars"/>  <!-- Reference -->
        <controls>...</controls>
    </template>
</templates>
```

**v2 approach (better):** Variables defined INSIDE the template, alongside controls.

```xml
<!-- v2 (correct structure) -->
<other include="widget">
    <condition>...</condition>
    <property>...</property>
    <variables>
        <variable name="PosterVar">...</variable>
    </variables>
    <controls>...</controls>
</other>
```

**Decision:** Variables belong INSIDE the template. Same conditions, same context, same build.

---

### Open: Param System for Slot Variation

**Problem:** The `.2` suffix system requires duplicating expressions, presets, and templates.

**Direction being explored:** Use a PARAM-like system (like Kodi includes) where:
- Template defines what it needs
- Call site provides slot-specific values
- System handles property suffix automatically

**Key insight:** Properties are the SAME (`widgetPath`, `widgetArt`, etc.) - only the VALUES differ. The `.2` suffix is just storage, not a template concern.

Still working out the exact syntax and how this ties together.

---

### Open: Output Structure

From v2 docs: templates generate named includes via `include="name"` attribute.

Content type (`<controls>` vs `<variables>`) determined by what's inside the template.

```xml
<other include="widget">
    <variables>...</variables>  <!-- Outputs Kodi variables -->
    <controls>...</controls>    <!-- Outputs Kodi controls -->
</other>
```

Both can exist in same template. Still confirming this is the right approach.

