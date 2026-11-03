"""Base loader functionality."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Any, TypeVar

from ..conditions import lookup
from ..exceptions import ConfigError
from ..log import notify
from ..models.override import Override

T = TypeVar("T")


def parse_xml(path: str | Path, expected_root: str, error_class: type[ConfigError]) -> ET.Element:
    """Parse XML file and validate root element."""
    path = Path(path)

    if not path.exists():
        raise error_class(str(path), "File not found")

    try:
        tree = ET.parse(str(path))
    except ET.ParseError as e:
        line = e.position[0] if e.position else None
        raise error_class(str(path), f"XML parse error: {e}", line) from e

    root = tree.getroot()
    if root.tag != expected_root:
        raise error_class(str(path), f"Expected <{expected_root}>, got <{root.tag}>")

    return root


def get_text(elem: ET.Element, child: str, default: str = "") -> str:
    """Get text content of child element."""
    child_elem = elem.find(child)
    if child_elem is not None and child_elem.text:
        return child_elem.text.strip()
    return default


def get_attr(elem: ET.Element, attr: str, default: str = "") -> str:
    """Get attribute value."""
    return (elem.get(attr) or default).strip()


def get_int(elem: ET.Element, child: str, default: int | None = None) -> int | None:
    """Get integer from child element text."""
    text = get_text(elem, child)
    if not text:
        return default
    try:
        return int(text)
    except ValueError:
        return default


def get_bool(elem: ET.Element, attr: str, default: bool = False) -> bool:
    """Get boolean from attribute value: true or false in any case, anything else falls back."""
    value = (elem.get(attr) or "").strip().lower()
    if value == "true":
        return True
    if value == "false":
        return False
    return default


def parse_content(elem: ET.Element):
    """Parse a content reference element."""
    from ..models.menu import Content

    source = get_attr(elem, "source")
    if not source:
        return None

    return Content(
        source=source,
        target=get_attr(elem, "target") or "",
        path=get_attr(elem, "path") or "",
        condition=get_attr(elem, "condition") or "",
        visible=get_attr(elem, "visible") or "",
        icon=get_attr(elem, "icon") or "",
        label=get_attr(elem, "label") or "",
        folder=get_attr(elem, "folder") or "",
    )


def parse_name_overrides(root, tag: str) -> list[Override]:
    """Parse an <overrides> section listing names the skin retired."""
    section = root.find("overrides")
    if section is None:
        return []

    overrides = []
    for elem in section.findall(tag):
        replace = get_attr(elem, "replace")
        if replace:
            overrides.append(Override(replace=replace, value=(elem.text or "").strip()))

    return overrides


def report_missing(
    heading: str, path: str | Path, elem: ET.Element, field: str, key: str = "name", scope: str = ""
) -> None:
    """Report an element skipped for lacking a value, named by its identifying attribute if set."""
    name = get_attr(elem, key)
    written = f'<{elem.tag} {key}="{name}">' if name else f"<{elem.tag}>"
    where = f" in {scope}" if scope else ""
    fix = f"add {field}" if field.startswith("<") else f'add {field}="..."'
    notify(
        heading,
        f"'{name}' missing {field}" if name else f"{elem.tag} missing '{field}'",
        f"{path}: {written}{where} has no {field}; {elem.tag} skipped; {fix}",
    )


_DUPLICATE_HEADINGS = {
    "menu": ("Menu Error", ""),
    "item": ("Menu Error", "item "),
    "widget": ("Widget Error", ""),
    "background": ("Background Error", ""),
    "view": ("View Error", ""),
    "content": ("View Error", "content "),
    "property": ("Property Error", ""),
    "fallback": ("Property Error", "fallback "),
    "property include": ("Property Error", "include "),
    "button": ("Property Button Error", ""),
    "expression": ("Template Error", "expression "),
    "preset": ("Template Error", "preset "),
    "presetGroup": ("Template Error", "presetGroup "),
    "propertyGroup": ("Template Error", "propertyGroup "),
    "variable": ("Template Error", "variable "),
    "variableGroup": ("Template Error", "variableGroup "),
    "include": ("Template Error", "include "),
    "items template": ("Items Template Error", ""),
}

_ANY_CASE = frozenset({"property", "fallback"})


def warn_duplicate_names(names: Iterable[str], kind: str, path: str, scope: str = "") -> None:
    """Warn per repeated name; only one definition of it can be looked up."""
    heading, prefix = _DUPLICATE_HEADINGS[kind]
    seen: set[str] = set()
    for name in names:
        if name in seen:
            where = f" in {scope}" if scope else ""
            notify(
                heading,
                f"{prefix}'{name}' defined twice{where}",
                f"{path}: {kind} '{name}' is defined more than once{where}; only one can be "
                "reached; give each a unique name",
            )
        seen.add(name)


def keep_first(found: dict, key: Any, value: Any, kind: str, path: str | Path) -> None:
    """Keep the first definition of each name, reporting a repeat; property names ignore case."""
    taken = lookup(key, found) is not None if kind in _ANY_CASE else key in found
    if not taken:
        found[key] = value
        return
    heading, prefix = _DUPLICATE_HEADINGS[kind]
    notify(
        heading,
        f"{prefix}'{key}' defined twice",
        f"{path}: {kind} '{key}' is defined more than once; the first is used; "
        "give each a unique name",
    )


def iter_nested(items: Iterable, item_type: type[T], group_type: type) -> Iterator[T]:
    """Every item of a type in a picker hierarchy in document order, nested groups included."""
    for item in items:
        if isinstance(item, group_type):
            yield from iter_nested(item.items, item_type, group_type)
        elif isinstance(item, item_type):
            yield item
