"""Real skin configs must build byte-identical output; SS_GOLDEN_REGEN=1 rewrites golden."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from skinshortcuts.config import SkinConfig

FIXTURES = Path(__file__).parent / "fixtures"
SKINS = sorted(p for p in (FIXTURES / "skins").iterdir() if p.is_dir())
GOLDEN = FIXTURES / "golden"
REGEN = os.environ.get("SS_GOLDEN_REGEN") == "1"


def _cases():
    """Defaults case per fixture skin, plus a userdata case where it ships one."""
    for skin in SKINS:
        yield pytest.param(skin, False, id=f"{skin.name}-defaults")
        if (skin / "userdata.json").exists():
            yield pytest.param(skin, True, id=f"{skin.name}-userdata")


def _compare(name: str, actual: str) -> None:
    """Compare output against its golden file, or rewrite that file under SS_GOLDEN_REGEN."""
    target = GOLDEN / name
    if REGEN:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(actual, encoding="utf-8", newline="\n")
        return
    assert target.exists(), f"missing golden {name}; run with SS_GOLDEN_REGEN=1"
    expected = target.read_text(encoding="utf-8")
    if actual != expected:
        exp_lines, act_lines = expected.splitlines(), actual.splitlines()
        for i, (e, a) in enumerate(zip(exp_lines, act_lines, strict=False)):
            if e != a:
                pytest.fail(f"{name} differs at line {i + 1}:\n- {e}\n+ {a}")
        pytest.fail(f"{name} differs in length: {len(exp_lines)} vs {len(act_lines)} lines")


@pytest.mark.parametrize(("skin", "with_user"), list(_cases()))
def test_skin_builds_match_golden(tmp_path, skin: Path, with_user: bool):
    userdata_path = None
    if with_user:
        userdata_path = str(tmp_path / "userdata.json")
        Path(userdata_path).write_bytes((skin / "userdata.json").read_bytes())

    config = SkinConfig.load(
        skin / "shortcuts", load_user=with_user, userdata_path=userdata_path
    )
    out = tmp_path / "includes.xml"
    config.build_includes(out)

    tag = "userdata" if with_user else "defaults"
    _compare(f"{skin.name}.{tag}.xml", out.read_text(encoding="utf-8"))
    if with_user:
        userdata = json.dumps(config.userdata.to_dict(), indent=1, sort_keys=True)
        _compare(f"{skin.name}.userdata.json", userdata)
