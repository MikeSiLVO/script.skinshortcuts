"""Entry point for Skin Shortcuts."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import parse_qs

try:
    import xbmc
    import xbmcvfs

    IN_KODI = True
except ImportError:
    IN_KODI = False

from .config import SkinConfig
from .constants import INCLUDES_FILE, MENU_FILE, MENUS_FILE
from .dialog import show_management_dialog
from .hashing import generate_config_hashes, needs_rebuild, write_hashes
from .userdata import get_userdata_path


def log(msg: str, level: int = 0) -> None:
    """Log message to Kodi log or stdout."""
    if IN_KODI:
        xbmc.log(f"[script.skinshortcuts] {msg}", level)
    else:
        print(f"[skinshortcuts] {msg}")


def get_skin_path() -> str:
    """Get current skin's shortcuts folder path."""
    if IN_KODI:
        skin_path = xbmcvfs.translatePath("special://skin/shortcuts/")
        return skin_path
    return ""


def get_output_paths() -> list[str]:
    """Get paths for includes.xml output by parsing skin's addon.xml."""
    if not IN_KODI:
        return []

    addon_xml_path = xbmcvfs.translatePath("special://skin/addon.xml")
    if not xbmcvfs.exists(addon_xml_path):
        log("Could not find skin addon.xml")
        return []

    try:
        tree = ET.parse(addon_xml_path)
        root = tree.getroot()

        paths = []
        for ext in root.findall("extension"):
            if ext.get("point") == "xbmc.gui.skin":
                for res in ext.findall("res"):
                    folder = res.get("folder")
                    if folder:
                        path = xbmcvfs.translatePath(f"special://skin/{folder}/")
                        if xbmcvfs.exists(path):
                            paths.append(path)
                break

        return paths
    except ET.ParseError as e:
        log(f"Error parsing addon.xml: {e}")
        return []


def build_includes(
    shortcuts_path: str | None = None,
    output_path: str | None = None,
    force: bool = False,
) -> bool:
    """Build includes.xml from skin config files.

    Args:
        shortcuts_path: Path to shortcuts folder (default: special://skin/shortcuts/)
        output_path: Path to write includes.xml (default: auto-detect from addon.xml)
        force: Force rebuild even if hashes match

    Returns:
        True if built successfully, False otherwise
    """
    log(f"build_includes called: path={shortcuts_path}, output={output_path}, force={force}")

    if shortcuts_path is None:
        shortcuts_path = get_skin_path()
        log(f"Auto-detected shortcuts path: {shortcuts_path}")

    if not shortcuts_path:
        log("Could not determine skin shortcuts path", xbmc.LOGERROR if IN_KODI else 0)
        return False

    # Check if config files exist
    path = Path(shortcuts_path)
    menus_file = path / MENUS_FILE
    menu_file = path / MENU_FILE

    if not menus_file.exists() and not menu_file.exists():
        log(f"No menu config found in {shortcuts_path}", xbmc.LOGWARNING if IN_KODI else 0)
        return False

    # Determine output paths early so we can check if files exist
    if output_path:
        output_paths = [output_path]
    else:
        output_paths = get_output_paths()

    # Check if rebuild is needed (also checks if output files exist)
    if not force and not needs_rebuild(shortcuts_path, output_paths):
        log("Menu is up to date, skipping rebuild")
        return False

    log(f"Loading config from: {shortcuts_path}")

    try:
        # SkinConfig.load() merges userdata by default (load_user=True)
        config = SkinConfig.load(shortcuts_path)
        log(
            f"Loaded {len(config.menus)} menus, "
            f"{len(config.widgets)} widgets, {len(config.backgrounds)} backgrounds"
        )

        if not config.menus:
            log("No menus found in config", xbmc.LOGWARNING if IN_KODI else 0)
            return False

        if not output_paths:
            log("Could not determine output paths", xbmc.LOGERROR if IN_KODI else 0)
            return False

        # Write to all resolution folders
        for out_path in output_paths:
            output_file = Path(out_path) / INCLUDES_FILE
            config.build_includes(str(output_file))
            log(f"Generated: {output_file}")

        # Save hashes after successful build
        hashes = generate_config_hashes(shortcuts_path)
        write_hashes(hashes)
        log("Saved config hashes")

        # Reload skin to apply changes
        if IN_KODI:
            xbmc.executebuiltin("ReloadSkin()")

        return True

    except Exception as e:
        log(f"Error building includes: {e}", xbmc.LOGERROR if IN_KODI else 0)
        import traceback
        log(traceback.format_exc(), xbmc.LOGERROR if IN_KODI else 0)
        return False


