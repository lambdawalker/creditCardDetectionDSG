import unittest

from scripts.color.generate_pallet import ColorPalette
from scripts.templates.generators.backgorund.generate_card_background import generate_card_background


class TestBordersFromGenerateCardBackground(unittest.TestCase):
    def setUp(self):
        self.palette = ColorPalette()

    def test_draw_solid_white_border(self):
        image = generate_card_background(
            self.palette
        )

        image.show()


if __name__ == "__main__":
    unittest.main()
