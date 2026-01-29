"""Browse provider for navigating Kodi paths.

Uses Files.GetDirectory JSON-RPC to list directory contents and detect
browsable (directory) vs selectable (file) items.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import xbmc

from ..log import get_logger

log = get_logger("BrowseProvider")


@dataclass
class BrowseItem:
    """An item from a directory listing."""

    label: str
    path: str
    icon: str
    is_directory: bool
    mimetype: str = ""


class BrowseProvider:
    """Lists directory contents via JSON-RPC."""

    def list_directory(self, path: str) -> list[BrowseItem] | None:
        """List contents of a directory.

        Args:
            path: The path to list (plugin://, videodb://, library://, etc.)

        Returns:
            List of BrowseItem objects, empty list for empty directories,
            or None if path is not listable (error).
        """
        result = self._jsonrpc(
            "Files.GetDirectory",
            {
                "directory": path,
                "media": "files",
                "properties": ["file", "mimetype"],
            },
        )

        if result is None:
            return None

        if "files" not in result:
            return []

        items = []
        for file_info in result["files"]:
            label = file_info.get("label", "")
            file_path = file_info.get("file", "")
            filetype = file_info.get("filetype", "file")
            mimetype = file_info.get("mimetype", "")

            if not file_path:
                continue

            icon = self._get_icon_for_item(file_info, filetype)

            items.append(
                BrowseItem(
                    label=label,
                    path=file_path,
                    icon=icon,
                    is_directory=(filetype == "directory"),
                    mimetype=mimetype,
                )
            )

        return items

    def is_browsable(self, path: str) -> bool:
        """Check if a path can be browsed into.

        Returns True if the path is a directory that can be listed.
        """
        if not path:
            return False

        browsable_prefixes = (
            "plugin://",
            "videodb://",
            "musicdb://",
            "library://",
            "addons://",
            "sources://",
            "pvr://",
            "special://",
            "upnp://",
        )

        if path.startswith(browsable_prefixes):
            return True

        return path.endswith("/")

    def _get_icon_for_item(self, file_info: dict, filetype: str) -> str:
        """Determine appropriate icon for an item."""
        if filetype == "directory":
            return "DefaultFolder.png"

        mimetype = file_info.get("mimetype", "")
        if mimetype.startswith("video/"):
            return "DefaultVideo.png"
        if mimetype.startswith("audio/"):
            return "DefaultAudio.png"
        if mimetype.startswith("image/"):
            return "DefaultPicture.png"

        return "DefaultFile.png"

    def _jsonrpc(self, method: str, params: dict | None = None) -> dict | None:
        """Execute a JSON-RPC request."""
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1,
        }

        try:
            response_str = xbmc.executeJSONRPC(json.dumps(request))
            response = json.loads(response_str)

            if "result" in response:
                return response["result"]
            if "error" in response:
                log.warning(f"JSON-RPC error for {method}: {response['error']}")
        except Exception as e:
            log.error(f"JSON-RPC exception for {method}: {e}")

        return None


_provider: BrowseProvider | None = None


def get_browse_provider() -> BrowseProvider:
    """Get the module-level browse provider instance."""
    global _provider
    if _provider is None:
        _provider = BrowseProvider()
    return _provider
