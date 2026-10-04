from PIL import Image

from qwerty_menubar.layout import asset_path
from tools.prepare_image import clean_edges, is_background, remove_background


def test_border_white_is_removed_but_key_legends_are_preserved():
    image = Image.new("RGB", (7, 7), "white")
    for x in range(1, 6):
        for y in range(1, 6):
            image.putpixel((x, y), (50, 50, 50))
    image.putpixel((3, 3), (255, 255, 255))  # a white key legend enclosed by a dark key
    result = remove_background(image)
    assert result.getpixel((0, 0))[3] == 0
    assert result.getpixel((1, 1)) == (50, 50, 50, 255)
    assert result.getpixel((3, 3)) == (255, 255, 255, 255)
    assert image.mode == "RGB"  # does not mutate the source


def test_colored_pixels_are_not_classified_as_white():
    assert not is_background((255, 220, 220))
    assert not is_background((210, 210, 210))
    assert is_background((248, 250, 249))


def test_packaged_photo_is_transparent_only_outside_keyboard():
    with Image.open(asset_path("keyboard.png")) as image:
        assert image.mode == "RGBA"
        assert image.size == (1000, 444)
        assert image.getpixel((0, 0))[3] == 0
        assert image.getpixel((999, 443))[3] == 0
        assert image.getpixel((500, 200))[3] == 255
        transparent = sum(alpha == 0 for alpha in image.getchannel("A").get_flattened_data())
        assert 1000 < transparent < image.width * image.height * 0.15


def test_edge_cleanup_preserves_interior_legends_and_softens_outline():
    image = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
    for x in range(2, 22):
        for y in range(2, 22):
            image.putpixel((x, y), (60, 60, 60, 255))
    image.putpixel((12, 12), (255, 255, 255, 255))
    cleaned = clean_edges(image)
    assert cleaned.getpixel((0, 0))[3] == 0
    assert cleaned.getpixel((12, 12)) == (255, 255, 255, 255)
    assert any(0 < value < 255 for value in cleaned.getchannel("A").get_flattened_data())


def test_status_icon_has_alpha_and_retina_resolution():
    with Image.open(asset_path("keyboard-status.png")) as image:
        assert image.mode == "RGBA"
        assert image.width >= 64
        assert image.getchannel("A").getextrema() == (0, 255)
