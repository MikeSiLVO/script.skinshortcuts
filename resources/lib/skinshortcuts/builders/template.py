"""Template builder for Skin Shortcuts v3.

Builds Kodi include XML from templates.xml and menu data.
"""

from __future__ import annotations

import copy
import re
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from ..conditions import evaluate_condition
from ..loaders.base import apply_suffix_to_from, apply_suffix_transform
from ..models.template import TemplateProperty

if TYPE_CHECKING:
    from ..models import Menu, MenuItem
    from ..models.property import PropertySchema
    from ..models.template import (
        Preset,
        PresetReference,
        PropertyGroup,
        Template,
        TemplateSchema,
        TemplateVar,
        VariableDefinition,
        VariableGroupReference,
    )

# Regex patterns for substitution
_PROPERTY_PATTERN = re.compile(r"\$PROPERTY\[([^\]]+)\]")
_EXP_PATTERN = re.compile(r"\$EXP\[([^\]]+)\]")
_INCLUDE_PATTERN = re.compile(r"\$INCLUDE\[([^\]]+)\]")


class TemplateBuilder:
    """Builds Kodi includes from v3 templates."""

    def __init__(
        self,
        schema: TemplateSchema,
        menus: list[Menu],
        container: str = "9000",
        property_schema: PropertySchema | None = None,
    ):
        self.schema = schema
        self.menus = menus
        self.container = container
        self.property_schema = property_schema
        self._menu_map: dict[str, Menu] = {m.name: m for m in menus}
        self._assigned_templates: set[str] = self._collect_assigned_templates()

    def _collect_assigned_templates(self) -> set[str]:
        """Collect template include names that are actually assigned to menu items.

        Scans all menu item properties (widgetPath, widgetPath.2, etc.) for
        $INCLUDE[skinshortcuts-template-*] references.
        """
        assigned: set[str] = set()
        include_pattern = re.compile(r"\$INCLUDE\[skinshortcuts-template-([^\]]+)\]")

        for menu in self.menus:
            for item in menu.items:
                # Check all properties that might contain template references
                for _prop_name, prop_value in item.properties.items():
                    if not prop_value:
                        continue
                    for match in include_pattern.finditer(prop_value):
                        assigned.add(f"skinshortcuts-template-{match.group(1)}")

        return assigned

    def build(self) -> ET.Element:
        """Build all template includes and variables.

        Templates with the same include name are merged into a single include element.
        Variables are output at the root level (siblings to includes).
        """
        root = ET.Element("includes")

        # Group templates by include name and merge their outputs
        include_map: dict[str, ET.Element] = {}
        # Collect variables (output at root level, not inside includes)
        variables_list: list[ET.Element] = []

        # Track templateonly settings per include name
        # "true" = never generate, "auto" = skip if unassigned
        template_only_settings: dict[str, str] = {}

        for template in self.schema.templates:
            include_name = f"skinshortcuts-template-{template.include}"

            if template.template_only:
                template_only_settings[include_name] = template.template_only

            # Get or create the include element
            if include_name not in include_map:
                include_elem = ET.Element("include")
                include_elem.set("name", include_name)
                include_map[include_name] = include_elem

            # Build controls and variables for this template variant
            self._build_template_into(template, include_map[include_name], variables_list)

        # Add variables first (they may be referenced by includes)
        for var_elem in variables_list:
            root.append(var_elem)

        # Add all includes to root (even empty ones to avoid Kodi log warnings)
        for include_name, include_elem in include_map.items():
            setting = template_only_settings.get(include_name, "")
            # "true" = never generate include
            if setting == "true":
                continue
            # "auto" = skip if template is not assigned to any menu item
            if setting == "auto" and include_name not in self._assigned_templates:
                continue
            if len(include_elem) == 0:
                # Add description for empty includes
                desc = ET.SubElement(include_elem, "description")
                desc.text = "Automatically generated - no menu items matched this template"
            root.append(include_elem)

        return root

    def _build_template_into(
        self,
        template: Template,
        include: ET.Element,
        variables_list: list[ET.Element],
    ) -> None:
        """Build template controls and variables.

        Controls go into the include element.
        Variables go into the variables_list (output at root level).
        """
        for menu in self.menus:
            for idx, item in enumerate(menu.items, start=1):
                if item.disabled:
                    continue

                # Check if template conditions match this item
                if not self._check_conditions(template.conditions, item):
                    continue

                # Build context for this item (idx is 1-based to match menu item IDs)
                context = self._build_context(template, item, idx, menu)

                # Build controls for this item
                if template.controls is not None:
                    controls = self._process_controls(
                        template.controls, context, item, menu
                    )
                    if controls is not None:
                        # Append children of <controls>, not the wrapper itself
                        for child in controls:
                            include.append(child)

                # Build inline variables defined in template
                for var_def in template.variables:
                    var_elem = self._build_variable(var_def, context, item)
                    if var_elem is not None:
                        variables_list.append(var_elem)

                # Build variables from variableGroup references
                for group_ref in template.variable_groups:
                    self._build_variable_group(
                        group_ref, context, item, variables_list
                    )

    def _build_context(
        self,
        template: Template,
        item: MenuItem,
        idx: int,
        menu: Menu,
    ) -> dict[str, str]:
        """Build property context for a menu item."""
        # Start with menu defaults, then item properties override them
        # This matches IncludesBuilder behavior: {**menu.defaults.properties, **item.properties}
        context: dict[str, str] = {**menu.defaults.properties, **item.properties}

        # Built-in properties (override any conflicts)
        context["index"] = str(idx)
        context["name"] = item.name
        context["menu"] = menu.name
        context["idprefix"] = template.id_prefix
        context["id"] = f"{template.id_prefix}{idx}" if template.id_prefix else str(idx)

        # Apply property fallbacks early so template conditions can use them
        self._apply_fallbacks(item, context)

        # Process template properties
        for prop in template.properties:
            value = self._resolve_property(prop, item, context)
            if value is not None:
                context[prop.name] = value

        # Process template vars (internal resolution)
        for var in template.vars:
            value = self._resolve_var(var, item, context)
            if value is not None:
                context[var.name] = value

        # Process preset references first (they set raw values from lookup tables)
        for ref in template.preset_refs:
            # Check condition if specified
            if ref.condition and not self._eval_condition(ref.condition, item, context):
                continue
            self._apply_preset(ref, item, context)

        # Process property group references (may transform/derive from preset values)
        for ref in template.property_groups:
            # Check condition if specified
            if ref.condition and not self._eval_condition(ref.condition, item, context):
                continue
            prop_group = self.schema.get_property_group(ref.name)
            if prop_group:
                self._apply_property_group(prop_group, item, context, ref.suffix)

        return context

    def _build_variable(
        self,
        var_def: VariableDefinition,
        context: dict[str, str],
        item: MenuItem,
    ) -> ET.Element | None:
        """Build a Kodi <variable> element from a variable definition.

        Checks the variable's condition, substitutes $PROPERTY[...] placeholders.
        """
        # Check per-variable condition
        if var_def.condition:
            condition = self._expand_expressions(var_def.condition)
            if not self._eval_condition(condition, item, context):
                return None

        # Deep copy the variable content
        if var_def.content is None:
            return None
        var_elem = copy.deepcopy(var_def.content)

        # Determine output name from output attribute or use original name
        if var_def.output:
            output_name = self._substitute_property_refs(var_def.output, item, context)
        else:
            # Use the variable's name attribute, substituting any $PROPERTY refs
            original_name = var_elem.get("name") or var_def.name
            output_name = self._substitute_property_refs(original_name, item, context)

        # Set the variable name attribute
        var_elem.set("name", output_name)

        # Process all text content in the variable element
        self._substitute_variable_content(var_elem, context, item)

        return var_elem

    def _build_variable_group(
        self,
        group_ref: VariableGroupReference,
        context: dict[str, str],
        item: MenuItem,
        variables_list: list[ET.Element],
    ) -> None:
        """Build variables from a variableGroup reference.

        Looks up the group, iterates its variable references, applies suffix
        transforms, and builds each matching variable from global definitions.
        Handles nested group references recursively.
        """
        # Check group-level condition
        if group_ref.condition:
            condition = self._expand_expressions(group_ref.condition)
            if not self._eval_condition(condition, item, context):
                return

        # Look up the variable group
        var_group = self.schema.get_variable_group(group_ref.name)
        if not var_group:
            return

        suffix = group_ref.suffix

        # Process nested variableGroup references first
        for nested_ref in var_group.group_refs:
            # Create a VariableGroupReference with inherited suffix
            from ..models.template import VariableGroupReference as VGRef

            nested_group_ref = VGRef(name=nested_ref.name, suffix=suffix, condition="")
            self._build_variable_group(nested_group_ref, context, item, variables_list)

        # Process each variable reference in the group
        for var_ref in var_group.references:
            # Apply suffix transform to condition if needed
            condition = var_ref.condition
            if suffix and condition:
                condition = apply_suffix_transform(condition, suffix)

            # Check variable-level condition
            if condition:
                condition = self._expand_expressions(condition)
                if not self._eval_condition(condition, item, context):
                    continue

            # Look up the global variable definition
            var_def = self.schema.get_variable_definition(var_ref.name)
            if not var_def:
                continue

            # Build the variable
            var_elem = self._build_variable(var_def, context, item)
            if var_elem is not None:
                variables_list.append(var_elem)

    def _substitute_variable_content(
        self,
        elem: ET.Element,
        context: dict[str, str],
        item: MenuItem,
    ) -> None:
        """Substitute $PROPERTY[...] in variable content recursively."""
        # Process text
        if elem.text:
            elem.text = self._substitute_property_refs(elem.text, item, context)

        # Process tail
        if elem.tail:
            elem.tail = self._substitute_property_refs(elem.tail, item, context)

        # Process attributes
        for attr, value in list(elem.attrib.items()):
            elem.set(attr, self._substitute_property_refs(value, item, context))

        # Process children recursively
        for child in elem:
            self._substitute_variable_content(child, context, item)

    def _resolve_property(
        self,
        prop: TemplateProperty,
        item: MenuItem,
        context: dict[str, str],
    ) -> str | None:
        """Resolve a property value."""
        # Check condition
        if prop.condition and not self._eval_condition(prop.condition, item, context):
            return None

        # From source
        if prop.from_source:
            return self._get_from_source(prop.from_source, item, context)

        # Literal value - substitute $PROPERTY[...] references
        value = prop.value
        if "$PROPERTY[" in value:
            value = self._substitute_property_refs(value, item, context)
        return value

    def _substitute_property_refs(
        self,
        text: str,
        item: MenuItem,
        context: dict[str, str],
    ) -> str:
        """Substitute $PROPERTY[...] in text during context building."""

        def replace_property(match: re.Match) -> str:
            name = match.group(1)
            if name in context:
                return context[name]
            if name in item.properties:
                return item.properties[name]
            return ""

        return _PROPERTY_PATTERN.sub(replace_property, text)

    def _resolve_var(
        self,
        var: TemplateVar,
        item: MenuItem,
        context: dict[str, str],
    ) -> str | None:
        """Resolve a var (first matching value wins)."""
        for val in var.values:
            if val.condition:
                if self._eval_condition(val.condition, item, context):
                    return val.value
            else:
                # Default/fallback
                return val.value
        return None

    def _get_from_source(
        self,
        source: str,
        item: MenuItem,
        context: dict[str, str],
    ) -> str:
        """Get value from a source (built-in, item property, or preset)."""
        # Check bracket syntax for preset lookup: preset[attr]
        if "[" in source and source.endswith("]"):
            bracket_pos = source.index("[")
            preset_name = source[:bracket_pos]
            attr = source[bracket_pos + 1 : -1]  # extract attr from [attr]
            preset = self.schema.get_preset(preset_name)
            if preset:
                return self._lookup_preset(preset, attr, item, context)

        # Check old dot-style preset lookup (preset.attribute format)
        if "." in source:
            preset_name, attr = source.split(".", 1)
            preset = self.schema.get_preset(preset_name)
            if preset:
                return self._lookup_preset(preset, attr, item, context)

        # Built-ins
        if source in ("index", "name", "menu", "id", "idprefix"):
            return context.get(source, "")

        # Check context first (for values set by presets/property groups)
        if source in context:
            return context[source]

        # Item property
        return item.properties.get(source, "")

    def _lookup_preset(
        self,
        preset: Preset,
        attr: str,
        item: MenuItem,
        context: dict[str, str],
    ) -> str:
        """Look up a value from a preset."""
        for row in preset.rows:
            if row.condition:
                if self._eval_condition(row.condition, item, context):
                    return row.values.get(attr, "")
            else:
                # Default row
                return row.values.get(attr, "")
        return ""

    def _apply_property_group(
        self,
        prop_group: PropertyGroup,
        item: MenuItem,
        context: dict[str, str],
        suffix: str = "",
    ) -> None:
        """Apply properties from a property group to context."""
        for prop in prop_group.properties:
            # Apply suffix transforms to from_source and condition
            from_source = prop.from_source
            condition = prop.condition

            if suffix:
                # Apply suffix transform to from_source
                if from_source:
                    from_source = apply_suffix_to_from(from_source, suffix)
                if condition:
                    # Expand expressions first, then apply suffix
                    condition = self._expand_expressions(condition)
                    condition = self._apply_suffix_to_condition(condition, suffix)

            # Create modified property
            modified_prop = TemplateProperty(
                name=prop.name,
                value=prop.value,
                from_source=from_source,
                condition=condition,
            )
            value = self._resolve_property(modified_prop, item, context)
            if value is not None and prop.name not in context:
                # Only set if not already in context (first match wins)
                context[prop.name] = value

        for var in prop_group.vars:
            value = self._resolve_var(var, item, context)
            if value is not None:
                context[var.name] = value

    def _apply_preset(
        self,
        ref: PresetReference,
        item: MenuItem,
        context: dict[str, str],
    ) -> None:
        """Apply preset values directly as properties.

        Evaluates preset conditions and sets all matched attributes as properties.
        Supports suffix transforms for Widget 1/2 reuse.

        The suffix is applied to CONDITIONS during evaluation, not to the preset name.
        This allows a single preset definition to be reused for Widget 1 and Widget 2
        by transforming conditions like 'widgetArt=Poster' to 'widgetArt.2=Poster'.
        """
        # Use base preset name (suffix is applied to conditions, not name)
        preset = self.schema.get_preset(ref.name)
        if not preset:
            return

        # Find matching row in preset
        for row in preset.rows:
            if row.condition:
                # Expand expressions first, then apply suffix to condition
                condition = self._expand_expressions(row.condition)
                if ref.suffix:
                    condition = self._apply_suffix_to_condition(condition, ref.suffix)
                if self._eval_condition(condition, item, context):
                    # Set all values from this row as properties
                    for attr_name, attr_value in row.values.items():
                        if attr_name not in context:
                            context[attr_name] = attr_value
                    return
            else:
                # Default row (no condition) - set all values
                for attr_name, attr_value in row.values.items():
                    if attr_name not in context:
                        context[attr_name] = attr_value
                return

    def _apply_fallbacks(
        self,
        item: MenuItem,
        context: dict[str, str],
    ) -> None:
        """Apply property fallbacks for missing properties.

        Checks all defined fallbacks and applies values for properties
        that are not already set in the context or item properties.

        Also applies fallbacks for suffixed properties (e.g., widgetArt.2)
        by transforming conditions to use suffixed property names.
        """
        if not self.property_schema:
            return

        # Collect suffixes in use by checking for suffixed widget properties
        suffixes_in_use = {""}  # Always include base (no suffix)
        for prop_name in item.properties:
            if "." in prop_name:
                # Extract suffix like ".2" from "widgetPath.2"
                parts = prop_name.rsplit(".", 1)
                if parts[1].isdigit():
                    suffixes_in_use.add(f".{parts[1]}")

        for prop_name, fallback in self.property_schema.fallbacks.items():
            # Apply fallback for each suffix variant
            for suffix in suffixes_in_use:
                suffixed_prop = f"{prop_name}{suffix}" if suffix else prop_name

                # Skip if property already has a value
                if suffixed_prop in context or suffixed_prop in item.properties:
                    continue

                # Evaluate fallback rules in order
                for rule in fallback.rules:
                    if rule.condition:
                        # Transform condition to use suffixed property names
                        condition = rule.condition
                        if suffix:
                            condition = apply_suffix_transform(condition, suffix)
                        if self._eval_condition(condition, item, context):
                            context[suffixed_prop] = rule.value
                            break
                    else:
                        # Default rule (no condition)
                        context[suffixed_prop] = rule.value
                        break

    def _apply_suffix_to_condition(self, condition: str, suffix: str) -> str:
        """Apply suffix to property names in a condition."""
        # Simple implementation - apply suffix to property names before operators
        # This is a basic version; may need refinement
        result = []
        parts = re.split(r"([=~|+\[\]!])", condition)
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            # Check if this is a property name (before = or ~)
            # Don't suffix built-ins
            if (
                i + 1 < len(parts)
                and parts[i + 1] in ("=", "~")
                and part not in ("index", "name", "menu", "id", "idprefix")
            ):
                part = f"{part}{suffix}"
            result.append(part)
        return "".join(result)

    def _check_conditions(self, conditions: list[str], item: MenuItem) -> bool:
        """Check if all template conditions match."""
        return all(self._eval_condition(cond, item, {}) for cond in conditions)

    def _get_property_value(
        self,
        prop_name: str,
        item: MenuItem,
        context: dict[str, str],
    ) -> str:
        """Get a property value, checking context first then item properties."""
        if prop_name in context:
            return context[prop_name]
        return item.properties.get(prop_name, "")

    def _eval_condition(
        self,
        condition: str,
        item: MenuItem,
        context: dict[str, str],
    ) -> bool:
        """Evaluate a condition against a menu item.

        Uses the shared evaluate_condition from loaders/property.py.
        Adds expression expansion ($EXP[name]) before evaluation.
        """
        # Expand expressions first
        condition = self._expand_expressions(condition)

        # Merge context with item properties (context takes precedence)
        properties = {**item.properties, **context}

        return evaluate_condition(condition, properties)

    def _expand_expressions(self, condition: str) -> str:
        """Expand $EXP[name] references in a condition."""

        def replace_exp(match: re.Match) -> str:
            name = match.group(1)
            expr = self.schema.get_expression(name)
            if expr:
                # Recursively expand nested expressions
                return self._expand_expressions(expr)
            return match.group(0)

        return _EXP_PATTERN.sub(replace_exp, condition)

    def _process_controls(
        self,
        controls: ET.Element,
        context: dict[str, str],
        item: MenuItem,
        menu: Menu,
    ) -> ET.Element | None:
        """Process controls XML, applying substitutions."""
        # Deep copy to avoid modifying original
        result = copy.deepcopy(controls)

        # Process the element tree
        self._process_element(result, context, item, menu)

        return result

    def _process_element(
        self,
        elem: ET.Element,
        context: dict[str, str],
        item: MenuItem,
        menu: Menu,
    ) -> None:
        """Recursively process an element, applying substitutions."""
        # Handle <skinshortcuts> tag
        if elem.tag == "skinshortcuts":
            # Handle visibility: <skinshortcuts>visibility</skinshortcuts>
            if elem.text and elem.text.strip() == "visibility":
                elem.tag = "visible"
                elem.text = (
                    f"String.IsEqual(Container({self.container})."
                    f"ListItem.Property(name),{item.name})"
                )
            # Handle include attribute: <skinshortcuts include="name" condition="prop" wrap="true"/>
            include_name = elem.get("include")
            if include_name:
                # Check for condition attribute - only include if property exists
                condition = elem.get("condition")
                if condition and condition not in item.properties:
                    # Condition not met - mark for removal
                    elem.set("_skinshortcuts_remove", "true")
                    elem.attrib.pop("include", None)
                    elem.attrib.pop("condition", None)
                    elem.attrib.pop("wrap", None)
                    return

                include_def = self.schema.get_include(include_name)
                if include_def and include_def.controls is not None:
                    # Get parent and replace this element with include contents
                    # We'll mark this element for replacement
                    elem.set("_skinshortcuts_include", include_name)
                    # Preserve wrap attribute for later processing
                    wrap_attr = elem.get("wrap") or ""
                    wrap = wrap_attr.lower() == "true"
                    if wrap:
                        elem.set("_skinshortcuts_wrap", "true")
                    elem.attrib.pop("include", None)
                    elem.attrib.pop("condition", None)
                    elem.attrib.pop("wrap", None)

        # Process text content
        if elem.text:
            elem.text = self._substitute_text(elem.text, context, item, menu)

        # Process tail
        if elem.tail:
            elem.tail = self._substitute_text(elem.tail, context, item, menu)

        # Process attributes
        for attr, value in list(elem.attrib.items()):
            elem.set(attr, self._substitute_text(value, context, item, menu))

        # Convert $INCLUDE[...] in text to <include> elements
        self._handle_include_substitution(elem)

        # Process children
        children_to_remove = []
        for child in elem:
            self._process_element(child, context, item, menu)

            # Check if child was marked for removal (condition not met)
            if child.get("_skinshortcuts_remove"):
                children_to_remove.append(child)

        # Handle <skinshortcuts include="..."/> replacements
        self._handle_skinshortcuts_include(elem, context, item, menu)

        for child in children_to_remove:
            elem.remove(child)

    def _handle_include_substitution(self, elem: ET.Element) -> None:
        """Convert $INCLUDE[...] in element text to <include> child elements.

        When element text contains $INCLUDE[name], converts it to a Kodi
        <include>name</include> child element.
        """
        if elem.text:
            match = _INCLUDE_PATTERN.search(elem.text)
            if match:
                include_name = match.group(1)
                # Create Kodi <include> element
                include_elem = ET.Element("include")
                include_elem.text = include_name
                include_elem.tail = elem.text[match.end():]
                elem.text = elem.text[:match.start()]
                elem.insert(0, include_elem)

    def _handle_skinshortcuts_include(
        self,
        elem: ET.Element,
        context: dict[str, str],
        item: MenuItem,
        menu: Menu,
    ) -> None:
        """Handle <skinshortcuts include="..."/> element replacements.

        Finds children marked with _skinshortcuts_include attribute and replaces
        them with the expanded include contents.

        If wrap="true" was specified, outputs as a Kodi <include> element.
        Otherwise, unwraps and inserts the include's children directly.
        """
        children_to_replace = []
        for i, child in enumerate(elem):
            include_name = child.get("_skinshortcuts_include")
            if include_name:
                wrap = child.get("_skinshortcuts_wrap") == "true"
                children_to_replace.append((i, child, include_name, wrap))

        # Process in reverse order to maintain correct indices
        for i, child, include_name, wrap in reversed(children_to_replace):
            include_def = self.schema.get_include(include_name)
            if include_def and include_def.controls is not None:
                # Expand include controls - process each child of the include element
                expanded = self._process_controls(
                    include_def.controls, context, item, menu
                )
                if expanded is not None:
                    tail = child.tail
                    elem.remove(child)

                    if wrap:
                        # Output as Kodi <include> element with processed contents
                        include_elem = ET.Element("include")
                        include_elem.set("name", include_name)
                        for inc_child in list(expanded):
                            include_elem.append(inc_child)
                        include_elem.tail = tail
                        elem.insert(i, include_elem)
                    else:
                        # Unwrap - insert all children from the include element
                        for j, inc_child in enumerate(list(expanded)):
                            elem.insert(i + j, inc_child)
                        # Preserve tail on last inserted element
                        if tail and len(expanded) > 0:
                            last_child = elem[i + len(expanded) - 1]
                            last_child.tail = (last_child.tail or "") + tail
            else:
                # Include not found - just remove the element
                elem.remove(child)

    def _substitute_text(
        self,
        text: str,
        context: dict[str, str],
        item: MenuItem,
        menu: Menu,
    ) -> str:
        """Substitute $PROPERTY[...] in text."""

        def replace_property(match: re.Match) -> str:
            name = match.group(1)
            # Check context first
            if name in context:
                return context[name]
            # Check item properties
            if name in item.properties:
                return item.properties[name]
            # Return empty for unknown
            return ""

        return _PROPERTY_PATTERN.sub(replace_property, text)

    def write(self, path: str, indent: bool = True) -> None:
        """Write template includes to file."""
        root = self.build()
        if indent:
            _indent_xml(root)
        tree = ET.ElementTree(root)
        tree.write(path, encoding="UTF-8", xml_declaration=True)


def _indent_xml(elem: ET.Element, level: int = 0) -> None:
    """Add indentation to XML tree."""
    indent = "\n" + "\t" * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = indent + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = indent
        for child in elem:
            _indent_xml(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = indent
    elif level and (not elem.tail or not elem.tail.strip()):
        elem.tail = indent
