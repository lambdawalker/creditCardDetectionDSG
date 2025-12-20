import os.path

from scripts.color.ColorPallet import ColorPalette
from scripts.templates.render_template import render_template


def test_card_operation_opacity():
    root = "../../"
    palette = ColorPalette((212, 16, 30))
    image, data, card_log = render_template(
        root_path=root,
        side="front",
        palette=palette,
        paint_order=[
            "draw_radial_gradient",
            "draw_parallel_lines", "draw_parallel_lines", "draw_parallel_lines"
        ]
    )
    image.show()


def test_draw_random_image_from_render_template():
    root = os.path.abspath("../../")
    palette = ColorPalette()

    image, data, card_log = render_template(
        root_path=root,
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
    image.show()