def clear_custom_menu(
    menu: str,
    property_name: str = "",
    shortcuts_path: str | None = None,
) -> bool:
    """Clear a custom widget menu and optionally reset a property.

    Called via RunScript to clear custom widget items. The menu parameter
    should be the custom menu name (e.g., "movies.customwidget").

    If property_name is specified, it will also clear the widget property
    on the parent item (e.g., clear "widget" property on "movies" item).

    Args:
        menu: Custom menu name to clear (e.g., "movies.customwidget")
        property_name: Optional property to clear on parent item
        shortcuts_path: Path to shortcuts folder

    Returns:
        True if cleared successfully
    """
    if not menu:
        log("clear_custom_menu: No menu specified")
        return False

    log(f"Clearing custom menu: {menu}, property: {property_name}")

    if shortcuts_path is None:
        shortcuts_path = get_skin_path()

    try:
        from .manager import MenuManager

        manager = MenuManager(shortcuts_path)

        # Get the custom menu
        custom_menu = manager.config.get_menu(menu)
        if custom_menu:
            # Clear all items from the menu
            custom_menu.items.clear()
            manager._changed = True
            log(f"Cleared items from menu: {menu}")

        # If property_name specified, clear it on parent item
        # Menu name format: {parent_item}.customwidget or {parent_item}.customwidget.2
        if property_name and ".customwidget" in menu:
            # Extract parent item name from menu name
            # e.g., "movies.customwidget" -> "movies", "movies.customwidget.2" -> "movies"
            parent_name = menu.split(".customwidget")[0]
            # Find parent menu (typically mainmenu for most items)
            for parent_menu in manager.config.menus:
                item = parent_menu.get_item(parent_name)
                if item:
                    # Clear the widget property and related properties
                    props_to_clear = [
                        property_name,
                        f"{property_name}Name",
                        f"{property_name}Path",
                        f"{property_name}Type",
                        f"{property_name}Target",
                        f"{property_name}Label",
                    ]
                    for prop in props_to_clear:
                        if prop in item.properties:
                            del item.properties[prop]
                    manager._changed = True
                    log(f"Cleared {property_name} property on item: {parent_name}")
                    break

        # Save changes
        if manager.has_changes():
            manager.save()
            log("Saved changes after clearing")
            # Rebuild includes
            build_includes(shortcuts_path, force=True)

        return True

    except Exception as e:
        log(f"Error clearing custom menu: {e}", xbmc.LOGERROR if IN_KODI else 0)
        import traceback
        log(traceback.format_exc(), xbmc.LOGERROR if IN_KODI else 0)
        return False


def reset_all_menus(shortcuts_path: str | None = None) -> bool:
    """Reset all menus to skin defaults by deleting skin's userdata.

    Args:
        shortcuts_path: Path to shortcuts folder (for rebuild after reset)

    Returns:
        True if reset successfully
    """
    if not IN_KODI:
        return False

    import xbmcgui

    # Confirm with user
    if not xbmcgui.Dialog().yesno(
        xbmc.getLocalizedString(186),  # "Reset"
        "Reset all menus to skin defaults?[CR]All customizations will be removed.",
    ):
        return False

    # Delete skin's userdata file
    userdata_path = Path(get_userdata_path())
    if userdata_path.exists():
        try:
            userdata_path.unlink()
            log(f"Deleted userdata: {userdata_path}")
        except OSError as e:
            log(f"Error deleting userdata: {e}", xbmc.LOGERROR)
            return False
    else:
        log("No userdata to reset")

    # Rebuild includes
    if shortcuts_path is None:
        shortcuts_path = get_skin_path()

    build_includes(shortcuts_path, force=True)
    return True


def main() -> None:
    """Main entry point for RunScript."""
    log("Skin Shortcuts started")

    # Parse arguments
    args = {}
    if len(sys.argv) > 1:
        # Handle both ?param=value and param=value formats
        query = sys.argv[1].lstrip("?")
        args = {k: v[0] for k, v in parse_qs(query).items()}

    action = args.get("type", "buildxml")

    if action == "buildxml":
        shortcuts_path = args.get("path")
        output_path = args.get("output")
        force = args.get("force", "").lower() == "true"
        build_includes(shortcuts_path, output_path, force)
    elif action == "manage":
        menu_id = args.get("menu", "mainmenu")
        shortcuts_path = args.get("path")
        log(f"Opening management dialog: menu_id={menu_id}, path={shortcuts_path}")
        changes_saved = False
        try:
            changes_saved = show_management_dialog(menu_id=menu_id, shortcuts_path=shortcuts_path)
        except Exception as e:
            log(f"Error in management dialog: {e}", xbmc.LOGERROR if IN_KODI else 0)
            import traceback
            log(traceback.format_exc(), xbmc.LOGERROR if IN_KODI else 0)
        # Only rebuild if changes were saved
        log(f"Dialog returned changes_saved={changes_saved}")
        if changes_saved:
            log("Changes saved, rebuilding includes")
            result = build_includes(shortcuts_path, force=True)
            log(f"build_includes returned: {result}")
        else:
            log("No changes saved, skipping rebuild")
    elif action == "resetall":
        # Reset all menus to skin defaults
        reset_all_menus(args.get("path"))
    elif action == "clear":
        # Clear a custom widget menu and optionally a property
        clear_custom_menu(
            menu=args.get("menu", ""),
            property_name=args.get("property", ""),
            shortcuts_path=args.get("path"),
        )
    else:
        log(f"Unknown action: {action}", xbmc.LOGWARNING if IN_KODI else 0)


if __name__ == "__main__":
    main()
