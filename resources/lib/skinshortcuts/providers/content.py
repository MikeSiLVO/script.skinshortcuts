"""Content provider for dynamic shortcut resolution.

Resolves <content> elements to actual shortcuts at runtime by querying
Kodi's JSON-RPC API and filesystem.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

import xbmc
import xbmcvfs

from ..log import get_logger

if TYPE_CHECKING:
    from ..models.menu import Content

log = get_logger("ContentProvider")


PLAYLIST_EXTENSIONS = (".xsp", ".m3u", ".m3u8", ".pls")


@dataclass
class ResolvedShortcut:
    """A shortcut resolved from dynamic content."""

    label: str
    action: str
    icon: str = "DefaultShortcut.png"
    label2: str = ""
    action_play: str = ""
    action_party: str = ""


def scan_playlist_files(directory: str) -> list[tuple[str, str]]:
    """Scan directory for playlist files.

    Args:
        directory: Path to scan (e.g., "{playlists_base}/video/")

    Returns:
        List of (label, filepath) tuples for found playlists.
    """
    playlists = []

    try:
        _dirs, files = xbmcvfs.listdir(directory)
    except Exception:
        return playlists

    for filename in files:
        if filename.endswith(PLAYLIST_EXTENSIONS):
            filepath = directory + filename
            label = filename.rsplit(".", 1)[0]
            playlists.append((label, filepath))

    return playlists


class ContentProvider:
    """Resolves dynamic content references to shortcuts."""

    def __init__(self) -> None:
        self._cache: dict[str, list[ResolvedShortcut]] = {}

    def resolve(self, content: Content) -> list[ResolvedShortcut]:
        """Resolve a content reference to a list of shortcuts.

        Args:
            content: Content object with source and target attributes.

        Returns:
            List of resolved shortcuts.

        Note:
            Condition (property) and visible (Kodi visibility) are checked
            by the caller (picker) before calling this method.
        """
        source = content.source.lower()
        target = content.target.lower() if content.target else ""

        if source == "sources":
            return self._resolve_sources(target)
        if source == "playlists":
            return self._resolve_playlists(target, content.path)
        if source == "addons":
            return self._resolve_addons(target)
        if source == "favourites":
            return self._resolve_favourites()
        if source == "pvr":
            return self._resolve_pvr(target)
        if source == "commands":
            return self._resolve_commands()
        if source == "settings":
            return self._resolve_settings()
        if source == "library":
            return self._resolve_library(target)
        if source == "nodes":
            return self._resolve_nodes(target)

        return []

    def clear_cache(self) -> None:
        """Clear the content cache."""
        self._cache.clear()

    def _resolve_sources(self, target: str) -> list[ResolvedShortcut]:
        """Resolve media sources."""
        cache_key = f"sources_{target}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        media_map = {
            "video": "video",
            "videos": "video",
            "music": "music",
            "audio": "music",
            "pictures": "pictures",
            "images": "pictures",
        }
        media = media_map.get(target, "video")

        result = self._jsonrpc("Files.GetSources", {"media": media})
        if not result or "sources" not in result:
            return []

        window_map = {
            "video": "Videos",
            "music": "Music",
            "pictures": "Pictures",
        }
        window = window_map.get(media, "Videos")

        shortcuts = []
        for source in result["sources"]:
            path = source.get("file", "")
            label = source.get("label", "")
            if path and label:
                shortcuts.append(
                    ResolvedShortcut(
                        label=label,
                        action=f"ActivateWindow({window},{path},return)",
                        icon="DefaultFolder.png",
                    )
                )

        self._cache[cache_key] = shortcuts
        return shortcuts

    def _get_playlists_base_path(self) -> str:
        """Get the playlist base path from Kodi settings.

        Returns the user-configured playlist path, or the default
        special://profile/playlists/ if not set.
        """
        result = self._jsonrpc(
            "Settings.GetSettingValue",
            {"setting": "system.playlistspath"},
        )
        if result and result.get("value"):
            base = result["value"]
            if not base.endswith("/"):
                base += "/"
            return base
        return "special://profile/playlists/"

    def _resolve_playlists(
        self, target: str, custom_path: str = ""
    ) -> list[ResolvedShortcut]:
        """Resolve playlists from standard or custom paths."""
        cache_key = f"playlists_{target}_{custom_path}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Kodi stores playlists in video/, music/, and mixed/ subdirectories
        if custom_path:
            paths = [custom_path]
        else:
            base = self._get_playlists_base_path()
            if target in ("video", "videos"):
                paths = [f"{base}video/", f"{base}mixed/"]
            elif target in ("audio", "music"):
                paths = [f"{base}music/", f"{base}mixed/"]
            else:
                paths = [f"{base}video/", f"{base}music/", f"{base}mixed/"]

        window_map = {
            "video": "Videos",
            "videos": "Videos",
            "audio": "Music",
            "music": "Music",
        }
        default_window = window_map.get(target, "Videos")

        shortcuts = []
        for path in paths:
            shortcuts.extend(self._scan_playlist_directory(path, default_window, target))

        self._cache[cache_key] = shortcuts
        return shortcuts

    def _scan_playlist_directory(
        self, directory: str, default_window: str, target: str = ""
    ) -> list[ResolvedShortcut]:
        """Scan a directory for playlist files and convert to shortcuts."""
        shortcuts = []
        filter_video = target in ("video", "videos")
        filter_music = target in ("audio", "music")

        video_types = ("movies", "tvshows", "episodes", "musicvideos")
        music_types = ("songs", "albums", "artists")

        for label, filepath in scan_playlist_files(directory):
            window = default_window
            display_label = label
            playlist_type = ""

            if filepath.endswith(".xsp"):
                playlist_type, playlist_name = self._parse_smart_playlist(filepath)
                if playlist_name:
                    display_label = playlist_name
                if playlist_type in music_types:
                    window = "Music"
                elif playlist_type in video_types:
                    window = "Videos"

            if filter_video and playlist_type and playlist_type not in video_types:
                continue
            if filter_music and playlist_type and playlist_type not in music_types:
                continue

            action_party = ""
            if window == "Music":
                action_party = f"PlayerControl(PartyMode({filepath}))"

            shortcuts.append(
                ResolvedShortcut(
                    label=display_label,
                    action=f"ActivateWindow({window},{filepath},return)",
                    icon="DefaultPlaylist.png",
                    action_play=f"PlayMedia({filepath})",
                    action_party=action_party,
                )
            )

        return shortcuts

    def _parse_smart_playlist(self, filepath: str) -> tuple[str, str]:
        """Parse a smart playlist (.xsp file) for type and name.

        Returns:
            Tuple of (type, name). Falls back to ("unknown", "") on error.
        """
        try:
            f = xbmcvfs.File(filepath)
            content = f.read()
            f.close()

            import xml.etree.ElementTree as ET

            root = ET.fromstring(content)
            playlist_type = root.get("type") or "unknown"
            name_elem = root.find("name")
            name = name_elem.text if name_elem is not None and name_elem.text else ""
            return playlist_type, name
        except Exception:
            return "unknown", ""

    def _get_smart_playlist_type(self, filepath: str) -> str:
        """Get the type of a smart playlist (.xsp file)."""
        playlist_type, _ = self._parse_smart_playlist(filepath)
        return playlist_type

    def _resolve_addons(self, target: str) -> list[ResolvedShortcut]:
        """Resolve installed addons by content type."""
        cache_key = f"addons_{target}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        content_map = {
            "video": "video",
            "videos": "video",
            "audio": "audio",
            "music": "audio",
            "image": "image",
            "images": "image",
            "pictures": "image",
            "program": "executable",
            "programs": "executable",
            "executable": "executable",
        }
        content = content_map.get(target, "video")

        result = self._jsonrpc(
            "Addons.GetAddons",
            {
                "content": content,
                "enabled": True,
                "properties": ["name", "thumbnail"],
            },
        )
        if not result or "addons" not in result:
            return []

        shortcuts = []
        for addon in result["addons"]:
            addon_id = addon.get("addonid", "")
            name = addon.get("name", addon_id)
            thumb = addon.get("thumbnail", "")

            if addon_id:
                shortcuts.append(
                    ResolvedShortcut(
                        label=name,
                        action=f"RunAddon({addon_id})",
                        icon=thumb or "DefaultAddon.png",
                    )
                )

        self._cache[cache_key] = shortcuts
        return shortcuts

    def _resolve_favourites(self) -> list[ResolvedShortcut]:
        """Resolve user favourites."""
        cache_key = "favourites"
        if cache_key in self._cache:
            return self._cache[cache_key]

        result = self._jsonrpc(
            "Favourites.GetFavourites",
            {"properties": ["thumbnail", "window", "windowparameter", "path"]},
        )
        if not result or "favourites" not in result:
            return []

        shortcuts = []
        for fav in result["favourites"]:
            title = fav.get("title", "")
            fav_type = fav.get("type", "")
            thumb = fav.get("thumbnail", "")

            action = ""
            if fav_type == "media":
                path = fav.get("path", "")
                if path:
                    action = f"PlayMedia({path})"
            elif fav_type == "window":
                window = fav.get("window", "")
                param = fav.get("windowparameter", "")
                if window:
                    if param:
                        action = f"ActivateWindow({window},{param},return)"
                    else:
                        action = f"ActivateWindow({window})"
            elif fav_type == "script":
                path = fav.get("path", "")
                if path:
                    action = f"RunScript({path})"
            elif fav_type == "androidapp":
                path = fav.get("path", "")
                if path:
                    action = f"StartAndroidActivity({path})"

            if title and action:
                shortcuts.append(
                    ResolvedShortcut(
                        label=title,
                        action=action,
                        icon=thumb or "DefaultFavourites.png",
                    )
                )

        self._cache[cache_key] = shortcuts
        return shortcuts

    def _resolve_pvr(self, target: str) -> list[ResolvedShortcut]:
        """Resolve PVR channels."""
        cache_key = f"pvr_{target}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if target in ("tv", "television"):
            if not xbmc.getCondVisibility("Pvr.HasTVChannels"):
                return []
            channel_group = "alltv"
        elif target == "radio":
            if not xbmc.getCondVisibility("Pvr.HasRadioChannels"):
                return []
            channel_group = "allradio"
        else:
            return []

        result = self._jsonrpc(
            "PVR.GetChannels",
            {
                "channelgroupid": channel_group,
                "properties": ["thumbnail", "channelnumber"],
            },
        )
        if not result or "channels" not in result:
            return []

        shortcuts = []
        for channel in result["channels"]:
            channel_id = channel.get("channelid", 0)
            label = channel.get("label", "")
            thumb = channel.get("thumbnail", "")
            number = channel.get("channelnumber", 0)

            if channel_id and label:
                display_label = f"{number}. {label}" if number else label
                shortcuts.append(
                    ResolvedShortcut(
                        label=display_label,
                        action=f"PlayPvrChannel({channel_id})",
                        icon=thumb or "DefaultTVShows.png",
                    )
                )

        self._cache[cache_key] = shortcuts
        return shortcuts

    def _resolve_commands(self) -> list[ResolvedShortcut]:
        """Resolve system commands."""
        commands = [
            ("$LOCALIZE[13012]", "Quit()", "DefaultProgram.png"),  # Quit
            ("$LOCALIZE[13005]", "Reboot()", "DefaultProgram.png"),  # Reboot
            ("$LOCALIZE[13009]", "Powerdown()", "DefaultProgram.png"),  # Power off
            ("$LOCALIZE[13014]", "Suspend()", "DefaultProgram.png"),  # Suspend
            ("$LOCALIZE[13015]", "Hibernate()", "DefaultProgram.png"),  # Hibernate
            ("$LOCALIZE[13016]", "RestartApp()", "DefaultProgram.png"),  # Restart
            ("$LOCALIZE[20183]", "ReloadSkin()", "DefaultProgram.png"),  # Reload skin
        ]

        return [
            ResolvedShortcut(label=label, action=action, icon=icon)
            for label, action, icon in commands
        ]

    def _resolve_settings(self) -> list[ResolvedShortcut]:
        """Resolve settings shortcuts."""
        settings = [
            ("$LOCALIZE[10004]", "ActivateWindow(Settings)", "DefaultAddonService.png"),
            ("$LOCALIZE[10035]", "ActivateWindow(SkinSettings)", "DefaultAddonService.png"),
            ("$LOCALIZE[14201]", "ActivateWindow(PlayerSettings)", "DefaultAddonService.png"),
            ("$LOCALIZE[14212]", "ActivateWindow(MediaSettings)", "DefaultAddonVideo.png"),
            ("$LOCALIZE[14205]", "ActivateWindow(PVRSettings)", "DefaultAddonPVRClient.png"),
            ("$LOCALIZE[14208]", "ActivateWindow(ServiceSettings)", "DefaultAddonService.png"),
            ("$LOCALIZE[10022]", "ActivateWindow(GameSettings)", "DefaultAddonGame.png"),
            ("$LOCALIZE[14207]", "ActivateWindow(InterfaceSettings)", "DefaultAddonService.png"),
            ("$LOCALIZE[14210]", "ActivateWindow(Profiles)", "DefaultUser.png"),
            ("$LOCALIZE[14209]", "ActivateWindow(SystemSettings)", "DefaultAddonService.png"),
            ("$LOCALIZE[10040]", "ActivateWindow(AddonBrowser)", "DefaultAddon.png"),
            ("$LOCALIZE[10003]", "ActivateWindow(FileManager)", "DefaultFolder.png"),
        ]

        return [
            ResolvedShortcut(label=label, action=action, icon=icon)
            for label, action, icon in settings
        ]

    def _resolve_library(self, target: str) -> list[ResolvedShortcut]:
        """Resolve library nodes (genres, years, studios, tags, actors).

        Args:
            target: Library content type. Valid values:
                - "genres", "moviegenres", "tvgenres", "musicgenres"
                - "years", "movieyears", "tvyears"
                - "studios", "moviestudios", "tvstudios"
                - "tags", "movietags", "tvtags"
                - "actors", "movieactors", "tvactors"
                - "directors", "moviedirectors", "tvdirectors"
                - "artists", "albums"
        """
        cache_key = f"library_{target}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        shortcuts: list[ResolvedShortcut] = []
        target_lower = target.lower()

        if target_lower in ("genres", "moviegenres"):
            shortcuts = self._get_video_genres("movie")
        elif target_lower == "tvgenres":
            shortcuts = self._get_video_genres("tvshow")
        elif target_lower == "musicgenres":
            shortcuts = self._get_music_genres()
        elif target_lower in ("years", "movieyears"):
            shortcuts = self._get_video_years("movie")
        elif target_lower == "tvyears":
            shortcuts = self._get_video_years("tvshow")
        elif target_lower in ("studios", "moviestudios"):
            shortcuts = self._get_video_property("movie", "studio", "Studios")
        elif target_lower == "tvstudios":
            shortcuts = self._get_video_property("tvshow", "studio", "Studios")
        elif target_lower in ("tags", "movietags"):
            shortcuts = self._get_video_property("movie", "tag", "Tags")
        elif target_lower == "tvtags":
            shortcuts = self._get_video_property("tvshow", "tag", "Tags")
        elif target_lower in ("actors", "movieactors"):
            shortcuts = self._get_video_actors("movie")
        elif target_lower == "tvactors":
            shortcuts = self._get_video_actors("tvshow")
        elif target_lower in ("directors", "moviedirectors"):
            shortcuts = self._get_video_directors("movie")
        elif target_lower == "tvdirectors":
            shortcuts = self._get_video_directors("tvshow")
        elif target_lower == "artists":
            shortcuts = self._get_music_artists()
        elif target_lower == "albums":
            shortcuts = self._get_music_albums()

        self._cache[cache_key] = shortcuts
        return shortcuts

    def _resolve_nodes(self, target: str) -> list[ResolvedShortcut]:
        """Resolve library nodes (navigation structure from XML files).

        Args:
            target: Node type - "video" or "music"

        Returns:
            List of shortcuts for top-level library navigation nodes.
        """
        cache_key = f"nodes_{target}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        target_lower = target.lower()
        if target_lower not in ("video", "videos", "music"):
            return []

        # Normalize for Kodi library path (uses "video" not "videos")
        lib_type = "video" if target_lower in ("video", "videos") else "music"
        base_path = f"special://xbmc/system/library/{lib_type}/"
        window = "Videos" if lib_type == "video" else "Music"

        shortcuts = []
        try:
            dirs, _files = xbmcvfs.listdir(base_path)
        except Exception:
            self._cache[cache_key] = shortcuts
            return shortcuts

        for dirname in sorted(dirs):
            node_path = f"{base_path}{dirname}/"
            index_file = f"{node_path}index.xml"

            label, icon, order = self._parse_library_node(index_file)
            if label:
                shortcuts.append(
                    ResolvedShortcut(
                        label=label,
                        action=f"ActivateWindow({window},library://{target_lower}/{dirname}/,return)",
                        icon=icon or f"Default{target_lower.capitalize()}.png",
                        label2=str(order),
                    )
                )

        shortcuts.sort(key=lambda s: int(s.label2) if s.label2.isdigit() else 999)
        for shortcut in shortcuts:
            shortcut.label2 = ""

        self._cache[cache_key] = shortcuts
        return shortcuts

    def _parse_library_node(self, index_file: str) -> tuple[str, str, int]:
        """Parse a library node index.xml file.

        Returns:
            Tuple of (label, icon, order). Label is empty string on error.
        """
        try:
            f = xbmcvfs.File(index_file)
            content = f.read()
            f.close()

            if not content:
                return "", "", 999

            import xml.etree.ElementTree as ET

            root = ET.fromstring(content)
            if root.tag != "node":
                return "", "", 999

            label = ""
            label_elem = root.find("label")
            if label_elem is not None and label_elem.text:
                label = label_elem.text
                if not label.startswith("$"):
                    label = f"$LOCALIZE[{label}]" if label.isdigit() else label

            icon = ""
            icon_elem = root.find("icon")
            if icon_elem is not None and icon_elem.text:
                icon = icon_elem.text

            order = 999
            order_attr = root.get("order")
            if order_attr and order_attr.isdigit():
                order = int(order_attr)

            return label, icon, order
        except Exception:
            return "", "", 999

    def _get_video_genres(self, media_type: str) -> list[ResolvedShortcut]:
        """Get video genres (movies or TV shows)."""
        result = self._jsonrpc(
            "VideoLibrary.GetGenres", {"type": media_type, "properties": ["thumbnail"]}
        )
        if not result or "genres" not in result:
            return []

        window = "Videos"
        db_type = "movies" if media_type == "movie" else "tvshows"

        shortcuts = []
        for genre in result["genres"]:
            label = genre.get("label", "")
            thumb = genre.get("thumbnail", "")
            genre_id = genre.get("genreid", 0)
            if label:
                path = f"videodb://{db_type}/genres/{genre_id}/"
                shortcuts.append(
                    ResolvedShortcut(
                        label=label,
                        action=f"ActivateWindow({window},{path},return)",
                        icon=thumb or "DefaultGenre.png",
                    )
                )
        return shortcuts

    def _get_music_genres(self) -> list[ResolvedShortcut]:
        """Get music genres."""
        result = self._jsonrpc("AudioLibrary.GetGenres", {"properties": ["thumbnail"]})
        if not result or "genres" not in result:
            return []

        shortcuts = []
        for genre in result["genres"]:
            label = genre.get("label", "")
            thumb = genre.get("thumbnail", "")
            genre_id = genre.get("genreid", 0)
            if label:
                path = f"musicdb://genres/{genre_id}/"
                shortcuts.append(
                    ResolvedShortcut(
                        label=label,
                        action=f"ActivateWindow(Music,{path},return)",
                        icon=thumb or "DefaultMusicGenres.png",
                    )
                )
        return shortcuts

    def _get_video_years(self, media_type: str) -> list[ResolvedShortcut]:
        """Get years from video library."""
        if media_type == "movie":
            result = self._jsonrpc(
                "VideoLibrary.GetMovies", {"properties": ["year"], "limits": {"end": 0}}
            )
            items = result.get("movies", []) if result else []
            db_type = "movies"
        else:
            result = self._jsonrpc(
                "VideoLibrary.GetTVShows", {"properties": ["year"], "limits": {"end": 0}}
            )
            items = result.get("tvshows", []) if result else []
            db_type = "tvshows"

        if media_type == "movie":
            result = self._jsonrpc("VideoLibrary.GetMovies", {"properties": ["year"]})
            items = result.get("movies", []) if result else []
        else:
            result = self._jsonrpc("VideoLibrary.GetTVShows", {"properties": ["year"]})
            items = result.get("tvshows", []) if result else []

        years = sorted(
            {item.get("year", 0) for item in items if item.get("year", 0) > 0},
            reverse=True,
        )

        shortcuts = []
        for year in years:
            path = f"videodb://{db_type}/years/{year}/"
            shortcuts.append(
                ResolvedShortcut(
                    label=str(year),
                    action=f"ActivateWindow(Videos,{path},return)",
                    icon="DefaultYear.png",
                )
            )
        return shortcuts

    def _get_video_property(
        self, media_type: str, prop: str, icon_suffix: str
    ) -> list[ResolvedShortcut]:
        """Get video library property values (studios, tags)."""
        if media_type == "movie":
            result = self._jsonrpc("VideoLibrary.GetMovies", {"properties": [prop]})
            items = result.get("movies", []) if result else []
            db_type = "movies"
        else:
            result = self._jsonrpc("VideoLibrary.GetTVShows", {"properties": [prop]})
            items = result.get("tvshows", []) if result else []
            db_type = "tvshows"

        values: set[str] = set()
        for item in items:
            prop_value = item.get(prop, [])
            if isinstance(prop_value, list):
                values.update(prop_value)
            elif prop_value:
                values.add(prop_value)

        shortcuts = []
        for value in sorted(values):
            path = f"videodb://{db_type}/{prop}s/{value}/"
            shortcuts.append(
                ResolvedShortcut(
                    label=value,
                    action=f"ActivateWindow(Videos,{path},return)",
                    icon=f"Default{icon_suffix}.png",
                )
            )
        return shortcuts

    def _get_video_actors(self, media_type: str) -> list[ResolvedShortcut]:
        """Get actors from video library."""
        if media_type == "movie":
            result = self._jsonrpc(
                "VideoLibrary.GetMovies", {"properties": ["cast"], "limits": {"end": 100}}
            )
            items = result.get("movies", []) if result else []
            db_type = "movies"
        else:
            result = self._jsonrpc(
                "VideoLibrary.GetTVShows", {"properties": ["cast"], "limits": {"end": 100}}
            )
            items = result.get("tvshows", []) if result else []
            db_type = "tvshows"

        actors: dict[str, str] = {}
        for item in items:
            for actor in item.get("cast", []):
                name = actor.get("name", "")
                if name and name not in actors:
                    actors[name] = actor.get("thumbnail", "")

        shortcuts = []
        for name in sorted(actors.keys()):
            path = f"videodb://{db_type}/actors/{name}/"
            shortcuts.append(
                ResolvedShortcut(
                    label=name,
                    action=f"ActivateWindow(Videos,{path},return)",
                    icon=actors[name] or "DefaultActor.png",
                )
            )
        return shortcuts

    def _get_video_directors(self, media_type: str) -> list[ResolvedShortcut]:
        """Get directors from video library.

        Note: TV shows don't have directors - episodes do. For tvshow media type,
        we query episodes to get directors.
        """
        if media_type == "movie":
            result = self._jsonrpc(
                "VideoLibrary.GetMovies", {"properties": ["director"]}
            )
            items = result.get("movies", []) if result else []
            db_type = "movies"
        else:
            result = self._jsonrpc(
                "VideoLibrary.GetEpisodes",
                {"properties": ["director"], "limits": {"end": 500}},
            )
            items = result.get("episodes", []) if result else []
            db_type = "tvshows"

        directors: set[str] = set()
        for item in items:
            for director in item.get("director", []):
                if director:
                    directors.add(director)

        shortcuts = []
        for name in sorted(directors):
            path = f"videodb://{db_type}/directors/{name}/"
            shortcuts.append(
                ResolvedShortcut(
                    label=name,
                    action=f"ActivateWindow(Videos,{path},return)",
                    icon="DefaultDirector.png",
                )
            )
        return shortcuts

    def _get_music_artists(self) -> list[ResolvedShortcut]:
        """Get music artists."""
        result = self._jsonrpc(
            "AudioLibrary.GetArtists", {"properties": ["thumbnail"], "limits": {"end": 100}}
        )
        if not result or "artists" not in result:
            return []

        shortcuts = []
        for artist in result["artists"]:
            label = artist.get("label", "")
            artist_id = artist.get("artistid", 0)
            thumb = artist.get("thumbnail", "")
            if label and artist_id:
                path = f"musicdb://artists/{artist_id}/"
                shortcuts.append(
                    ResolvedShortcut(
                        label=label,
                        action=f"ActivateWindow(Music,{path},return)",
                        icon=thumb or "DefaultMusicArtists.png",
                    )
                )
        return shortcuts

    def _get_music_albums(self) -> list[ResolvedShortcut]:
        """Get music albums."""
        result = self._jsonrpc(
            "AudioLibrary.GetAlbums",
            {"properties": ["thumbnail", "artist"], "limits": {"end": 100}},
        )
        if not result or "albums" not in result:
            return []

        shortcuts = []
        for album in result["albums"]:
            label = album.get("label", "")
            album_id = album.get("albumid", 0)
            thumb = album.get("thumbnail", "")
            artists = album.get("artist", [])
            artist_str = ", ".join(artists) if artists else ""
            if label and album_id:
                path = f"musicdb://albums/{album_id}/"
                shortcuts.append(
                    ResolvedShortcut(
                        label=label,
                        action=f"ActivateWindow(Music,{path},return)",
                        icon=thumb or "DefaultMusicAlbums.png",
                        label2=artist_str,
                    )
                )
        return shortcuts

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


_provider: ContentProvider | None = None


def resolve_content(content: Content) -> list[ResolvedShortcut]:
    """Resolve a content reference to shortcuts.

    Convenience function using module-level provider instance.
    """
    global _provider
    if _provider is None:
        _provider = ContentProvider()
    return _provider.resolve(content)


def clear_content_cache() -> None:
    """Clear the content provider cache.

    Call this when opening the management dialog to ensure fresh data
    (e.g., newly added favourites are visible in the picker).
    """
    if _provider is not None:
        _provider.clear_cache()
