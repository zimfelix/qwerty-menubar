"""Platform-independent sizing and resource lookup."""

from pathlib import Path

IMAGE_WIDTH = 1000
IMAGE_HEIGHT = 444
PADDING = 14
PREFERRED_WIDTH = 780


def popover_size(screen_width: float) -> tuple[int, int]:
    """Keep the reference within the screen without changing its aspect ratio."""
    available = max(1, int(screen_width) - 48)
    width = min(PREFERRED_WIDTH, available)
    image_width = max(1, width - 2 * PADDING)
    height = round(image_width * IMAGE_HEIGHT / IMAGE_WIDTH) + 2 * PADDING
    return width, height


def asset_path(name: str, bundle_resources: str | None = None) -> Path:
    """Support both a standalone .app and a source checkout; fail clearly."""
    if Path(name).name != name:
        raise ValueError("Asset names must not contain directory components")
    roots = [Path(__file__).parent / "assets"]
    if bundle_resources:
        roots.insert(0, Path(bundle_resources) / "assets")
    for root in roots:
        candidate = root / name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"Missing app asset: {name}")
