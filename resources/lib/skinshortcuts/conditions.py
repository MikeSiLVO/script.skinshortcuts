"""Condition evaluation utilities for Skin Shortcuts.

Evaluates property conditions using a simple expression language:
- Equality: propertyName=value
- Contains: propertyName~value
- AND: condition1 + condition2
- OR: condition1 | condition2
- NOT: !condition or ![grouped condition]
- Grouping: [condition1 | condition2]
- Compact OR: propertyName=value1 | value2 | value3

Compact OR Notes:
    The property name cascades from the most recent full condition:
        prop=a | other=b | c  ->  prop=a | other=b | other=c

Negation Precedence:
    Negation applies to the adjacent condition only:
        !prop=a | b  ->  (!prop=a) | (prop=b)
    For group negation, use brackets:
        ![prop=a | b]  ->  !(prop=a | prop=b)
"""

from __future__ import annotations

import re

_OR_SPLIT_PATTERN = re.compile(r"\s*\|\s*")
_CONDITION_MATCH_PATTERN = re.compile(r"^(!?)([a-zA-Z_][a-zA-Z0-9_\.]*)(=|~)(.*)$")


def expand_compact_or(condition: str) -> str:
    """Expand compact OR syntax to full form.

    "widgetType=movies | episodes | tvshows" becomes
    "widgetType=movies | widgetType=episodes | widgetType=tvshows"
    """
    if not condition:
        return condition

    result_parts = []
    and_parts = _split_preserving_brackets(condition, "+")

    for and_part in and_parts:
        and_part = and_part.strip()
        if not and_part:
            continue

        is_negated = and_part.startswith("!")
        if is_negated:
            and_part = and_part[1:].strip()

        if and_part.startswith("[") and and_part.endswith("]"):
            inner = and_part[1:-1].strip()
            expanded_inner = _expand_or_segment(inner)
            if is_negated:
                result_parts.append(f"![{expanded_inner}]")
            else:
                result_parts.append(f"[{expanded_inner}]")
        else:
            expanded = _expand_or_segment(and_part)
            if is_negated:
                result_parts.append(f"!{expanded}")
            else:
                result_parts.append(expanded)

    return " + ".join(result_parts)


def _split_preserving_brackets(text: str, delimiter: str) -> list[str]:
    """Split text by delimiter but preserve content inside brackets."""
    parts = []
    current = []
    depth = 0

    for char in text:
        if char == "[":
            depth += 1
            current.append(char)
        elif char == "]":
            depth -= 1
            current.append(char)
        elif char == delimiter and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)

    if current:
        parts.append("".join(current))

    return parts


def _expand_or_segment(segment: str) -> str:
    """Expand a single OR segment."""
    parts = _OR_SPLIT_PATTERN.split(segment)
    if len(parts) <= 1:
        return segment

    result_parts = []
    current_property = ""
    current_operator = ""

    for part in parts:
        part = part.strip()
        if not part:
            continue

        match = _CONDITION_MATCH_PATTERN.match(part)
        if match:
            negation = match.group(1)
            current_property = match.group(2)
            current_operator = match.group(3)
            value = match.group(4)
            result_parts.append(f"{negation}{current_property}{current_operator}{value}")
        elif current_property:
            result_parts.append(f"{current_property}{current_operator}{part}")
        else:
            result_parts.append(part)

    return " | ".join(result_parts)


def evaluate_condition(condition: str, properties: dict[str, str]) -> bool:
    """Evaluate a condition against property values.

    Args:
        condition: Condition string to evaluate
        properties: Dict of property name -> value to check against

    Returns:
        True if condition matches, False otherwise.
        Empty/None conditions return True.
    """
    if not condition:
        return True

    condition = condition.strip()
    if not condition:
        return True

    if "|" in condition:
        condition = expand_compact_or(condition)
    return _evaluate_expanded(condition, properties)


def _is_wrapped_in_brackets(text: str) -> bool:
    """Check if text is wrapped in matching brackets (not just starts/ends with them)."""
    if not text.startswith("[") or not text.endswith("]"):
        return False
    depth = 0
    for i, char in enumerate(text):
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0 and i < len(text) - 1:
                return False
    return depth == 0


def _evaluate_expanded(condition: str, properties: dict[str, str]) -> bool:
    """Evaluate an expanded condition."""
    condition = condition.strip()
    if not condition:
        return True

    if _is_wrapped_in_brackets(condition):
        return _evaluate_expanded(condition[1:-1], properties)

    # Split AND/OR before negation: !a + b = (!a) + b, not !(a + b)
    and_parts = _split_preserving_brackets(condition, "+")
    if len(and_parts) > 1:
        return all(_evaluate_expanded(part.strip(), properties) for part in and_parts)

    or_parts = _split_preserving_brackets(condition, "|")
    if len(or_parts) > 1:
        return any(_evaluate_expanded(part.strip(), properties) for part in or_parts)

    if condition.startswith("!"):
        inner = condition[1:].strip()
        if _is_wrapped_in_brackets(inner):
            return not _evaluate_expanded(inner[1:-1], properties)
        return not _evaluate_single(inner, properties)

    return _evaluate_single(condition, properties)


def _evaluate_single(condition: str, properties: dict[str, str]) -> bool:
    """Evaluate a single condition (property=value or property~value)."""
    condition = condition.strip()

    negated = False
    if condition.startswith("!"):
        negated = True
        condition = condition[1:].strip()

    if _is_wrapped_in_brackets(condition):
        result = _evaluate_expanded(condition[1:-1], properties)
        return not result if negated else result

    if "=" in condition:
        prop_name, value = condition.split("=", 1)
        prop_name = prop_name.strip()
        value = value.strip()
        actual = properties.get(prop_name, "")
        result = actual == value
        return not result if negated else result

    if "~" in condition:
        prop_name, value = condition.split("~", 1)
        prop_name = prop_name.strip()
        value = value.strip()
        actual = properties.get(prop_name, "")
        result = value in actual
        return not result if negated else result

    # Property name only: truthy if non-empty
    result = bool(properties.get(condition, ""))
    return not result if negated else result
