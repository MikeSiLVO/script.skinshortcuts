"""Label localization utilities."""

from __future__ import annotations

import re

try:
    import xbmc
    import xbmcaddon

    IN_KODI = True
except ImportError:
    IN_KODI = False

# Pattern for $ADDON[addon.id #####] which needs special handling
ADDON_PATTERN = re.compile(r"\$ADDON\[([^\s\]]+)\s+(\d+)\]")


def resolve_label(label: str) -> str:
    """Resolve a label string to its localized value.

    Handles formats:
        $LOCALIZE[#####] - Kodi/skin string ID
        $NUMBER[#####] - Numeric value
        $ADDON[addon.id #####] - Addon string ID
        ##### - Plain number treated as string ID (Kodi convention)
        Plain text - returned as-is
    """
    if not label or not IN_KODI:
        return label

    # Check for $ADDON[addon.id #####] first - needs special handling
    # Must be checked before generic $ handling since getInfoLabel doesn't support $ADDON
    if label.startswith("$ADDON["):
        match = ADDON_PATTERN.match(label)
        if match:
            addon_id = match.group(1)
            string_id = int(match.group(2))
            try:
                addon = xbmcaddon.Addon(addon_id)
                result = addon.getLocalizedString(string_id)
                if result:
                    return result
            except RuntimeError:
                # Addon not installed - return label as-is (no warning, this is expected
                # when widgets reference optional addons filtered by visibility)
                pass
        return label

    # Any $... pattern - use getInfoLabel ($LOCALIZE, $NUMBER, $INFO, etc.)
    if label.startswith("$"):
        result = xbmc.getInfoLabel(label)
        if result:
            return result
        return label

    # Plain number - treat as localize string ID (Kodi convention)
    if label.isdigit():
        result = xbmc.getInfoLabel(f"$LOCALIZE[{label}]")
        if result:
            return result
        return label

    return label
