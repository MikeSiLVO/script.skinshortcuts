# localize.py

**Path:** `resources/lib/skinshortcuts/localize.py`
**Purpose:** Label localization utilities.

***

## Functions

### LANGUAGE(string_id) → str

Get localized string from this addon's strings.po.

### resolve_label(label) → str

Resolve label to localized value.

| Format | Example | Resolution |
|--------|---------|------------|
| `$LOCALIZE[#####]` | `$LOCALIZE[20000]` | xbmc.getInfoLabel() |
| `$NUMBER[#####]` | `$NUMBER[10]` | xbmc.getInfoLabel() |
| `$ADDON[addon.id #####]` | `$ADDON[script.skinshortcuts 32001]` | Addon.getLocalizedString() |
| `32000-32999` | `32001` | Script string |
| `#####` | `20000` | $LOCALIZE via getInfoLabel() |
| Plain text | `Movies` | Returned as-is |

Returns original label when not in Kodi.
