"""Offline asset preparation. Pillow is not imported by the running app."""

import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw


def is_background(pixel: tuple[int, ...]) -> bool:
    """Only near-white/neutral pixels; pale legends must not be globally erased."""
    red, green, blue = pixel[:3]
    return min(red, green, blue) >= 220 and max(red, green, blue) - min(red, green, blue) <= 18


def remove_background(image: Image.Image) -> Image.Image:
    """Flood-fill white pixels connected to the border, keeping interior legends."""
    result = image.convert("RGBA")
    width, height = result.size
    pixels = result.load()
    queue = deque((x, y) for x in range(width) for y in (0, height - 1))
    queue.extend((x, y) for y in range(height) for x in (0, width - 1))
    visited = set()
    while queue:
        x, y = queue.popleft()
        if (x, y) in visited or not (0 <= x < width and 0 <= y < height):
            continue
        visited.add((x, y))
        if not is_background(pixels[x, y]):
            continue
        pixels[x, y] = (0, 0, 0, 0)
        queue.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))
    return result


def keyboard_symbol(size: int, color: tuple[int, ...]) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    scale = size / 128

    def box(coords):
        return tuple(round(value * scale) for value in coords)

    draw.rounded_rectangle(
        box((5, 25, 123, 103)),
        radius=round(11 * scale),
        outline=color,
        width=max(1, round(6 * scale)),
    )
    for row in range(3):
        for column in range(8):
            x, y = 17 + column * 12, 38 + row * 15
            draw.rounded_rectangle(
                box((x, y, x + 7, y + 7)), radius=max(1, round(scale)), fill=color
            )
    draw.rounded_rectangle(box((40, 83, 88, 90)), radius=round(2 * scale), fill=color)
    return image


def create_icons(destination: Path):
    symbol = keyboard_symbol(256, (0, 0, 0, 255))
    symbol.crop((0, 40, 256, 224)).save(destination / "keyboard-status.png", optimize=True)
    icon = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    draw.rounded_rectangle((48, 48, 976, 976), radius=215, fill=(40, 53, 73, 255))
    symbol = keyboard_symbol(800, (226, 236, 249, 255))
    icon.alpha_composite(symbol, (112, 112))
    icon.save(destination / "app-icon.icns")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("qwerty_menubar/assets"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with Image.open(args.source) as source:
        cleaned = remove_background(source)
    cleaned.save(args.output / "keyboard.png", optimize=True)
    create_icons(args.output)
    print(f"Prepared {cleaned.width} × {cleaned.height} transparent image in {args.output}")


if __name__ == "__main__":
    main()
