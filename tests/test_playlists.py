"""Smart playlist generation for source shortcuts."""

from __future__ import annotations

import json as _json
import xml.etree.ElementTree as ET

import xbmc
import xbmcvfs

from skinshortcuts.playlists import (
    DEFAULT_PLAYLISTS_PATH,
    DOMAIN_VIEWS,
    FILES_VIEW,
    build_smartplaylist_xml,
    detect_domain,
    display_options,
    path_has_content,
    playlist_filename,
    playlists_base_path,
    save_playlist,
    unpack_multipath,
)


def test_unpack_plain_path():
    assert unpack_multipath("D:\\HD Movies\\") == ["D:\\HD Movies\\"]


def test_unpack_multipath():
    raw = "multipath://B%3a%5cMy%20TV%20Shows%5c/B%3a%5cKids%20TV%5c/"
    assert unpack_multipath(raw) == ["B:\\My TV Shows\\", "B:\\Kids TV\\"]


def test_include_single_path():
    xml = build_smartplaylist_xml("movies", "Movies (D)", ["D:\\HD Movies\\"])
    root = ET.fromstring(xml)
    assert root.tag == "smartplaylist"
    assert root.get("type") == "movies"
    assert root.findtext("match") == "one"
    rules = root.findall("rule")
    assert len(rules) == 1
    assert rules[0].get("operator") == "startswith"
    assert rules[0].findtext("value") == "D:\\HD Movies\\"


def test_exclude_uses_doesnotcontain_and_match_all():
    xml = build_smartplaylist_xml("movies", "Not D", ["D:\\HD Movies\\"], exclude=True)
    root = ET.fromstring(xml)
    assert root.findtext("match") == "all"
    assert root.find("rule").get("operator") == "doesnotcontain"


def test_multipath_emits_one_rule_per_path():
    xml = build_smartplaylist_xml(
        "tvshows", "TV (B)", ["B:\\My TV Shows\\", "B:\\Kids TV\\"]
    )
    root = ET.fromstring(xml)
    values = [r.findtext("value") for r in root.findall("rule")]
    assert values == ["B:\\My TV Shows\\", "B:\\Kids TV\\"]


def test_no_group_element():
    # grouping is left to Kodi's "group movies into sets" setting
    xml = build_smartplaylist_xml("movies", "Movies", ["D:\\HD Movies\\"])
    assert "<group>" not in xml


def test_sort_random():
    xml = build_smartplaylist_xml("songs", "Songs", ["D:\\Music\\"], sort_field="random")
    root = ET.fromstring(xml)
    order = root.find("order")
    assert order.text == "random"
    assert order.get("direction") is None


def test_sort_field_with_direction():
    xml = build_smartplaylist_xml(
        "movies", "Movies", ["D:\\HD Movies\\"], sort_field="year", sort_order="descending"
    )
    order = ET.fromstring(xml).find("order")
    assert order.text == "year"
    assert order.get("direction") == "descending"


def test_no_order_when_unset():
    xml = build_smartplaylist_xml("movies", "Movies", ["D:\\HD Movies\\"])
    assert ET.fromstring(xml).find("order") is None


def test_name_is_escaped():
    xml = build_smartplaylist_xml("movies", "Tom & Jerry", ["D:\\x\\"])
    assert "Tom &amp; Jerry" in xml
    assert ET.fromstring(xml).findtext("name") == "Tom & Jerry"


def test_playlist_filename_sanitises():
    assert playlist_filename("mainmenu", "movies") == "source-mainmenu-movies.xsp"
    assert playlist_filename("main menu", "my/item") == "source-main_menu-my_item.xsp"


def test_save_playlist_writes_file_and_returns_special_path():
    xml = build_smartplaylist_xml("movies", "X", ["D:\\x\\"])
    path = save_playlist("mainmenu", "movies", xml)
    # namespaced per skin, conftest stubs getSkinDir as "test.skin"
    assert path == (
        "special://profile/addon_data/script.skinshortcuts/playlists/test.skin/"
        "source-mainmenu-movies.xsp"
    )
    with open(xbmcvfs.translatePath(path), encoding="utf-8") as f:
        assert f.read() == xml


def _fake_jsonrpc(totals: dict[str, int]):
    """Stand-in executeJSONRPC reporting the summed row counts of the filtered paths."""

    def _call(request_str: str) -> str:
        flt = _json.loads(request_str)["params"]["filter"]
        rules = flt["and"] if "and" in flt else [flt]
        total = sum(totals.get(r["value"], 0) for r in rules)
        return _json.dumps({"result": {"limits": {"total": total}}})

    return _call


def test_probe_include_true_when_path_has_rows(monkeypatch):
    monkeypatch.setattr(
        xbmc, "executeJSONRPC", _fake_jsonrpc({"D:\\HD Movies\\": 407}), raising=False
    )
    assert path_has_content("movies", ["D:\\HD Movies\\"]) is True
    assert path_has_content("movies", ["D:\\Empty\\"]) is False


