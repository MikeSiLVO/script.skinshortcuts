"""Tests for browse/multi background <path> vs <source> behavior."""

from __future__ import annotations

from skinshortcuts.loaders.background import load_backgrounds
from skinshortcuts.models.background import BackgroundType


def write_backgrounds(tmp_path, xml: str):
    """Write backgrounds.xml into the temp folder and return its path."""
    p = tmp_path / "backgrounds.xml"
    p.write_text(xml.strip(), encoding="utf-8")
    return p


def test_browse_with_no_path_no_source(tmp_path):
    path = write_backgrounds(tmp_path, """
<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
    <background name="folder" label="Folder" type="browse" />
</backgrounds>
""")
    config = load_backgrounds(path)
    bg = config.backgrounds[0]
    assert bg.type == BackgroundType.BROWSE
    assert bg.path == ""
    assert bg.browse_sources == []


def test_browse_with_path_only(tmp_path):
    path = write_backgrounds(tmp_path, """
<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
    <background name="folder" label="Folder" type="browse">
        <path>special://profile/folders/</path>
    </background>
</backgrounds>
""")
    config = load_backgrounds(path)
    bg = config.backgrounds[0]
    assert bg.path == "special://profile/folders/"
    assert bg.browse_sources == []


def test_multi_with_path_only(tmp_path):
    path = write_backgrounds(tmp_path, """
<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
    <background name="folder" label="Folder" type="multi">
        <path>special://profile/folders/</path>
    </background>
</backgrounds>
""")
    config = load_backgrounds(path)
    bg = config.backgrounds[0]
    assert bg.type == BackgroundType.MULTI
    assert bg.path == "special://profile/folders/"


def test_browse_with_sources_only(tmp_path):
    path = write_backgrounds(tmp_path, """
<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
    <background name="folder" label="Folder" type="browse">
        <source label="A">special://path-a/</source>
        <source label="B">browse</source>
    </background>
</backgrounds>
""")
    config = load_backgrounds(path)
    bg = config.backgrounds[0]
    assert bg.path == ""
    assert len(bg.browse_sources) == 2


def test_browse_with_both_path_and_source_keeps_sources(tmp_path):
    path = write_backgrounds(tmp_path, """
<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
    <background name="folder" label="Folder" type="browse">
        <path>special://profile/folders/</path>
        <source label="A">browse</source>
    </background>
</backgrounds>
""")
    config = load_backgrounds(path)
    bg = config.backgrounds[0]
    assert bg.path == ""
    assert len(bg.browse_sources) == 1


def test_multi_with_both_path_and_source_keeps_sources(tmp_path):
    path = write_backgrounds(tmp_path, """
<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
    <background name="folder" label="Folder" type="multi">
        <path>special://profile/folders/</path>
        <source>browse</source>
    </background>
</backgrounds>
""")
    config = load_backgrounds(path)
    bg = config.backgrounds[0]
    assert bg.path == ""
    assert len(bg.browse_sources) == 1


def test_static_still_requires_path(tmp_path):
    path = write_backgrounds(tmp_path, """
<?xml version="1.0" encoding="UTF-8"?>
<backgrounds>
    <background name="bg" label="BG" type="static" />
</backgrounds>
""")
    assert load_backgrounds(path).backgrounds == []
