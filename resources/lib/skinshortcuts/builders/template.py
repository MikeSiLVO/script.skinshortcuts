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
        PresetGroupReference,
        PresetReference,
        PropertyGroup,
        Template,
        TemplateOutput,
        TemplateSchema,
        TemplateVar,
        VariableDefinition,
        VariableGroupReference,
    )

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

        include_map: dict[str, ET.Element] = {}
        variables_list: list[ET.Element] = []

        # templateonly: "true" = never generate, "auto" = skip if unassigned
        template_only_settings: dict[str, str] = {}

        for template in self.schema.templates:
            for output in template.get_outputs():
                include_name = f"skinshortcuts-template-{output.include}"

                if template.template_only:
                    template_only_settings[include_name] = template.template_only

                if include_name not in include_map:
                    include_elem = ET.Element("include")
                    include_elem.set("name", include_name)
                    include_map[include_name] = include_elem

                self._build_template_into(
                    template, output, include_map[include_name], variables_list
                )

        for var_elem in variables_list:
            root.append(var_elem)

        for include_name, include_elem in include_map.items():
            setting = template_only_settings.get(include_name, "")
            if setting == "true":
                continue
            if setting == "auto" and include_name not in self._assigned_templates:
                continue
            if len(include_elem) == 0:
                desc = ET.SubElement(include_elem, "description")
                desc.text = "Automatically generated - no menu items matched this template"
            root.append(include_elem)

        return root

    def _build_template_into(
        self,
        template: Template,
        output: TemplateOutput,
        include: ET.Element,
        variables_list: list[ET.Element],
    ) -> None:
        """Build template controls and variables for a specific output.

        Controls go into the include element.
        Variables go into the variables_list (output at root level).

        The output's suffix is applied to all conditions and references,
        allowing one template to generate multiple includes.
        """
        for menu in self.menus:
            for idx, item in enumerate(menu.items, start=1):
                if item.disabled:
                    continue

                if not self._check_conditions(template.conditions, item, output.suffix):
                    continue

                context = self._build_context(template, output, item, idx, menu)

                if template.controls is not None:
                    controls = self._process_controls(template.controls, context, item, menu)
                    if controls is not None:
                        for child in controls:
                            include.append(child)

                for var_def in template.variables:
                    var_elem = self._build_variable(var_def, context, item)
                    if var_elem is not None:
                        variables_list.append(var_elem)

                for group_ref in template.variable_groups:
                    effective_suffix = self._combine_suffixes(
                        output.suffix, group_ref.suffix
                    )
                    self._build_variable_group(
                        group_ref, context, item, variables_list, effective_suffix
                    )

    def _combine_suffixes(self, base_suffix: str, ref_suffix: str) -> str:
        """Combine output suffix with reference suffix.

        If ref already has a suffix, use it (explicit overrides output default).
        Otherwise, use the base output suffix.
        """
        return ref_suffix if ref_suffix else base_suffix

    def _build_context(
        self,
        template: Template,
        output: TemplateOutput,
        item: MenuItem,
        idx: int,
        menu: Menu,
    ) -> dict[str, str]:
        """Build property context for a menu item.

        The output's suffix is applied to all property/preset/variableGroup
        references, allowing one template to serve multiple widget slots.
        """
        context: dict[str, str] = {**menu.defaults.properties, **item.properties}

        context["index"] = str(idx)
        context["name"] = item.name
        context["menu"] = menu.name
        context["idprefix"] = output.id_prefix
        context["id"] = f"{output.id_prefix}{idx}" if output.id_prefix else str(idx)
        context["suffix"] = output.suffix or ""

        self._apply_fallbacks(item, context)

        # First match wins for same-named properties
        resolved_props: set[str] = set()
        for prop in template.properties:
            if prop.name in resolved_props:
                continue  # Already set by earlier match in this template
            value = self._resolve_property(prop, item, context, output.suffix)
            if value is not None:
                context[prop.name] = value
                resolved_props.add(prop.name)

        for var in template.vars:
            value = self._resolve_var(var, item, context, output.suffix)
            if value is not None:
                context[var.name] = value

        for ref in template.preset_refs:
            effective_suffix = self._combine_suffixes(output.suffix, ref.suffix)
            condition = ref.condition
            if condition:
                condition = self._expand_expressions(condition)
                if effective_suffix:
                    condition = self._apply_suffix_to_condition(condition, effective_suffix)
                if not self._eval_condition(condition, item, context):
                    continue
            self._apply_preset(ref, item, context, effective_suffix)

        for ref in template.preset_group_refs:
            effective_suffix = self._combine_suffixes(output.suffix, ref.suffix)
            condition = ref.condition
            if condition:
                condition = self._expand_expressions(condition)
                if effective_suffix:
                    condition = self._apply_suffix_to_condition(condition, effective_suffix)
                if not self._eval_condition(condition, item, context):
                    continue
            self._apply_preset_group(ref, item, context, effective_suffix)

        for ref in template.property_groups:
            effective_suffix = self._combine_suffixes(output.suffix, ref.suffix)
            condition = ref.condition
            if condition:
                condition = self._expand_expressions(condition)
                if effective_suffix:
                    condition = self._apply_suffix_to_condition(condition, effective_suffix)
                if not self._eval_condition(condition, item, context):
                    continue
            prop_group = self.schema.get_property_group(ref.name)
            if prop_group:
                self._apply_property_group(prop_group, item, context, effective_suffix)

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
        if var_def.condition:
            condition = self._expand_expressions(var_def.condition)
            if not self._eval_condition(condition, item, context):
                return None

        if var_def.content is None:
            return None
        var_elem = copy.deepcopy(var_def.content)

        if var_def.output:
            output_name = self._substitute_property_refs(var_def.output, item, context)
        else:
            original_name = var_elem.get("name") or var_def.name
            output_name = self._substitute_property_refs(original_name, item, context)

        var_elem.set("name", output_name)
        self._substitute_variable_content(var_elem, context, item)

        return var_elem

    def _build_variable_group(
        self,
        group_ref: VariableGroupReference,
        context: dict[str, str],
        item: MenuItem,
        variables_list: list[ET.Element],
        override_suffix: str = "",
    ) -> None:
        """Build variables from a variableGroup reference.

        Looks up the group, iterates its variable references, applies suffix
        transforms, and builds each matching variable from global definitions.
        Handles nested group references recursively.

        override_suffix: If provided, overrides the group_ref's suffix.
        """
        if group_ref.condition:
            condition = self._expand_expressions(group_ref.condition)
            if not self._eval_condition(condition, item, context):
                return

        var_group = self.schema.get_variable_group(group_ref.name)
        if not var_group:
            return

        suffix = override_suffix if override_suffix else group_ref.suffix

        for nested_ref in var_group.group_refs:
            from ..models.template import VariableGroupReference as VGRef

            nested_group_ref = VGRef(name=nested_ref.name, suffix=suffix, condition="")
            self._build_variable_group(nested_group_ref, context, item, variables_list)

        for var_ref in var_group.references:
            condition = var_ref.condition
            if suffix and condition:
                condition = apply_suffix_transform(condition, suffix)

            if condition:
                condition = self._expand_expressions(condition)
                if not self._eval_condition(condition, item, context):
                    continue

            var_def = self.schema.get_variable_definition(var_ref.name)
            if not var_def:
                continue

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
        if elem.text:
            elem.text = self._substitute_property_refs(elem.text, item, context)
        if elem.tail:
            elem.tail = self._substitute_property_refs(elem.tail, item, context)
        for attr, value in list(elem.attrib.items()):
            elem.set(attr, self._substitute_property_refs(value, item, context))
        for child in elem:
            self._substitute_variable_content(child, context, item)

    def _resolve_property(
        self,
        prop: TemplateProperty,
        item: MenuItem,
        context: dict[str, str],
        suffix: str = "",
    ) -> str | None:
        """Resolve a property value.

        When suffix is provided, it's applied to condition property names.
        """
        if prop.condition:
            condition = self._expand_expressions(prop.condition)
            if suffix:
                condition = self._apply_suffix_to_condition(condition, suffix)
            if not self._eval_condition(condition, item, context):
                return None

        if prop.from_source:
            source = prop.from_source
            if suffix:
                source = apply_suffix_to_from(source, suffix)
            return self._get_from_source(source, item, context, suffix)

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
        suffix: str = "",
    ) -> str | None:
        """Resolve a var (first matching value wins).

        When suffix is provided, it's applied to condition property names.
        """
        for val in var.values:
            if val.condition:
                condition = self._expand_expressions(val.condition)
                if suffix:
                    condition = self._apply_suffix_to_condition(condition, suffix)
                if self._eval_condition(condition, item, context):
                    return val.value
            else:
                return val.value
        return None

    def _get_from_source(
        self,
        source: str,
        item: MenuItem,
        context: dict[str, str],
        suffix: str = "",
    ) -> str:
        """Get value from a source (built-in or item property)."""
        if source in ("index", "name", "menu", "id", "idprefix"):
            return context.get(source, "")
        if source in context:
            return context[source]
        return item.properties.get(source, "")

    def _apply_property_group(
        self,
        prop_group: PropertyGroup,
        item: MenuItem,
        context: dict[str, str],
        suffix: str = "",
    ) -> None:
        """Apply properties from a property group to context."""
        for prop in prop_group.properties:
            from_source = prop.from_source
            condition = prop.condition

            if suffix:
                if from_source:
                    from_source = apply_suffix_to_from(from_source, suffix)
                if condition:
                    condition = self._expand_expressions(condition)
                    condition = self._apply_suffix_to_condition(condition, suffix)

            modified_prop = TemplateProperty(
                name=prop.name,
                value=prop.value,
                from_source=from_source,
                condition=condition,
            )
            value = self._resolve_property(modified_prop, item, context)
            if value is not None and prop.name not in context:
                context[prop.name] = value

        for var in prop_group.vars:
            value = self._resolve_var(var, item, context, suffix)
            if value is not None:
                context[var.name] = value

    def _apply_preset(
        self,
        ref: PresetReference,
        item: MenuItem,
        context: dict[str, str],
        override_suffix: str = "",
    ) -> None:
        """Apply preset values directly as properties.

        Evaluates preset conditions and sets all matched attributes as properties.
        Supports suffix transforms for Widget 1/2 reuse.

        The suffix is applied to CONDITIONS during evaluation, not to the preset name.
        This allows a single preset definition to be reused for Widget 1 and Widget 2
        by transforming conditions like 'widgetArt=Poster' to 'widgetArt.2=Poster'.

        override_suffix: If provided, overrides the ref's suffix.
        """
        preset = self.schema.get_preset(ref.name)
        if not preset:
            return

        suffix = override_suffix if override_suffix else ref.suffix

        for row in preset.rows:
            if row.condition:
                condition = self._expand_expressions(row.condition)
                if suffix:
                    condition = self._apply_suffix_to_condition(condition, suffix)
                if self._eval_condition(condition, item, context):
                    for attr_name, attr_value in row.values.items():
                        if attr_name not in context:
                            context[attr_name] = attr_value
                    return
            else:
                for attr_name, attr_value in row.values.items():
                    if attr_name not in context:
                        context[attr_name] = attr_value
                return

    def _apply_preset_group(
        self,
        ref: PresetGroupReference,
        item: MenuItem,
        context: dict[str, str],
        override_suffix: str = "",
    ) -> None:
        """Apply presetGroup - conditional preset selection.

        Evaluates children in document order, first matching condition wins.
        Children can be preset references or inline values.

        override_suffix: If provided, overrides the ref's suffix.
        """
        group = self.schema.get_preset_group(ref.name)
        if not group:
            return

        suffix = override_suffix if override_suffix else ref.suffix

        for child in group.children:
            if child.condition:
                condition = self._expand_expressions(child.condition)
                if suffix:
                    condition = self._apply_suffix_to_condition(condition, suffix)
                if not self._eval_condition(condition, item, context):
                    continue

            if child.preset_name:
                preset = self.schema.get_preset(child.preset_name)
                if preset:
                    values = self._get_preset_values(preset, item, context, suffix)
                    if values:
                        for attr_name, attr_value in values.items():
                            if attr_name not in context:
                                context[attr_name] = attr_value
                        return
            elif child.values:
                for attr_name, attr_value in child.values.items():
                    if attr_name not in context:
                        context[attr_name] = attr_value
                return

    def _get_preset_values(
        self,
        preset: Preset,
        item: MenuItem,
        context: dict[str, str],
        suffix: str = "",
    ) -> dict[str, str] | None:
        """Get matching values from a preset (first matching row)."""
        for row in preset.rows:
            if row.condition:
                condition = self._expand_expressions(row.condition)
                if suffix:
                    condition = self._apply_suffix_to_condition(condition, suffix)
                if self._eval_condition(condition, item, context):
                    return row.values
            else:
                return row.values
        return None

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

        suffixes_in_use = {""}
        for prop_name in item.properties:
            if "." in prop_name:
                parts = prop_name.rsplit(".", 1)
                if parts[1].isdigit():
                    suffixes_in_use.add(f".{parts[1]}")

        for prop_name, fallback in self.property_schema.fallbacks.items():
            for suffix in suffixes_in_use:
                suffixed_prop = f"{prop_name}{suffix}" if suffix else prop_name

                if suffixed_prop in context or suffixed_prop in item.properties:
                    continue

                for rule in fallback.rules:
                    if rule.condition:
                        condition = rule.condition
                        if suffix:
                            condition = apply_suffix_transform(condition, suffix)
                        if self._eval_condition(condition, item, context):
                            context[suffixed_prop] = rule.value
                            break
                    else:
                        context[suffixed_prop] = rule.value
                        break

    def _apply_suffix_to_condition(self, condition: str, suffix: str) -> str:
        """Apply suffix to property names in a condition.

        Preserves content within {NOSUFFIX:...} markers (from nosuffix expressions)
        without applying suffix transformation.
        """
        nosuffix_pattern = re.compile(r"\{NOSUFFIX:([^}]+)\}")
        preserved: list[str] = []

        def extract_nosuffix(match: re.Match) -> str:
            preserved.append(match.group(1))
            return f"__NOSUFFIX_{len(preserved) - 1}__"

        condition = nosuffix_pattern.sub(extract_nosuffix, condition)

        result = []
        parts = re.split(r"([=~|+\[\]!])", condition)
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            if (
                i + 1 < len(parts)
                and parts[i + 1] in ("=", "~")
                and part not in ("index", "name", "menu", "id", "idprefix", "suffix")
                and not part.startswith("__NOSUFFIX_")
            ):
                part = f"{part}{suffix}"
            result.append(part)

        transformed = "".join(result)

        for i, content in enumerate(preserved):
            transformed = transformed.replace(f"__NOSUFFIX_{i}__", content)

        return transformed

    def _strip_nosuffix_markers(self, condition: str) -> str:
        """Strip {NOSUFFIX:...} markers, keeping only the content."""
        return re.sub(r"\{NOSUFFIX:([^}]+)\}", r"\1", condition)

    def _check_conditions(
        self, conditions: list[str], item: MenuItem, suffix: str = ""
    ) -> bool:
        """Check if all template conditions match.

        When suffix is provided, it's applied to property names in conditions
        (e.g., 'widgetPath' becomes 'widgetPath.2' with suffix='.2').
        """
        for cond in conditions:
            expanded = self._expand_expressions(cond)
            if suffix:
                expanded = self._apply_suffix_to_condition(expanded, suffix)
            if not self._eval_condition(expanded, item, {}):
                return False
        return True

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
        condition = self._expand_expressions(condition)
        condition = self._strip_nosuffix_markers(condition)

        properties = {**item.properties, **context}

        return evaluate_condition(condition, properties)

    def _expand_expressions(self, condition: str) -> str:
        """Expand $EXP[name] references in a condition.

        For nosuffix=True expressions, wraps the value in {NOSUFFIX:...} markers
        which _apply_suffix_to_condition will preserve unchanged.
        """

        def replace_exp(match: re.Match) -> str:
            name = match.group(1)
            expr = self.schema.get_expression(name)
            if expr:
                expanded = self._expand_expressions(expr.value)
                if expr.nosuffix:
                    return f"{{NOSUFFIX:{expanded}}}"
                return expanded
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
        result = copy.deepcopy(controls)
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
        if elem.tag == "skinshortcuts":
            if elem.text and elem.text.strip() == "visibility":
                elem.tag = "visible"
                elem.text = (
                    f"String.IsEqual(Container({self.container})."
                    f"ListItem.Property(name),{item.name})"
                )
            include_name = elem.get("include")
            if include_name:
                condition = elem.get("condition")
                if condition and not self._eval_condition(condition, item, context):
                    elem.set("_skinshortcuts_remove", "true")
                    elem.attrib.pop("include", None)
                    elem.attrib.pop("condition", None)
                    elem.attrib.pop("wrap", None)
                    return

                include_def = self.schema.get_include(include_name)
                if include_def and include_def.controls is not None:
                    elem.set("_skinshortcuts_include", include_name)
                    wrap_attr = elem.get("wrap") or ""
                    wrap = wrap_attr.lower() == "true"
                    if wrap:
                        elem.set("_skinshortcuts_wrap", "true")
                    elem.attrib.pop("include", None)
                    elem.attrib.pop("condition", None)
                    elem.attrib.pop("wrap", None)

        if elem.text:
            elem.text = self._substitute_text(elem.text, context, item, menu)
        if elem.tail:
            elem.tail = self._substitute_text(elem.tail, context, item, menu)
        for attr, value in list(elem.attrib.items()):
            elem.set(attr, self._substitute_text(value, context, item, menu))

        self._handle_include_substitution(elem)

        children_to_remove = []
        for child in elem:
            self._process_element(child, context, item, menu)
            if child.get("_skinshortcuts_remove"):
                children_to_remove.append(child)

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

        for i, child, include_name, wrap in reversed(children_to_replace):
            include_def = self.schema.get_include(include_name)
            if include_def and include_def.controls is not None:
                expanded = self._process_controls(
                    include_def.controls, context, item, menu
                )
                if expanded is not None:
                    tail = child.tail
                    elem.remove(child)

                    if wrap:
                        include_elem = ET.Element("include")
                        include_elem.set("name", include_name)
                        for inc_child in list(expanded):
                            include_elem.append(inc_child)
                        include_elem.tail = tail
                        elem.insert(i, include_elem)
                    else:
                        for j, inc_child in enumerate(list(expanded)):
                            elem.insert(i + j, inc_child)
                        if tail and len(expanded) > 0:
                            last_child = elem[i + len(expanded) - 1]
                            last_child.tail = (last_child.tail or "") + tail
            else:
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
            if name in context:
                return context[name]
            if name in item.properties:
                return item.properties[name]
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
