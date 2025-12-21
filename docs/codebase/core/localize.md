# localize.py

**Path:** `resources/lib/skinshortcuts/localize.py`
**Lines:** 61
**Purpose:** Label localization utilities for resolving Kodi string IDs.

***

## Overview

Provides label resolution that handles various Kodi localization formats. Works both inside and outside Kodi (returns original string when not in Kodi).

***

## Constants

### ADDON_PATTERN (line 16)

Regex pattern for `$ADDON[addon.id #####]` format.

Pattern: `r"\$ADDON\[([^\s\]]+)\s+(\d+)\]"`

Captures: addon ID and string ID

***

## Functions

### LANGUAGE(string_id) → str (line 20)

Get localized string from this addon.

**Parameters:**

* `string_id` - Integer string ID from addon's strings.po

**Returns:** Localized string, or string ID as string if not in Kodi

**Used by:** dialog/pickers.py (playlist action dialog)

***

### resolve_label(label) → str (line 27)

Resolve a label string to its localized value.

**Parameters:**

* `label` - String to resolve

**Returns:** Localized string or original if resolution fails

**Handled formats:**

| Format | Example | Resolution |
|--------|---------|------------|
| `$LOCALIZE[#####]` | `$LOCALIZE[20000]` | `xbmc.getInfoLabel()` |
| `$NUMBER[#####]` | `$NUMBER[10]` | `xbmc.getInfoLabel()` |
| `$ADDON[addon.id #####]` | `$ADDON[script.skinshortcuts 32001]` | `xbmcaddon.Addon().getLocalizedString()` |
| `32000-32999` | `32001` | Script string via `getLocalizedString()` |
| `#####` (other numbers) | `20000` | `$LOCALIZE[#####]` via `getInfoLabel()` |
| Plain text | `Movies` | Returned as-is |

**Behavior outside Kodi:**
Returns the original label unchanged (IN_KODI = False).

**Used by:** dialog.py (displaying labels in UI)

***

## Dead Code Analysis

All code appears to be in active use.

***

## Test Candidates

1. `resolve_label()` with `$LOCALIZE[...]` format
2. `resolve_label()` with `$ADDON[...]` format
3. `resolve_label()` with plain number
4. `resolve_label()` with plain text
5. `resolve_label()` when not in Kodi environment

**Note:** Most tests require mocking Kodi APIs.
