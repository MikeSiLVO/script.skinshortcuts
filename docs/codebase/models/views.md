# models/views.py

**Path:** `resources/lib/skinshortcuts/models/views.py`
**Purpose:** Dataclasses for view locking configuration.

---

## Classes

### View

A single view definition.

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | View identifier (used in expressions) |
| `label` | str | Display label |
| `icon` | str | Optional icon path |

### ViewContent

Content type with detection rules and available views.

| Field | Type | Description |
|-------|------|-------------|
| `name` | str | Content identifier (movies, tvshows, etc.) |
| `label` | str | Display label |
| `visible` | str | Kodi visibility condition for detection |
| `views` | list[str] | Available view IDs for this content |
| `library_default` | str | Default view ID for library content |
| `plugin_default` | str | Default view ID for plugin content (optional) |
| `icon` | str | Optional icon path |

**Methods:**
- `get_default(is_plugin)` - Returns plugin_default if is_plugin and set, else library_default

### ViewConfig

Complete view configuration loaded from views.xml.

| Field | Type | Description |
|-------|------|-------------|
| `views` | list[View] | All defined views |
| `content_rules` | list[ViewContent] | Content type rules |
| `prefix` | str | Expression name prefix (default: `ShortcutView_`) |

**Methods:**
- `get_view(view_id)` - Get View by ID
- `get_content(name)` - Get ViewContent by name
- `get_views_for_content(name)` - Get list of View objects available for a content type

---

## Usage

```python
from skinshortcuts.models.views import ViewConfig, ViewContent, View

# Typically loaded via loaders/views.py
config = ViewConfig(
    views=[
        View(id="List", label="$LOCALIZE[535]"),
        View(id="Poster", label="Poster"),
    ],
    content_rules=[
        ViewContent(
            name="movies",
            label="Movies",
            visible="Container.Content(movies)",
            views=["List", "Poster"],
            library_default="Poster",
            plugin_default="List",
        ),
    ],
    prefix="ShortcutView_",
)

# Get available views for movies
views = config.get_views_for_content("movies")
```
