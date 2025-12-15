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

if TYPE_CHECKING:
    from ..models.menu import Content


PLAYLIST_EXTENSIONS = (".xsp", ".m3u", ".m3u8", ".pls")


@dataclass
class ResolvedShortcut:
    """A shortcut resolved from dynamic content."""

    label: str
    action: str
    icon: str = "DefaultShortcut.png"
    label2: str = ""


def scan_playlist_files(directory: str) -> list[tuple[str, str]]:
    """Scan directory for playlist files.

    Args:
        directory: Path to scan (e.g., "special://videoplaylists/")

    Returns:
        List of (label, filepath) tuples for found playlists.
    """
    playlists = []

    try:
        dirs, files = xbmcvfs.listdir(directory)
    except Exception:
        return playlists

    for filename in files:
        if filename.endswith(PLAYLIST_EXTENSIONS):
            filepath = directory + filename
            label = filename.rsplit(".", 1)[0]  # Remove extension
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

        # Route to appropriate resolver
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

        return []

    def clear_cache(self) -> None:
        """Clear the content cache."""
        self._cache.clear()

    # -------------------------------------------------------------------------
    # Sources (video, music, pictures)
    # -------------------------------------------------------------------------

    def _resolve_sources(self, target: str) -> list[ResolvedShortcut]:
        """Resolve media sources."""
        cache_key = f"sources_{target}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Map target to media type
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

        # Map to window for action
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

    # -------------------------------------------------------------------------
    # Playlists (video, audio)
    # -------------------------------------------------------------------------

    def _resolve_playlists(
        self, target: str, custom_path: str = ""
    ) -> list[ResolvedShortcut]:
        """Resolve playlists from standard or custom paths."""
        cache_key = f"playlists_{target}_{custom_path}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Default playlist paths based on target
        if custom_path:
            paths = [custom_path]
        elif target in ("video", "videos"):
            paths = ["special://videoplaylists/"]
        elif target in ("audio", "music"):
            paths = ["special://musicplaylists/"]
        else:
            # Both video and audio playlists
            paths = ["special://videoplaylists/", "special://musicplaylists/"]

        # Map target to window
        window_map = {
            "video": "Videos",
            "videos": "Videos",
            "audio": "Music",
            "music": "Music",
        }
        default_window = window_map.get(target, "Videos")

        shortcuts = []
        for path in paths:
            shortcuts.extend(self._scan_playlist_directory(path, default_window))

        self._cache[cache_key] = shortcuts
        return shortcuts

    def _scan_playlist_directory(
        self, directory: str, default_window: str
    ) -> list[ResolvedShortcut]:
        """Scan a directory for playlist files and convert to shortcuts."""
        shortcuts = []

        for label, filepath in scan_playlist_files(directory):
            # Determine window based on playlist type
            window = default_window
            if filepath.endswith(".xsp"):
                # Smart playlists - check content type
                playlist_type = self._get_smart_playlist_type(filepath)
                if playlist_type in ("songs", "albums", "artists", "mixed"):
                    window = "Music"
                else:
                    window = "Videos"

            shortcuts.append(
                ResolvedShortcut(
                    label=label,
                    action=f"ActivateWindow({window},{filepath},return)",
                    icon="DefaultPlaylist.png",
                )
            )

        return shortcuts

    def _get_smart_playlist_type(self, filepath: str) -> str:
        """Get the type of a smart playlist (.xsp file)."""
        try:
            f = xbmcvfs.File(filepath)
            content = f.read()
            f.close()

            # Simple XML parsing for type attribute
            import xml.etree.ElementTree as ET

            root = ET.fromstring(content)
            return root.get("type") or "unknown"
        except Exception:
            return "unknown"

    # -------------------------------------------------------------------------
    # Addons (video, audio, image, program)
    # -------------------------------------------------------------------------

    def _resolve_addons(self, target: str) -> list[ResolvedShortcut]:
        """Resolve installed addons by content type."""
        cache_key = f"addons_{target}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Map target to content parameter
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

    # -------------------------------------------------------------------------
    # Favourites
    # -------------------------------------------------------------------------

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

            # Build action based on favourite type
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

    # -------------------------------------------------------------------------
    # PVR (tv, radio)
    # -------------------------------------------------------------------------

    def _resolve_pvr(self, target: str) -> list[ResolvedShortcut]:
        """Resolve PVR channels."""
        cache_key = f"pvr_{target}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Check if PVR is available
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
                # Include channel number in label if available
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

    # -------------------------------------------------------------------------
    # Commands (system commands)
    # -------------------------------------------------------------------------

    def _resolve_commands(self) -> list[ResolvedShortcut]:
        """Resolve system commands."""
        # These are static, no caching needed
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

    # -------------------------------------------------------------------------
    # Settings
    # -------------------------------------------------------------------------

    def _resolve_settings(self) -> list[ResolvedShortcut]:
        """Resolve settings shortcuts."""
        # These are static
        settings = [
            ("$LOCALIZE[10004]", "ActivateWindow(Settings)", "DefaultAddonService.png"),
            (
                "$LOCALIZE[166]",
                "ActivateWindow(SkinSettings)",
                "DefaultAddonService.png",
            ),
            ("$LOCALIZE[14083]", "ActivateWindow(VideoSettings)", "DefaultAddonVideo.png"),
            ("$LOCALIZE[14081]", "ActivateWindow(MusicSettings)", "DefaultAddonMusic.png"),
            ("$LOCALIZE[14082]", "ActivateWindow(PictureSettings)", "DefaultAddonPicture.png"),
            ("$LOCALIZE[14092]", "ActivateWindow(GameSettings)", "DefaultAddonGame.png"),
            ("$LOCALIZE[14094]", "ActivateWindow(PlayerSettings)", "DefaultAddonService.png"),
            ("$LOCALIZE[14086]", "ActivateWindow(ServiceSettings)", "DefaultAddonService.png"),
            ("$LOCALIZE[14084]", "ActivateWindow(SystemSettings)", "DefaultAddonService.png"),
            ("$LOCALIZE[24001]", "ActivateWindow(AddonBrowser)", "DefaultAddon.png"),
            ("$LOCALIZE[13200]", "ActivateWindow(Profiles)", "DefaultUser.png"),
            ("$LOCALIZE[7]", "ActivateWindow(FileManager)", "DefaultFolder.png"),
        ]

        return [
            ResolvedShortcut(label=label, action=action, icon=icon)
            for label, action, icon in settings
        ]

    # -------------------------------------------------------------------------
    # Library (genres, years, studios, tags, actors)
    # -------------------------------------------------------------------------

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

        # Route to appropriate library resolver based on target
        target_lower = target.lower()

        # Genres
        if target_lower in ("genres", "moviegenres"):
            shortcuts = self._get_video_genres("movie")
        elif target_lower == "tvgenres":
            shortcuts = self._get_video_genres("tvshow")
        elif target_lower == "musicgenres":
            shortcuts = self._get_music_genres()

        # Years
        elif target_lower in ("years", "movieyears"):
            shortcuts = self._get_video_years("movie")
        elif target_lower == "tvyears":
            shortcuts = self._get_video_years("tvshow")

        # Studios
        elif target_lower in ("studios", "moviestudios"):
            shortcuts = self._get_video_property("movie", "studio", "Studios")
        elif target_lower == "tvstudios":
            shortcuts = self._get_video_property("tvshow", "studio", "Studios")

        # Tags
        elif target_lower in ("tags", "movietags"):
            shortcuts = self._get_video_property("movie", "tag", "Tags")
        elif target_lower == "tvtags":
            shortcuts = self._get_video_property("tvshow", "tag", "Tags")

        # Actors
        elif target_lower in ("actors", "movieactors"):
            shortcuts = self._get_video_actors("movie")
        elif target_lower == "tvactors":
            shortcuts = self._get_video_actors("tvshow")

        # Directors
        elif target_lower in ("directors", "moviedirectors"):
            shortcuts = self._get_video_directors("movie")
        elif target_lower == "tvdirectors":
            shortcuts = self._get_video_directors("tvshow")

        # Music-specific
        elif target_lower == "artists":
            shortcuts = self._get_music_artists()
        elif target_lower == "albums":
            shortcuts = self._get_music_albums()

        self._cache[cache_key] = shortcuts
        return shortcuts

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
                # Navigate to genre in library
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
        # Kodi doesn't have a direct GetYears method, so we query movies/tvshows
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

        # Get unique years - need to query without limit to get all years
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

        # Collect unique values
        values: set[str] = set()
        for item in items:
            prop_value = item.get(prop, [])
            if isinstance(prop_value, list):
                values.update(prop_value)
            elif prop_value:
                values.add(prop_value)

        shortcuts = []
        for value in sorted(values):
            # Use filter path for studios/tags
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

        # Collect unique actors with thumbnails
        actors: dict[str, str] = {}  # name -> thumbnail
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
            # TV shows don't have director field - episodes do
            result = self._jsonrpc(
                "VideoLibrary.GetEpisodes",
                {"properties": ["director"], "limits": {"end": 500}},
            )
            items = result.get("episodes", []) if result else []
            db_type = "tvshows"

        # Collect unique directors
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

    # -------------------------------------------------------------------------
    # JSON-RPC Helper
    # -------------------------------------------------------------------------

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
                xbmc.log(
                    f"JSON-RPC error for {method}: {response['error']}",
                    xbmc.LOGWARNING,
                )
        except Exception as e:
            xbmc.log(f"JSON-RPC exception for {method}: {e}", xbmc.LOGERROR)

        return None


# Module-level singleton for convenience
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
