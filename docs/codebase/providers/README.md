# providers/

Live data from Kodi for the pickers. Both modules import `xbmc` at the top, so they only load inside Kodi or under the test stubs. `providers/__init__.py` exports nothing; import from the module.

| Module | Provides |
|--------|----------|
| `content.py` | `ContentProvider`: resolves `<content>` elements into shortcuts through JSON-RPC and playlist folder scans |
| `browse.py` | `BrowseProvider`: lists a path's entries through `Files.GetDirectory` for browse-into |

The sources and targets a skin can use are documented in [skinning/menus.md](../../skinning/menus.md#dynamic-content) and [skinning/widgets.md](../../skinning/widgets.md#dynamic-content).

## ContentProvider

- `resolve` dispatches on `content.source` to one `_resolve_*` method per source. Each resolver turns the skin's target word into what its JSON-RPC method accepts; sources, playlists and addons go through alias tables at the top of the module. An unknown source or target gives an empty list, and the three alias-table resolvers also log the valid targets.
- Results are `ResolvedShortcut` objects. The pickers turn them into `Shortcut` or `Widget` objects (`PickersMixin._resolve_content_to_shortcuts`, `_resolve_content_to_widgets`). A result with `action_play` makes the picker ask whether to show, play or party-play; one with `browse_path` can be browsed into; one with `source_media` is a media source and goes through the source playlist flow in `playlists.py`.
- Each instance caches its JSON-RPC and folder scan results by source and target. The dialog keeps one instance per dialog tree (`PickersMixin._get_content_provider`, handed to every child), so results stay cached until the root dialog closes.
- Icon overrides apply to every result's icon.
- `_collection` reads a JSON-RPC list field the same way whether Kodi sent `null`, left the key out or sent an empty list.
- `scan_playlist_files` and `library_node_type` are module functions shared with the dialog: the background playlist picker and the widget type check.

## BrowseProvider

- `get_browse_provider` returns a module-level instance. The picker sets the skin's icon overrides on it before each browse.
- `list_directory` returns `None` when Kodi cannot list the path, an empty list for an empty folder, and `BrowseItem` objects otherwise. Fetching art is opt-in (`include_art`); without art, or when an entry has none, the icon is a default chosen by media type, then entry type, then MIME type.
- `normalize_image` unwraps Kodi's `image://` form. The content provider and the dialog's file browsing use it too.
