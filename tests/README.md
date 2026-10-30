# Tests

Unit tests for the parts of the add-on that run without Kodi: loaders, builders, conditions, expressions, the menu manager, and the management dialog's logic behind stubbed controls.

## Run

From the repo root, with Python 3.12 or newer and pytest installed:

```bash
python -m pytest tests/
```

`conftest.py` stubs the Kodi modules (`xbmc`, `xbmcaddon`, `xbmcgui`, `xbmcvfs`, `xbmcplugin`) and puts `resources/lib` on `sys.path`.

## Golden builds

`test_golden_skins.py` builds each skin in `fixtures/skins/` from its defaults and from its `userdata.json`, and compares the output to `fixtures/golden/` byte for byte. When a change is meant to alter the output, regenerate the golden files and review their diff:

```bash
SS_GOLDEN_REGEN=1 python -m pytest tests/test_golden_skins.py
```

`fixtures/seed.py` writes `userdata.json` for the fixture skins that have no real userdata and adds a custom widget per slot to silvo's. Custom widget menu ids are random: a rerun changes the golden output even when no code changed.

## Expected failures

A test marked `xfail(strict=True)` pins a known bug. Once a fix makes it pass, the run fails until the marker is removed.

## Fixture skins

The skins in `fixtures/skins/` keep their own licenses; [fixtures/skins/README.md](fixtures/skins/README.md) lists each one's authors, source and license.
