# log.py

**Path:** `resources/lib/skinshortcuts/log.py`
**Purpose:** Component logging and Kodi notifications.

***

## Overview

Provides per-component loggers that prefix every line with
`script.skinshortcuts:` and the component name. Falls back to `print`
when `xbmc` is not importable, so the modules that use it stay testable
outside Kodi.

`IN_KODI` is set by attempting to import `xbmc`. When in Kodi, `DEBUG`
is read once from the addon's `debug` setting; otherwise it is False.

***

## Functions

| Function | Returns | Description |
|----------|---------|-------------|
| `get_logger(component="")` | Logger | Cached logger for the named component |
| `notify(heading, message, detail)` | None | Log the detail at warning and fire a Kodi notification ending in "(see log)" |

`get_logger` caches one `Logger` per component name in `_loggers`.

`notify` writes each distinct detail line once per run (`_logged`) and each distinct heading and message once (`_notified`). Outside Kodi the detail still prints and the toast is skipped. Skinner-facing errors use it: heading `<Feature> Error`, message led by the offending name, detail as `<file>: <what was written>; <what the script did>; <how to fix>`.

***

## Logger Class

`Logger(component="")` formats messages and dispatches to `xbmc.log`.

| Method | Kodi level |
|--------|------------|
| `debug(msg)` | LOGDEBUG |
| `info(msg)` | LOGINFO |
| `warning(msg)` | LOGWARNING |
| `error(msg)` | LOGERROR |

Format: `script.skinshortcuts: {component} - {msg}`, or
`script.skinshortcuts: {msg}` when the component is empty.

When `DEBUG` is True, messages at LOGDEBUG are emitted at LOGINFO so
debug output appears without enabling Kodi's global debug logging.
Outside Kodi all levels print to stdout.
