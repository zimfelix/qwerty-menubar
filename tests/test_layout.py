from pathlib import Path

import pytest

from qwerty_menubar.layout import PADDING, asset_path, popover_size


@pytest.mark.parametrize("screen_width", [320, 640, 1024, 1440, 2560, 5120])
def test_popover_fits_screen_and_keeps_ratio(screen_width):
    width, height = popover_size(screen_width)
    assert width <= min(780, screen_width - 48)
    assert abs((height - 2 * PADDING) / (width - 2 * PADDING) - 444 / 1000) < 0.003


def test_small_or_invalid_screen_never_produces_negative_size():
    assert all(value > 0 for value in popover_size(0))


def test_source_asset_exists():
    assert asset_path("keyboard.png").is_file()


def test_bundle_asset_takes_precedence(tmp_path):
    folder = tmp_path / "assets"
    folder.mkdir()
    (folder / "keyboard.png").write_bytes(b"bundle asset")
    assert asset_path("keyboard.png", str(tmp_path)) == folder / "keyboard.png"


def test_missing_bundle_asset_falls_back_to_source(tmp_path):
    assert asset_path("keyboard.png", str(tmp_path)).parent == Path(__file__).parents[1] / (
        "qwerty_menubar/assets"
    )


def test_missing_asset_fails_clearly():
    with pytest.raises(FileNotFoundError, match="Missing app asset"):
        asset_path("does-not-exist.png")


@pytest.mark.parametrize("name", ["../keyboard.png", "assets/keyboard.png", "/tmp/keyboard.png"])
def test_path_traversal_is_rejected(name):
    with pytest.raises(ValueError):
        asset_path(name)
