# exceptions.py

**Path:** `resources/lib/skinshortcuts/exceptions.py`
**Purpose:** Exception hierarchy for error handling.

***

## Hierarchy

```
SkinShortcutsError
├── ConfigError (base for config file errors)
│   ├── MenuConfigError
│   ├── WidgetConfigError
│   ├── BackgroundConfigError
│   ├── PropertyConfigError
│   └── TemplateConfigError
└── TemplateError (template processing errors)
```

### ConfigError

Base for config file errors. Stores file path and optional line number.

```python
ConfigError(file_path, message, line=None)
```

Message format: `"{file_path}:{line}: {message}"`
