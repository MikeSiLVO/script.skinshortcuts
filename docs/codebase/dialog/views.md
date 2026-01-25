# dialog/views.py

**Path:** `resources/lib/skinshortcuts/dialog/views.py`
**Purpose:** View selection dialogs for user customization.

---

## Public Functions

### show_view_browser(config, userdata)

Hierarchical view browser for managing all view settings.

| Parameter | Type | Description |
|-----------|------|-------------|
| `config` | ViewConfig | View configuration |
| `userdata` | UserData | User data for read/write |
| **Returns** | bool | True if changes made |

Menu structure:
- Library > (content types)
- Plugins > (content types + Add Addon Override)
- (addon overrides with reset options)
- Reset Library Views
- Reset Addon Views

### show_view_picker(config, userdata, content, plugin)

Direct view picker for a specific content type.

| Parameter | Type | Description |
|-----------|------|-------------|
| `config` | ViewConfig | View configuration |
| `userdata` | UserData | User data for read/write |
| `content` | str | Content type name (e.g., "movies") |
| `plugin` | str | Optional plugin ID for override |
| **Returns** | bool | True if change made |

---

## Window Properties

| Property | Window | Description |
|----------|--------|-------------|
| `SkinShortcuts.ViewDialog` | Home | Set to `true` while dialog is open |

---

## Dialog Flow

### Browser Mode

```
View Settings
├── Library >
│   ├── Movies [current view]
│   ├── TV Shows [current view]
│   └── ...
├── Plugins >
│   ├── Movies [current view]
│   ├── TV Shows [current view]
│   └── Add Addon Override >
├── plugin.video.example (reset) >
├── Reset Library Views
└── Reset Addon Views
```

### Addon Override Flow

1. User selects "Add Addon Override"
2. Dialog shows installed video addons
3. User selects addon
4. Dialog shows content types
5. User selects content type
6. View picker shown for that addon/content combination

---

## Entry Points

Called from entry.py:

```python
# Browser mode
view_select(shortcuts_path="/path/to/skin")

# Direct picker
view_select(content="movies", shortcuts_path="/path/to/skin")

# Addon-specific
view_select(content="movies", plugin="plugin.video.example", shortcuts_path="/path/to/skin")
```

---

## RunScript Commands

```
RunScript(script.skinshortcuts,type=viewselect)
RunScript(script.skinshortcuts,type=viewselect,content=movies)
RunScript(script.skinshortcuts,type=viewselect,content=movies,plugin=plugin.video.example)
RunScript(script.skinshortcuts,type=resetviews)
```
