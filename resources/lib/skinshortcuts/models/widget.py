"""Widget model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union

    from .menu import Content

    WidgetGroupContent = Union["Widget", "WidgetGroup", "Content"]


@dataclass
class Widget:
    """A widget that can be assigned to menu items.

    For custom widgets (type="custom"), the slot attribute specifies which
    widget property slot this custom widget applies to (e.g., "widget", "widget.2").
    When selected, the dialog opens an item editor for the custom menu.
    """

    name: str
    label: str
    path: str
    type: str = ""
    target: str = "videos"
    icon: str = ""
    condition: str = ""  # Property condition (evaluated against item properties)
    visible: str = ""  # Kodi visibility condition (evaluated at runtime)
    sort_by: str = ""
    sort_order: str = ""
    limit: int | None = None
    source: str = ""  # Widget source type (library, playlist, addon, etc.)
    slot: str = ""  # For type="custom": which widget slot (e.g., "widget", "widget.2")

    @property
    def is_custom(self) -> bool:
        """Return True if this is a custom widget (user-defined item list)."""
        return self.type == "custom"

    def to_properties(self, prefix: str = "widget") -> dict[str, str]:
        """Convert to property dictionary for skin access.

        Core properties only - skins extend via properties.xml.
        """
        props = {
            f"{prefix}": self.name,
            f"{prefix}Label": self.label,
            f"{prefix}Path": self.path,
            f"{prefix}Target": self.target,
        }
        if self.source:
            props[f"{prefix}Source"] = self.source
        return props


@dataclass
class WidgetGroup:
    """A group/category of widgets in groupings."""

    name: str
    label: str
    condition: str = ""  # Property condition (evaluated against item properties)
    visible: str = ""  # Kodi visibility condition (evaluated at runtime)
    icon: str = ""  # Optional icon for group display
    items: list[WidgetGroupContent] = field(default_factory=list)


@dataclass
class WidgetConfig:
    """Widget configuration including widgets, groupings, and settings.

    Groupings can contain both WidgetGroup (folders) and standalone Widget items
    at the top level for flexibility.
    """

    widgets: list[Widget] = field(default_factory=list)
    groupings: list[WidgetGroup | Widget] = field(default_factory=list)
    show_get_more: bool = True
