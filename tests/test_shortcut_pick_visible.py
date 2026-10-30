"""Picking a shortcut replaces the item's runtime visible condition, an empty one included."""

from __future__ import annotations

from pathlib import Path

from harness import harness_fixture, open_root, write_skin  # noqa: F401

from skinshortcuts.config import SkinConfig
from skinshortcuts.manager import MenuManager
from skinshortcuts.models.menu import Action, Shortcut

GAMES_VISIBLE = "System.GetBool(gamesgeneral.enable)"

MENUS = f"""<menus>
  <menu name="mainmenu">
    <item name="games">
      <label>Games</label><action>ActivateWindow(Games)</action>
      <visible>{GAMES_VISIBLE}</visible>
    </item>
  </menu>
  <groupings>
    <shortcut name="movies" label="Movies"><action>ActivateWindow(Videos)</action></shortcut>
  </groupings>
</menus>"""


def _pick(tmp_path: Path, item_visible: str):
    """Pick a movies shortcut with a given item visible on the root dialog's first item."""
    dialog = open_root(write_skin(tmp_path, MENUS), tmp_path)
    movies = Shortcut(
        name="movies",
        label="Movies",
        actions=[Action(action="ActivateWindow(Videos)")],
        item_visible=item_visible,
    )
    dialog._pick_shortcut = lambda _groups, _props: movies
    dialog._choose_shortcut()
    return dialog


def test_shortcut_visible_replaces_the_item_visible(harness, tmp_path: Path) -> None:
    dialog = _pick(tmp_path, "Library.HasContent(movies)")
    assert dialog.items[0].visible == "Library.HasContent(movies)"


def test_shortcut_without_visible_clears_the_item_visible(harness, tmp_path: Path) -> None:
    dialog = _pick(tmp_path, "")
    assert dialog.items[0].label == "Movies"
    assert dialog.items[0].visible == ""


def test_cleared_visible_stays_out_of_the_build(harness, tmp_path: Path) -> None:
    dialog = _pick(tmp_path, "")
    dialog.manager.save()
    output = tmp_path / "includes.xml"
    userdata = str(tmp_path / "userdata.json")
    SkinConfig.load(dialog.shortcuts_path, userdata_path=userdata).build_includes(output)
    assert GAMES_VISIBLE not in output.read_text()


def test_emptied_visible_survives_save_and_reload(harness, tmp_path: Path) -> None:
    dialog = open_root(write_skin(tmp_path, MENUS), tmp_path)
    dialog.manager.set_visible("mainmenu", "games", "")
    dialog.manager.save()
    reloaded = MenuManager(dialog.shortcuts_path, userdata_path=str(tmp_path / "userdata.json"))
    assert reloaded.working["mainmenu"].items[0].visible == ""
