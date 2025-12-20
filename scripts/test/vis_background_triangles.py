from PIL import Image

from scripts.color.ColorPallet import ColorPalette
from scripts.generators.backgorund.draw_ordered_triangles import draw_ordered_triangles

if __name__ == "__main__":
    # Example usage:
    area_width = 400
    area_height = 400
    triangle_width = 50
    triangle_height = 50

    image = Image.new("RGB", (area_width, area_height), (0, 0, 0))

    palette = ColorPalette()

    # primary_colors = palette['analogous'] + [palette['primary']]
    # complementary_colors = [palette['complementary']] + palette['triadic']

    # primary_colors = [palette['primary']]
    # complementary_colors = [palette['complementary']]

    primary_colors = palette['analogous']
    complementary_colors = [palette['primary']]

    draw_ordered_triangles(
        image,
        triangle_width,
        triangle_height,
        primary_colors,
        complementary_colors
    )

    image.show()
