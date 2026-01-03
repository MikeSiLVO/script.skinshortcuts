# loaders/views.py

**Path:** `resources/lib/skinshortcuts/loaders/views.py`
**Purpose:** Parse views.xml into ViewConfig.

---

## Public Functions

### load_views(path)

Load view configuration from views.xml.

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | str \| Path | Path to views.xml |
| **Returns** | ViewConfig | Parsed configuration (empty if file missing) |

---

## Parsing Structure

Parses three sections:
1. Root `prefix` attribute
2. `<view>` elements → View objects
3. `<rules><content>` elements → ViewContent objects

---

## Validation

The loader validates:
- All views have `id` and `label`
- All content rules have `name`, `label`, `library`, `<visible>`, and `<views>`
- Default view IDs exist in defined views
- View IDs in content rules exist in defined views

Raises `ViewConfigError` on validation failure.

---

## Private Functions

| Function | Purpose |
|----------|---------|
| `_parse_views(root, path)` | Parse view definitions |
| `_parse_rules(root, path, views)` | Parse content rules |
| `_parse_content(elem, path, valid_view_ids)` | Parse single content element |
