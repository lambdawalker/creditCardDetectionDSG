import unittest
import os.path
from scripts.color.generate_pallet import ColorPalette
from scripts.templates.render_template import render_template


class TestRenderTemplate(unittest.TestCase):

    def test_card_operation_opacity(self):
        palette = ColorPalette((212, 16, 30))

        image, data, card_log = render_template(
            side="front",
            palette=palette,
            paint_order=[
                "draw_radial_gradient",
                "draw_parallel_lines", "draw_parallel_lines", "draw_parallel_lines",
                "draw_dotted_border"
            ]
        )
        # Perform assertions here if you have expected outcomes, e.g.,
        self.assertIsNotNone(image)
        self.assertTrue(isinstance(data, list))
        # You can save the image and compare or just show it for manual inspection
        image.show()

    def test_draw_random_image_from_render_template(self):
        palette = ColorPalette()

        image, data, card_log = render_template(
            side="front",
            palette=palette,
            render_field=False,
            paint_order=[
                {
                    "name": "draw_random_image",
                    "parameters": {
                        "container_path": os.path.join(root, "assets/images/real_cards/post_validation_source")
                    }
                }
            ]
        )
        # Perform assertions here if you have expected outcomes, e.g.,
        self.assertIsNotNone(image)
        self.assertTrue(isinstance(data, dict))
        self.assertTrue(isinstance(card_log, list))
        # You can save the image and compare or just show it for manual inspection
        image.show()


if __name__ == "__main__":
    unittest.main()
