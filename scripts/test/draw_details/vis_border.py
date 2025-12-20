import unittest

from PIL import Image

from scripts.color.generate_pallet import ColorPalette
from scripts.templates.generators.backgorund.generate_card_background import generate_card_background
from scripts.templates.generators.backgorund.draw_border import (
    draw_dashed_border,
    draw_dotted_border,
    draw_solid_border,
)


def initialize_canvas_with_palette():
    width = 900
    height = 540
    palette = ColorPalette()
    return Image.new('RGBA', (width, height), (0, 0, 0, 0)), palette


class TestBorders(unittest.TestCase):
    def setUp(self):
        self.image, self.palette = initialize_canvas_with_palette()

    def tearDown(self):
        self.image.close()

    def test_draw_solid_border(self):
        draw_solid_border(self.image, self.palette.get_primary_group(), self.palette.get_complementary_group())
        self.image.show()

    def test_draw_dotted_border(self):
        draw_dotted_border(self.image, self.palette.get_primary_group(), self.palette.get_complementary_group())
        self.image.show()

    def test_draw_dashed_border(self):
        draw_dashed_border(self.image, self.palette.get_primary_group(), self.palette.get_complementary_group())
        self.image.show()


class TestBordersFromGenerateCardBackground(unittest.TestCase):
    def setUp(self):
        self.palette = ColorPalette()

    def test_draw_dashed_border(self):
        image = generate_card_background(
            self.palette,
            paint_order=[
                "draw_radial_gradient",
                "draw_parallel_lines", "draw_parallel_lines", "draw_parallel_lines",
                "draw_dashed_border"
            ]
        )

        image.show()

    def test_draw_solid_border(self):
        image = generate_card_background(
            self.palette,
            paint_order=[
                "draw_radial_gradient",
                "draw_parallel_lines", "draw_parallel_lines", "draw_parallel_lines",
                "draw_solid_border"
            ]
        )

        image.show()

    def test_draw_solid_white_border(self):
        image = generate_card_background(
            self.palette,
            paint_order=[
                "draw_radial_gradient",
                "draw_parallel_lines", "draw_parallel_lines", "draw_parallel_lines",
                "draw_solid_white_border"
            ]
        )

        image.show()


if __name__ == "__main__":
    unittest.main()
