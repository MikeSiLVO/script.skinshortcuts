"""Domain models for Skin Shortcuts."""

from __future__ import annotations

from .background import (
    Background,
    BackgroundConfig,
    BackgroundGroup,
    BackgroundType,
    BrowseSource,
    PlaylistSource,
)
from .menu import (
    Action,
    Content,
    DefaultAction,
    Group,
    IconSource,
    Menu,
    MenuAllow,
    MenuConfig,
    MenuItem,
    Shortcut,
)
from .property import (
    ButtonMapping,
    FallbackRule,
    IconVariant,
    PropertyFallback,
    PropertySchema,
    SchemaOption,
    SchemaProperty,
)
from .template import (
    BuildMode,
    IncludeDefinition,
    ListItem,
    Preset,
    PresetValues,
    PropertyGroup,
    PropertyGroupReference,
    SubmenuTemplate,
    Template,
    TemplateParam,
    TemplateProperty,
    TemplateSchema,
    TemplateVar,
    VariableDefinition,
    VariableGroup,
    VariableGroupReference,
    VariableReference,
)
from .widget import Widget, WidgetConfig, WidgetGroup

__all__ = [
    # Menu
    "Menu",
    "MenuAllow",
    "MenuItem",
    "Action",
    "DefaultAction",
    # Groupings
    "Group",
    "Shortcut",
    "Content",
    # Icons
    "IconSource",
    # Menu Config
    "MenuConfig",
    # Widget
    "Widget",
    "WidgetConfig",
    "WidgetGroup",
    # Background
    "Background",
    "BackgroundConfig",
    "BackgroundGroup",
    "BackgroundType",
    "BrowseSource",
    "PlaylistSource",
    # Property Schema
    "PropertySchema",
    "SchemaProperty",
    "SchemaOption",
    "ButtonMapping",
    "IconVariant",
    "PropertyFallback",
    "FallbackRule",
    # Template
    "TemplateSchema",
    "Template",
    "SubmenuTemplate",
    "TemplateProperty",
    "TemplateVar",
    "TemplateParam",
    "IncludeDefinition",
    "PropertyGroup",
    "PropertyGroupReference",
    "Preset",
    "PresetValues",
    "ListItem",
    "BuildMode",
    "VariableDefinition",
    "VariableReference",
    "VariableGroup",
    "VariableGroupReference",
]
