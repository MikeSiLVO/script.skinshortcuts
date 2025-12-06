"""Template models for Skin Shortcuts v3."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum


class BuildMode(Enum):
    """Template build mode."""

    MENU = "menu"  # Iterate menu items (default)
    LIST = "list"  # Iterate <list> items
    RAW = "true"  # Raw output, no iteration


@dataclass
class TemplateParam:
    """Parameter for parameterized includes or raw templates."""

    name: str
    default: str = ""


@dataclass
class TemplateProperty:
    """Property assignment in a template.

    Can be:
    - Literal value: name="left", value="245"
    - From source: name="content", from_source="widgetPath"
    - Conditional: name="aspect", condition="widgetArt=Poster", value="stretch"
    """

    name: str
    value: str = ""
    from_source: str = ""  # Built-in or item property name
    condition: str = ""


@dataclass
class TemplateVar:
    """Multi-conditional property for internal template resolution.

    Example:
        <var name="aspect">
            <value condition="widgetArt=Poster">stretch</value>
            <value>scale</value>
        </var>
    """

    name: str
    values: list[TemplateProperty] = field(default_factory=list)


@dataclass
class PresetValues:
    """A single row in a preset lookup table."""

    condition: str = ""
    values: dict[str, str] = field(default_factory=dict)


@dataclass
class Preset:
    """Lookup table returning multiple values based on conditions."""

    name: str
    rows: list[PresetValues] = field(default_factory=list)


@dataclass
class PropertyGroup:
    """Reusable property group definition.

    Contains properties and vars that can be referenced by templates.
    Supports suffix transforms for Widget 1/2 property reuse.
    """

    name: str
    properties: list[TemplateProperty] = field(default_factory=list)
    vars: list[TemplateVar] = field(default_factory=list)


@dataclass
class PropertyGroupReference:
    """Reference to a property group."""

    name: str  # Name of property group to apply
    suffix: str = ""  # Suffix for property transforms (e.g., ".2")
    condition: str = ""  # Optional condition for applying this group


@dataclass
class PresetReference:
    """Reference to a preset for direct property resolution.

    When used in a template, evaluates the preset conditions and sets
    all matched attributes as properties directly.
    """

    name: str  # Name of preset to apply
    suffix: str = ""  # Suffix for condition transforms (e.g., ".2")
    condition: str = ""  # Optional condition for applying this preset


@dataclass
class IncludeDefinition:
    """Reusable include definition for controls (like Kodi includes).

    Contains control XML that can be inserted via $INCLUDE[name].
    """

    name: str
    controls: ET.Element | None = None  # Raw XML for control content


@dataclass
class ListItem:
    """Item in a <list> for build="list" templates."""

    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class VariableDefinition:
    """Kodi variable definition.

    Contains the actual <variable> content with $PROPERTY[id] placeholders.
    Can be defined:
    - Inside a template's <variables> section (inline)
    - In the global <variables> section (for reuse via variableGroups)
    """

    name: str  # Variable name (e.g., "PosterVar")
    condition: str = ""  # Only build if item matches (evaluated per-item)
    output: str = ""  # Override output name pattern
    content: ET.Element | None = None  # The <variable> XML content


@dataclass
class VariableReference:
    """Reference to a variable definition within a variableGroup.

    Points to a global variable definition with an optional condition
    for when to build it.
    """

    name: str  # Name of variable definition to use
    condition: str = ""  # Only build if item matches this condition


@dataclass
class VariableGroupRef:
    """Reference to another variableGroup (for nested groups)."""

    name: str  # Name of the referenced variableGroup


@dataclass
class VariableGroup:
    """Group of variable references for reuse across templates.

    Allows defining which variables to build together, with conditions
    for each. Supports suffix transforms for Widget 1/2 property reuse.
    Can also include references to other variableGroups for composition.
    """

    name: str
    references: list[VariableReference] = field(default_factory=list)
    group_refs: list[VariableGroupRef] = field(default_factory=list)  # Nested groups


@dataclass
class VariableGroupReference:
    """Reference to a variable group from a template.

    When used in a template, builds all matching variables from the group
    with optional suffix transformation for slot support.
    """

    name: str  # Name of variable group to apply
    suffix: str = ""  # Suffix for condition transforms (e.g., ".2")
    condition: str = ""  # Optional condition for applying this group


@dataclass
class Template:
    """Main template definition.

    Iterates menu items (default), list items (build="list"),
    or outputs raw (build="true").
    """

    include: str  # Output include name
    build: BuildMode = BuildMode.MENU
    id_prefix: str = ""  # For computed control IDs
    template_only: str = ""  # "true"=never generate, "auto"=skip if unassigned

    conditions: list[str] = field(default_factory=list)  # ANDed together
    params: list[TemplateParam] = field(default_factory=list)  # For build="true"
    properties: list[TemplateProperty] = field(default_factory=list)
    vars: list[TemplateVar] = field(default_factory=list)  # Internal context resolution
    property_groups: list[PropertyGroupReference] = field(default_factory=list)
    preset_refs: list[PresetReference] = field(default_factory=list)  # Direct preset lookups
    list_items: list[ListItem] = field(default_factory=list)  # For build="list"
    controls: ET.Element | None = None  # Raw XML for controls output
    variables: list[VariableDefinition] = field(default_factory=list)  # Inline variables
    variable_groups: list[VariableGroupReference] = field(default_factory=list)  # Group refs


@dataclass
class SubmenuTemplate:
    """Submenu template definition."""

    include: str = ""
    level: int = 0
    name: str = ""

    properties: list[TemplateProperty] = field(default_factory=list)
    vars: list[TemplateVar] = field(default_factory=list)
    property_groups: list[PropertyGroupReference] = field(default_factory=list)
    controls: ET.Element | None = None


@dataclass
class TemplateSchema:
    """Complete template schema from templates.xml."""

    expressions: dict[str, str] = field(default_factory=dict)  # name -> condition
    property_groups: dict[str, PropertyGroup] = field(default_factory=dict)
    includes: dict[str, IncludeDefinition] = field(default_factory=dict)  # For controls
    presets: dict[str, Preset] = field(default_factory=dict)
    variable_definitions: dict[str, VariableDefinition] = field(default_factory=dict)
    variable_groups: dict[str, VariableGroup] = field(default_factory=dict)
    templates: list[Template] = field(default_factory=list)
    submenus: list[SubmenuTemplate] = field(default_factory=list)

    def get_expression(self, name: str) -> str | None:
        """Get expression by name."""
        return self.expressions.get(name)

    def get_property_group(self, name: str) -> PropertyGroup | None:
        """Get property group by name."""
        return self.property_groups.get(name)

    def get_include(self, name: str) -> IncludeDefinition | None:
        """Get include definition by name (for controls)."""
        return self.includes.get(name)

    def get_preset(self, name: str) -> Preset | None:
        """Get preset by name."""
        return self.presets.get(name)

    def get_variable_definition(self, name: str) -> VariableDefinition | None:
        """Get variable definition by name."""
        return self.variable_definitions.get(name)

    def get_variable_group(self, name: str) -> VariableGroup | None:
        """Get variable group by name."""
        return self.variable_groups.get(name)
