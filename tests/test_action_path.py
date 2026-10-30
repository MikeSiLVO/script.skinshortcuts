"""The path property is the bare content path, split from the action."""

from __future__ import annotations

import pytest

from skinshortcuts.constants import extract_path_from_action, extract_window_from_action


@pytest.mark.parametrize(
    ("action", "path"),
    [
        ("ActivateWindow(Videos,videodb://movies/titles/,return)", "videodb://movies/titles/"),
        ("PlayMedia(special://profile/playlists/video/a.xsp)", "special://profile/playlists/video/a.xsp"),
        ("RunAddon(plugin.video.youtube)", "plugin://plugin.video.youtube/"),
        ("Skin.ToggleSetting(x)", "Skin.ToggleSetting(x)"),
    ],
)
def test_plain_actions(action: str, path: str) -> None:
    assert extract_path_from_action(action) == path


@pytest.mark.parametrize(
    ("action", "path"),
    [
        ('PlayMedia("special://profile/playlists/video/a.xsp",resume)', "special://profile/playlists/video/a.xsp"),
        ("PlayMedia(special://profile/playlists/video/a.xsp,resume)", "special://profile/playlists/video/a.xsp"),
        ('ActivateWindow(Videos,"library://video/movies/",return)', "library://video/movies/"),
        ('ActivateWindow(Videos,"smb://nas/Films, HD/",return)', "smb://nas/Films, HD/"),
    ],
)
def test_quoted_and_trailing_argument_actions(action: str, path: str) -> None:
    assert extract_path_from_action(action) == path


def test_window_of_a_plain_action() -> None:
    assert extract_window_from_action("ActivateWindow(Videos,videodb://movies/titles/)") == "Videos"


def test_split_params_matches_the_kodi_port() -> None:
    import random

    from test_skinstring_picker import split_params as kodi_port

    from skinshortcuts.constants import split_params

    rng = random.Random(7)
    samples = [
        "".join(rng.choice('ab ,"\\()=') for _ in range(rng.randint(0, 14))) for _ in range(5000)
    ]
    assert [split_params(s) for s in samples] == [kodi_port(s) for s in samples]


def test_empty_calls_give_no_path_or_window() -> None:
    assert extract_window_from_action("ActivateWindow()") == ""
    assert extract_path_from_action("PlayMedia()") == ""
