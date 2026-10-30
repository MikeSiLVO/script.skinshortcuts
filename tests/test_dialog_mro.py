"""Every NotImplementedError stub on the dialog mixins must resolve to a real method."""

from __future__ import annotations

import ast
import inspect
import textwrap

from skinshortcuts.dialog import ManagementDialog


def _is_stub(func) -> bool:
    """Whether a function's body only raises NotImplementedError."""
    try:
        source = textwrap.dedent(inspect.getsource(func))
    except (OSError, TypeError):
        return False
    body = ast.parse(source).body[0].body  # type: ignore[attr-defined]
    stmts = [s for s in body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
    return (
        len(stmts) == 1
        and isinstance(stmts[0], ast.Raise)
        and "NotImplementedError" in ast.unparse(stmts[0])
    )


def test_no_stub_wins_resolution():
    stub_names = set()
    for cls in ManagementDialog.__mro__:
        for name, attr in vars(cls).items():
            if inspect.isfunction(attr) and _is_stub(attr):
                stub_names.add(name)
    assert stub_names, "expected the base mixin to declare stubs"
    unresolved = sorted(n for n in stub_names if _is_stub(getattr(ManagementDialog, n)))
    assert not unresolved, f"stubs with no implementation: {unresolved}"
