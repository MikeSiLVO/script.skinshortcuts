"""Constants for Skin Shortcuts."""

from __future__ import annotations

MENUS_FILE = "menus.xml"
WIDGETS_FILE = "widgets.xml"
BACKGROUNDS_FILE = "backgrounds.xml"
PROPERTIES_FILE = "properties.xml"
TEMPLATES_FILE = "templates.xml"
VIEWS_FILE = "views.xml"
INCLUDES_FILE = "script-skinshortcuts-includes.xml"

DEFAULT_ICON = "DefaultShortcut.png"
DEFAULT_TARGET = "videos"
DEFAULT_VIEW_PREFIX = "ShortcutView_"

WIDGET_TYPES = frozenset(
    {
        "movies",
        "tvshows",
        "episodes",
        "musicvideos",
        "artists",
        "albums",
        "songs",
        "pvr",
        "pictures",
        "programs",
        "addons",
        "files",
        "custom",
    }
)

WIDGET_TARGETS = frozenset(
    {
        "videos",
        "music",
        "pictures",
        "programs",
        "pvr",
        "files",
    }
)

PROPERTY_TYPES = frozenset(
    {
        "select",
        "text",
        "number",
        "bool",
        "image",
        "path",
    }
)


WINDOW_MAP: dict[str, str] = {
    "video": "Videos",
    "videos": "Videos",
    "music": "Music",
    "audio": "Music",
    "pictures": "Pictures",
    "images": "Pictures",
    "programs": "Programs",
    "executable": "Programs",
    "pvr": "TVChannels",
    "tv": "TVChannels",
    "radio": "RadioChannels",
    "livetv": "TVChannels",
    "liveradio": "RadioChannels",
}

def extract_path_from_action(action: str) -> str:
    """Extract the bare content path from a full action string."""
    lower = action.lower()
    if lower.startswith("activatewindow("):
        inner = action[15:-1]
        parts = inner.split(",")
        if len(parts) >= 2:
            return parts[1].strip()
    elif lower.startswith("playmedia("):
        return action[10:-1]
    elif lower.startswith("runaddon("):
        addon_id = action[9:-1]
        return f"plugin://{addon_id}/"
    return action


TARGET_MAP: dict[str, str] = {
    "video": "videos",
    "videos": "videos",
    "music": "music",
    "audio": "music",
    "pictures": "pictures",
    "images": "pictures",
    "programs": "programs",
    "executable": "programs",
}