def test_probe_include_multipath_any_path(monkeypatch):
    monkeypatch.setattr(xbmc, "executeJSONRPC", _fake_jsonrpc({"B:\\Kids TV\\": 7}), raising=False)
    assert path_has_content("tvshows", ["B:\\My TV Shows\\", "B:\\Kids TV\\"]) is True


def test_probe_exclude_uses_total(monkeypatch):
    monkeypatch.setattr(
        xbmc, "executeJSONRPC", _fake_jsonrpc({"D:\\HD Movies\\": 3983}), raising=False
    )
    assert path_has_content("movies", ["D:\\HD Movies\\"], exclude=True) is True


def test_probe_unknown_type_is_false():
    assert path_has_content("bogus", ["D:\\x\\"]) is False


def _fake_jsonrpc_by_method(method_totals: dict[str, int]):
    """Stand-in executeJSONRPC answering each method with its total."""

    def _call(request_str: str) -> str:
        method = _json.loads(request_str)["method"]
        return _json.dumps({"result": {"limits": {"total": method_totals.get(method, 0)}}})

    return _call


def test_detect_domain_video_single_type(monkeypatch):
    monkeypatch.setattr(
        xbmc, "executeJSONRPC", _fake_jsonrpc_by_method({"VideoLibrary.GetTVShows": 5}),
        raising=False,
    )
    assert detect_domain("video", ["B:\\TV\\"]) == "tvshows"


def test_detect_domain_music(monkeypatch):
    monkeypatch.setattr(
        xbmc, "executeJSONRPC", _fake_jsonrpc_by_method({"AudioLibrary.GetSongs": 99}),
        raising=False,
    )
    assert detect_domain("music", ["D:\\Music\\"]) == "music"


def test_detect_domain_none_when_unscanned(monkeypatch):
    monkeypatch.setattr(xbmc, "executeJSONRPC", _fake_jsonrpc_by_method({}), raising=False)
    assert detect_domain("video", ["D:\\NotScanned\\"]) is None


def test_display_options_prunes_to_domain(monkeypatch):
    monkeypatch.setattr(
        xbmc, "executeJSONRPC", _fake_jsonrpc_by_method({"VideoLibrary.GetMovies": 407}),
        raising=False,
    )
    opts = display_options("video", ["D:\\HD Movies\\"])
    assert opts == [FILES_VIEW, *DOMAIN_VIEWS["movies"]]
    assert [o.media_type for o in opts] == ["", "movies", "movies"]


def test_display_options_files_only_when_not_library(monkeypatch):
    monkeypatch.setattr(xbmc, "executeJSONRPC", _fake_jsonrpc_by_method({}), raising=False)
    assert display_options("video", ["D:\\NotScanned\\"]) == [FILES_VIEW]


def _fake_setting(value):
    """Stand-in executeJSONRPC returning a setting value, or no result for None."""

    def _call(_request_str: str) -> str:
        return _json.dumps({"result": {"value": value}} if value is not None else {})

    return _call


def test_base_path_uses_configured_value(monkeypatch):
    monkeypatch.setattr(
        xbmc, "executeJSONRPC", _fake_setting("special://profile/lists/"), raising=False
    )
    assert playlists_base_path() == "special://profile/lists/"


def test_base_path_appends_trailing_slash(monkeypatch):
    monkeypatch.setattr(xbmc, "executeJSONRPC", _fake_setting("D:\\Lists"), raising=False)
    assert playlists_base_path() == "D:\\Lists/"


def test_base_path_falls_back_when_unset(monkeypatch):
    monkeypatch.setattr(xbmc, "executeJSONRPC", _fake_setting(""), raising=False)
    assert playlists_base_path() == DEFAULT_PLAYLISTS_PATH
    monkeypatch.setattr(xbmc, "executeJSONRPC", _fake_setting(None), raising=False)
    assert playlists_base_path() == DEFAULT_PLAYLISTS_PATH


def test_base_path_falls_back_on_malformed_response(monkeypatch):
    monkeypatch.setattr(xbmc, "executeJSONRPC", lambda _req: "not json", raising=False)
    assert playlists_base_path() == DEFAULT_PLAYLISTS_PATH


def test_cleanup_removes_unreferenced_keeps_referenced():
    import os

    from skinshortcuts.playlists import cleanup_orphan_playlists

    keep = save_playlist("clmenu", "keepitem", "<x/>")
    drop = save_playlist("clmenu", "dropitem", "<y/>")
    cleanup_orphan_playlists([f"ActivateWindow(Videos,{keep},return)"])
    assert os.path.exists(xbmcvfs.translatePath(keep))
    assert not os.path.exists(xbmcvfs.translatePath(drop))
