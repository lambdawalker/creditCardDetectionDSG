from PIL import Image

from scripts.color.ColorPallet import ColorPalette
from scripts.generators.backgorund.draw_ordered_triangles import draw_ordered_triangles
from scripts.generators.backgorund.generate_base import ordered_triangles
from scripts.generators.backgorund.generate_random_contrasting_background import generate_random_contrasting_background


def test_draw_ordered_triangles_contrasting():
    image = Image.new('RGBA', (800, 600), (255, 255, 255))

    triangle_width = 153
    triangle_height = 34
    primary_colors = [(203, 22, 246), (237, 22, 246), (169, 22, 246)]
    complementary_colors = [(65, 246, 22), (31, 246, 22), (99, 246, 22)]

    draw_ordered_triangles(image, triangle_width, triangle_height, primary_colors, complementary_colors)

    image.show()


def test_ordered_triangles_contrasting():
    palette = ColorPalette()
    image = ordered_triangles(palette.get_primary_group(), palette.get_complementary_group(), 800, 600)
    image.show()


def test_force_ordered_triangles():
    pallet = ColorPalette()
    image = generate_random_contrasting_background(800, 600, pallet, force_type="ordered_triangles")

    image.show()


def test_generate_random_contrasting_background():
    pallet = ColorPalette()
    image = generate_random_contrasting_background(800, 600, pallet)

    image.show()
    # visualize_palette(pallet)
