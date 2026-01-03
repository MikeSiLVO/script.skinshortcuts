# builders/views.py

**Path:** `resources/lib/skinshortcuts/builders/views.py`
**Purpose:** Generate Kodi visibility expressions for view locking.

---

## Class: ViewExpressionBuilder

### Constructor

| Parameter | Type | Description |
|-----------|------|-------------|
| `config` | ViewConfig | View configuration |
| `userdata` | UserData | User view selections |

### Methods

#### build()

Generate all view expressions. Returns `list[ET.Element]`.

---

## Generated Expressions

### Per-View Expressions

For each defined view, generates two expressions:

| Expression | Purpose |
|------------|---------|
| `{prefix}{ViewId}` | Combined visibility - when this view should be active |
| `{prefix}{ViewId}_Include` | Whether view is used at all (for conditional loading) |

### Plugin Override Expressions

Generated only when plugin-specific overrides exist:

| Expression | Purpose |
|------------|---------|
| `{prefix}{Content}_HasPluginOverride` | True if current plugin has a custom view |
| `{prefix}{Content}_IsGenericPlugin` | True if plugin without custom override |

---

## Expression Logic

### Simple Case

When library and plugin use the same view with no overrides, the expression is just the content rule.

### Different Library/Plugin Views

When library and plugin defaults differ, expressions include source checks using `String.IsEmpty(Container.PluginName)`.

### With Plugin Overrides

When specific plugins have custom views:
1. `_HasPluginOverride` expression lists known plugin IDs
2. `_IsGenericPlugin` expression checks for unlisted plugins
3. Per-plugin conditions added to view expressions

---

## UserData Integration

The builder reads user selections from UserData:

| Source | Description |
|--------|-------------|
| `library` | User's library view selections |
| `plugins` | User's generic plugin view selections |
| `plugin.video.X` | Plugin-specific view overrides |

Falls back to content rule defaults when no user selection exists.

---

## Integration

Called from `IncludesBuilder.build()` when view configuration exists:

```python
if self.view_config and self.view_config.content_rules and self.userdata:
    view_builder = ViewExpressionBuilder(self.view_config, self.userdata)
    for expr in view_builder.build():
        root.append(expr)
```
