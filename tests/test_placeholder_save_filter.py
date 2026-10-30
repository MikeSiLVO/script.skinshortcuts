"""Empty-state and add-stub placeholders are visual-only until edited."""

from __future__ import annotations

from pathlib import Path

from skinshortcuts.manager import MenuManager
from skinshortcuts.models.menu import Action, MenuItem


MENUS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<menus>
  <menu name="mainmenu">
    <item name="home">
      <label>Home</label>
      <action>Noop</action>
    </item>
  </menu>
</menus>
"""


def _setup(tmp_path: Path) -> tuple[Path, Path]:
    """Write the test menus.xml into a shortcuts folder; return it and a userdata path."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(MENUS_XML)
    userdata = tmp_path / "userdata.json"
    return skin, userdata


def test_unmodified_placeholder_is_not_saved(tmp_path: Path):
    skin, userdata = _setup(tmp_path)
    manager = MenuManager(skin, userdata_path=str(userdata))

    placeholder = MenuItem(
        name="sub-abc",
        label="New Item",
        icon="DefaultFolder.png",
        is_placeholder=True,
    )
    manager.working["mainmenu"].items.append(placeholder)
    manager._changed = True

    diff = manager._generate_userdata()
    assert "mainmenu" not in diff.menus


def test_edited_placeholder_is_saved(tmp_path: Path):
    skin, userdata = _setup(tmp_path)
    manager = MenuManager(skin, userdata_path=str(userdata))

    placeholder = MenuItem(
        name="sub-abc",
        label="New Item",
        icon="DefaultFolder.png",
        is_placeholder=True,
    )
    manager.working["mainmenu"].items.append(placeholder)

    manager.set_label("mainmenu", "sub-abc", "My Custom Label")

    diff = manager._generate_userdata()
    assert "mainmenu" in diff.menus
    saved_names = [i.name for i in diff.menus["mainmenu"].items]
    assert "sub-abc" in saved_names


def test_manager_add_item_creates_placeholder(tmp_path: Path):
    skin, userdata = _setup(tmp_path)
    manager = MenuManager(skin, userdata_path=str(userdata))

    new_item = manager.add_item("mainmenu")

    assert new_item.is_placeholder is True


def test_add_item_with_label_is_not_placeholder(tmp_path: Path):
    skin, userdata = _setup(tmp_path)
    manager = MenuManager(skin, userdata_path=str(userdata))

    new_item = manager.add_item("mainmenu", label="Real Item")

    assert new_item.is_placeholder is False


def test_add_item_with_explicit_item_is_not_placeholder(tmp_path: Path):
    skin, userdata = _setup(tmp_path)
    manager = MenuManager(skin, userdata_path=str(userdata))

    provided = MenuItem(name="my-item", label="From Widget", actions=[Action(action="Noop")])
    new_item = manager.add_item("mainmenu", item=provided)

    assert new_item.is_placeholder is False


def test_rapid_adds_only_modified_persist(tmp_path: Path):
    skin, userdata = _setup(tmp_path)
    manager = MenuManager(skin, userdata_path=str(userdata))

    a = manager.add_item("mainmenu")
    b = manager.add_item("mainmenu")
    c = manager.add_item("mainmenu")
    d = manager.add_item("mainmenu")

    manager.set_label("mainmenu", b.name, "Edited B")
    manager.set_action("mainmenu", c.name, "ActivateWindow(Settings)")

    diff = manager._generate_userdata()
    saved_names = {i.name for i in diff.menus["mainmenu"].items}
    assert b.name in saved_names
    assert c.name in saved_names
    assert a.name not in saved_names
    assert d.name not in saved_names


def test_custom_property_clears_placeholder(tmp_path: Path):
    skin, userdata = _setup(tmp_path)
    manager = MenuManager(skin, userdata_path=str(userdata))

    item = manager.add_item("mainmenu")
    assert item.is_placeholder is True

    manager.set_custom_property("mainmenu", item.name, "widget", "some-widget")

    assert item.is_placeholder is False
