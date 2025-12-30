"""Menu and MenuItem models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Union

    GroupContent = Union["Shortcut", "ShortcutGroup", "Content"]


@dataclass
class IconSource:
    """A source for browsing icons.

    Used by the icon picker to provide browse locations. Supports both
    simple (single path) and advanced (multiple conditional sources) modes.

    Attributes:
        condition: Property condition (evaluated against item properties)
        visible: Kodi visibility condition (evaluated at runtime)
    """

    label: str
    path: str  # Path to browse, or "browse" for free file browser
    condition: str = ""
    visible: str = ""
    icon: str = ""


@dataclass
class Content:
    """Dynamic content reference for groupings.

    Content references are resolved at runtime to library items like
    playlists, addons, sources, favourites, etc.

    Attributes:
        source: The content source type. Valid values:
            - "playlists": User playlists
            - "addons": Installed addons
            - "library": Library nodes (genres, years, etc.)
            - "sources": File sources
            - "favourites": User favourites
            - "pvr": PVR channels/recordings
            - "commands": System commands (quit, restart, etc.)
            - "settings": Settings shortcuts
        target: The media type context. Valid values:
            - "video", "videos": Video context
            - "music", "audio": Music context
            - "pictures", "images": Picture context
            - "programs", "executable": Program/addon context
            - "tv": Live TV
            - "radio": Radio
        path: Optional custom path (e.g., "special://skin/playlists/")
        condition: Property condition (evaluated against item properties)
        visible: Kodi visibility condition (evaluated at runtime)
        icon: Optional icon override
        label: Optional label override for the group
        folder: Optional label for wrapping resolved items in a sub-folder.
            When set, resolved items appear in a navigable folder with this
            label instead of being added directly to the parent group.
    """

    source: str
    target: str = ""
    path: str = ""
    condition: str = ""
    visible: str = ""
    icon: str = ""
    label: str = ""
    folder: str = ""


@dataclass
class Action:
    """An action with optional condition.

    When condition is set, the action only executes if the condition is true.
    """

    action: str
    condition: str = ""


@dataclass
class Protection:
    """Protection rule for a menu item.

    Protects items from accidental deletion or modification by showing
    a confirmation dialog before the action is performed.

    Attributes:
        type: What operations to protect against:
            - "delete": Only protect against deletion
            - "action": Only protect against action changes
            - "all": Protect against both deletion and action changes
        heading: Dialog heading (can be localize string like "$LOCALIZE[123]")
        message: Dialog message (can be localize string)
    """

    type: str = "all"  # "delete", "action", or "all"
    heading: str = ""
    message: str = ""

    def protects_delete(self) -> bool:
        """Return True if this protection applies to deletion."""
        return self.type in ("delete", "all")

    def protects_action(self) -> bool:
        """Return True if this protection applies to action changes."""
        return self.type in ("action", "all")


@dataclass
class Shortcut:
    """A shortcut option in groupings (for picker dialog).

    Attributes:
        name: Unique identifier
        label: Display label (can be localize string ID)
        action: The action to execute (if not using browse)
        path: The path to browse (if using browse mode)
        browse: Target window for browse mode ("videos", "music", "pictures", "programs")
                When set, path is opened via ActivateWindow({browse}, {path}, return)
        type: Category/type label (e.g., "Movies", shown as secondary info)
        icon: Icon path
        condition: Visibility condition
    """

    name: str
    label: str
    action: str = ""
    path: str = ""
    browse: str = ""
    type: str = ""
    icon: str = "DefaultShortcut.png"
    condition: str = ""
    visible: str = ""
    action_play: str = ""
    action_party: str = ""

    def get_action(self) -> str:
        """Get the resolved action string.

        If browse is set, constructs ActivateWindow action from path.
        Otherwise returns the action directly.
        """
        if self.browse and self.path:
            from ..constants import WINDOW_MAP

            window = WINDOW_MAP.get(self.browse.lower(), "Videos")
            return f"ActivateWindow({window},{self.path},return)"
        return self.action


@dataclass
class ShortcutGroup:
    """A group/category of shortcuts in groupings.

    Items can be:
    - Shortcut: A specific shortcut option
    - ShortcutGroup: A nested sub-group
    - Content: A dynamic content reference resolved at runtime
    """

    name: str
    label: str
    condition: str = ""  # Property condition (evaluated against item properties)
    visible: str = ""  # Kodi visibility condition (evaluated at runtime)
    icon: str = ""
    items: list[GroupContent] = field(default_factory=list)


@dataclass
class MenuItem:
    """A single item in a menu."""

    name: str
    label: str
    actions: list[Action] = field(default_factory=list)
    label2: str = ""
    icon: str = "DefaultShortcut.png"
    thumb: str = ""
    visible: str = ""  # Output to includes.xml (<visible> element)
    dialog_visible: str = ""  # Filter in management dialog (visible= attribute)
    disabled: bool = False
    required: bool = False  # If True, item cannot be deleted
    protection: Protection | None = None  # Optional protection against delete/modify

    properties: dict[str, str] = field(default_factory=dict)
    submenu: str | None = None
    original_action: str = ""  # Set from defaults, not saved to userdata

    @property
    def action(self) -> str:
        """Primary action (first unconditional action, for backwards compat)."""
        for act in self.actions:
            if not act.condition:
                return act.action
        return self.actions[0].action if self.actions else ""

    @action.setter
    def action(self, value: str) -> None:
        """Set primary action (first unconditional action)."""
        for act in self.actions:
            if not act.condition:
                act.action = value
                return
        self.actions.insert(0, Action(action=value))


@dataclass
class DefaultAction:
    """A default action applied to all items in a menu.

    Attributes:
        action: The action to execute
        when: When to run relative to item actions ("before" or "after")
        condition: Optional visibility condition
    """

    action: str
    when: str = "before"  # "before" or "after"
    condition: str = ""


@dataclass
class MenuDefaults:
    """Default properties and actions for items in a menu."""

    properties: dict[str, str] = field(default_factory=dict)
    actions: list[DefaultAction] = field(default_factory=list)


@dataclass
class MenuAllow:
    """Configuration for what features are allowed in a menu."""

    widgets: bool = True
    backgrounds: bool = True
    submenus: bool = True


@dataclass
class Menu:
    """A menu containing menu items."""

    name: str
    items: list[MenuItem] = field(default_factory=list)
    defaults: MenuDefaults = field(default_factory=MenuDefaults)
    allow: MenuAllow = field(default_factory=MenuAllow)
    container: str | None = None  # Container ID for submenu visibility
    is_submenu: bool = False  # True if defined with <submenu> tag (not built as root include)

    def get_item(self, item_name: str) -> MenuItem | None:
        """Get item by name."""
        for item in self.items:
            if item.name == item_name:
                return item
        return None

    def add_item(self, item: MenuItem, position: int | None = None) -> None:
        """Add item at position (or end if None)."""
        if position is None:
            self.items.append(item)
        else:
            self.items.insert(position, item)

    def remove_item(self, item_name: str) -> bool:
        """Remove item by name. Returns True if found."""
        for i, item in enumerate(self.items):
            if item.name == item_name:
                self.items.pop(i)
                return True
        return False

    def move_item(self, item_name: str, direction: int) -> bool:
        """Move item up (-1) or down (+1). Returns True if moved."""
        for i, item in enumerate(self.items):
            if item.name == item_name:
                new_pos = i + direction
                if 0 <= new_pos < len(self.items):
                    self.items.pop(i)
                    self.items.insert(new_pos, item)
                    return True
                return False
        return False


@dataclass
class OnCloseAction:
    """An action to execute when a subdialog closes.

    Used to trigger follow-up actions based on the item's state after
    the subdialog. For example, opening a custom widget editor when
    widgetType=custom is set.

    Attributes:
        action: The action type ("menu" to open a menu)
        menu: Menu name for action="menu" (supports {item} placeholder)
        condition: Visibility condition (evaluated against current item properties)
    """

    action: str  # "menu"
    menu: str = ""  # For action="menu": menu name (supports {item} placeholder)
    condition: str = ""


@dataclass
class SubDialog:
    """A sub-dialog definition for the management dialog.

    When the user clicks a button with the specified ID, a child dialog
    is spawned with the given mode. The mode is set as a window property
    to control visibility of different panels in the skin XML.

    Attributes:
        button_id: The button ID that triggers this sub-dialog
        mode: The mode name set in Window.Property(skinshortcuts-dialog)
        setfocus: Optional control ID to focus when the sub-dialog opens
        suffix: Property suffix for this widget slot (e.g., ".2" for widget 2).
            When set, all property reads/writes are automatically suffixed,
            allowing one set of controls to edit multiple widget slots.
        onclose: Optional list of actions to run when subdialog closes.
            Actions are evaluated in order; first matching condition wins.
    """

    button_id: int
    mode: str
    setfocus: int | None = None
    suffix: str = ""
    onclose: list[OnCloseAction] = field(default_factory=list)


@dataclass
class ActionOverride:
    """An action override that replaces one action with another.

    Used to fix deprecated actions in user-edited menus without requiring
    manual re-editing. For example, replacing old window names with new ones.

    Attributes:
        replace: The action string to find and replace
        action: The new action string to use instead
    """

    replace: str
    action: str


@dataclass
class MenuConfig:
    """Menu configuration including menus, groupings, and icon sources."""

    menus: list[Menu] = field(default_factory=list)
    groupings: list[ShortcutGroup] = field(default_factory=list)
    icon_sources: list[IconSource] = field(default_factory=list)
    subdialogs: list[SubDialog] = field(default_factory=list)
    action_overrides: list[ActionOverride] = field(default_factory=list)
    show_context_menu: bool = True  # Whether to show context menu on items
