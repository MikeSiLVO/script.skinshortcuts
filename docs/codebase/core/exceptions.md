# exceptions.py

**Path:** `resources/lib/skinshortcuts/exceptions.py`
**Lines:** 54
**Purpose:** Exception hierarchy for error handling throughout the addon.

---

## Overview

Defines a hierarchy of custom exceptions used for error reporting. All exceptions inherit from `SkinShortcutsError` which inherits from Python's base `Exception`.

---

## Classes

### SkinShortcutsError (line 6)
Base exception class. All other exceptions inherit from this.

### ConfigError (line 10)
Base for configuration file errors. Stores file path and optional line number.

**Constructor:**
```python
def __init__(self, file_path: str, message: str, line: int | None = None)
```

**Attributes:**
- `file_path` - path to the problematic config file
- `line` - line number where error occurred (optional)

**Message format:** `"{file_path}:{line}: {message}"` or `"{file_path}: {message}"`

### Config-Specific Errors (lines 20-41)
All inherit from `ConfigError` with no additional logic:

| Class | Config File |
|-------|-------------|
| `MenuConfigError` | menus.xml |
| `WidgetConfigError` | widgets.xml |
| `BackgroundConfigError` | backgrounds.xml |
| `PropertyConfigError` | properties.xml |
| `GroupingsConfigError` | groupings.xml |
| `TemplateConfigError` | templates.xml |

### ValidationError (line 44)
For invalid input data validation failures.

### BuildError (line 48)
For errors during includes.xml generation.

### TemplateError (line 52)
For errors processing skin templates.

---

## Usage

**Raised by:**
- `loaders/menu.py` → `MenuConfigError`
- `loaders/widget.py` → `WidgetConfigError`
- `loaders/background.py` → `BackgroundConfigError`
- `loaders/property.py` → `PropertyConfigError`
- `loaders/template.py` → `TemplateConfigError`
- `builders/template.py` → `TemplateError`

**Caught by:**
- `entry.py` - catches generic exceptions during build

---

## Dead Code Analysis

- `GroupingsConfigError` - **POTENTIALLY UNUSED** - no groupings.xml loader exists
- `ValidationError` - **UNUSED** - never raised anywhere in codebase
- `BuildError` - **UNUSED** - never raised anywhere in codebase

---

## Test Candidates

1. `ConfigError` message formatting with/without line number
2. Exception inheritance hierarchy verification
