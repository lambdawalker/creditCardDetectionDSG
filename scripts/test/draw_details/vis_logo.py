import unittest

from PIL import Image

from scripts.color.generate_pallet import ColorPalette
from scripts.templates.generators.backgorund.draw_details import draw_solid_big_logo
from scripts.templates.generators.backgorund.generate_card_background import generate_card_background
from scripts.templates.render_template import render_template


def initialize_canvas_with_palette():
    width = 900
    height = 540
    palette = ColorPalette()
    return Image.new('RGBA', (width, height), (0, 0, 0, 0)), palette


class VisLogo(unittest.TestCase):
    def setUp(self):
        self.image, self.palette = initialize_canvas_with_palette()

    def tearDown(self):
        self.image.close()

    def test_solid_big_logo(self):
        draw_solid_big_logo(self.image, self.palette.get_primary_group(), self.palette.get_complementary_group())
        self.image.show()


class VisLogoFromIntegrated(unittest.TestCase):
    def setUp(self):
        self.palette = ColorPalette()

    def test_solid_big_logo_GCB(self):
        image = generate_card_background(
            self.palette,
            paint_order=[
                "draw_radial_gradient",
                "draw_parallel_lines", "draw_parallel_lines", "draw_parallel_lines",
                "draw_solid_big_logo"
            ]
        )

        image.show()

    def test_solid_big_logo_RT(self):
        palette = ColorPalette((212, 16, 30))

        image, data, card_log = render_template(
            side="front",
            palette=palette,
            paint_order=[
                "draw_radial_gradient",
                "draw_parallel_lines", "draw_parallel_lines", "draw_parallel_lines",
                "draw_solid_big_logo"
            ]
        )

        image.show()


if __name__ == "__main__":
    unittest.main()
