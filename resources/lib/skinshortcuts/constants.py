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
