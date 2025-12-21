from PIL import Image

from scripts.templates.generators.backgorund.draw_ordered_triangles import draw_ordered_triangles


def test_draw_ordered_triangles_contrasting():
    image = Image.new('RGBA', (800, 600), (255, 255, 255))

    triangle_width = 153
    triangle_height = 34
    primary_colors = [(203, 22, 246), (237, 22, 246), (169, 22, 246)]
    complementary_colors = [(65, 246, 22), (31, 246, 22), (99, 246, 22)]

    draw_ordered_triangles(image, triangle_width, triangle_height, primary_colors, complementary_colors)

    image.show()
