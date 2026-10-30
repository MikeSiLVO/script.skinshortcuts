"""Drive the real ManagementDialog outside Kodi: fake list controls, ListItems and doModal."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest
import xbmcgui

import skinshortcuts.dialog as dialog_pkg
from skinshortcuts.dialog import ManagementDialog
from skinshortcuts.manager import MenuManager


class FakeListItem:
    """ListItem stand-in keeping label and properties readable."""

    def __init__(self, label: str = "", label2: str = "", offscreen: bool = False) -> None:
        self.label = label
        self.label2 = label2
        self.offscreen = offscreen
        self.props: dict[str, str] = {}
        self.art: dict[str, str] = {}

    def setLabel(self, label: str) -> None:  # noqa: N802
        self.label = label

    def setLabel2(self, label: str) -> None:  # noqa: N802
        self.label2 = label

    def setProperty(self, key: str, value: str) -> None:  # noqa: N802
        self.props[key.lower()] = value

    def getProperty(self, key: str) -> str:  # noqa: N802
        return self.props.get(key.lower(), "")

    def setArt(self, art: dict[str, str]) -> None:  # noqa: N802
        self.art.update(art)


class FakeList:
    """List control stand-in; selection lands on row 0 once rows exist."""

    def __init__(self) -> None:
        self.rows: list[FakeListItem] = []
        self.pos = -1
        self.sizes: list[int] = []

    def reset(self) -> None:
        self.rows = []
        self.pos = -1
        self.sizes.append(0)

    def size(self) -> int:
        return len(self.rows)

    def removeItem(self, index: int) -> None:  # noqa: N802
        del self.rows[index]
        self.sizes.append(len(self.rows))

    def addItems(self, items: list[FakeListItem]) -> None:  # noqa: N802
        self.rows.extend(items)
        if self.pos < 0 and self.rows:
            self.pos = 0
        self.sizes.append(len(self.rows))

    def addItem(self, item: FakeListItem) -> None:  # noqa: N802
        self.addItems([item])

    def selectItem(self, index: int) -> None:  # noqa: N802
        self.pos = index

    def getSelectedPosition(self) -> int:  # noqa: N802
        return self.pos

    def getSelectedItem(self) -> FakeListItem | None:  # noqa: N802
        return self.rows[self.pos] if 0 <= self.pos < len(self.rows) else None

    def names(self) -> list[str]:
        """Item names shown, in row order."""
        return [row.getProperty("name") for row in self.rows]


class HarnessDialog(ManagementDialog):
    """ManagementDialog with fake controls and window properties."""

    child_scripts: list[Callable[[HarnessDialog], None]] = []
    opened: list[HarnessDialog] = []

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(**kwargs)
        self.controls = {211: FakeList(), 212: FakeList()}
        self.window_props: dict[str, str] = {}
        self.closed = False
        HarnessDialog.opened.append(self)

    def getControl(self, control_id: int):  # noqa: N802
        if control_id in self.controls:
            return self.controls[control_id]
        raise RuntimeError(f"no control {control_id}")

    def setProperty(self, key: str, value: str) -> None:  # noqa: N802
        self.window_props[key] = value

    def clearProperty(self, key: str) -> None:  # noqa: N802
        self.window_props.pop(key, None)

    def getProperty(self, key: str) -> str:  # noqa: N802
        return self.window_props.get(key, "")

    def setFocusId(self, control_id: int) -> None:  # noqa: N802
        pass

    def getFocusId(self) -> int:  # noqa: N802
        return 211

    def close(self) -> None:
        self.closed = True
        super().close()

    def doModal(self) -> None:  # noqa: N802
        self.onInit()
        if HarnessDialog.child_scripts:
            HarnessDialog.child_scripts.pop(0)(self)
        self.close()


def home() -> dict[str, str]:
    """Home window properties as the fake Window records them."""
    return xbmcgui.Window(10000).props


@pytest.fixture(name="harness")
def harness_fixture(monkeypatch: pytest.MonkeyPatch):
    """Patch the Kodi GUI stubs the dialog needs and route children through the harness."""
    monkeypatch.setattr(xbmcgui, "ListItem", FakeListItem)
    monkeypatch.setattr(xbmcgui.WindowXMLDialog, "close", lambda self: None, raising=False)
    monkeypatch.setattr(xbmcgui.Window, "_instances", {})
    monkeypatch.setattr(dialog_pkg, "ManagementDialog", HarnessDialog)
    monkeypatch.setattr(HarnessDialog, "child_scripts", [])
    monkeypatch.setattr(HarnessDialog, "opened", [])
    return HarnessDialog


def write_skin(tmp_path: Path, menus_xml: str, **files: str) -> Path:
    """Write a shortcuts folder holding menus.xml plus any named extra files."""
    skin = tmp_path / "shortcuts"
    skin.mkdir()
    (skin / "menus.xml").write_text(menus_xml, encoding="utf-8")
    for name, text in files.items():
        (skin / f"{name}.xml").write_text(text, encoding="utf-8")
    return skin


def open_root(skin: Path, tmp_path: Path, menu_id: str = "mainmenu", **kwargs) -> HarnessDialog:
    """Open a root dialog on the skin with userdata in the test's temp folder, onInit done."""
    dialog = HarnessDialog(menu_id=menu_id, shortcuts_path=str(skin), **kwargs)
    dialog.manager = MenuManager(skin, userdata_path=str(tmp_path / "userdata.json"))
    dialog.onInit()
    return dialog
