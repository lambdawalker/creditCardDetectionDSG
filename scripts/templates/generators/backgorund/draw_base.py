import random

from PIL import ImageDraw, Image

from scripts.color.generate_color import generate_random_shade_color
from scripts.common.file import get_random_file
from scripts.templates.generators.backgorund.draw_ordered_triangles import draw_ordered_triangles as draw_ordered_triangle_


def draw_linear_gradient(image, primary_colors, complementary_colors, **parameters):
    width, height = image.size

    primary_color = random.choice(primary_colors)
    complementary_color = random.choice(complementary_colors)

    start_color = generate_random_shade_color(primary_color)
    end_color = generate_random_shade_color(complementary_color)

    draw = ImageDraw.Draw(image)

    for i in range(height):
        blend = i / height
        r = int(start_color[0] * (1 - blend) + end_color[0] * blend)
        g = int(start_color[1] * (1 - blend) + end_color[1] * blend)
        b = int(start_color[2] * (1 - blend) + end_color[2] * blend)
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    return image


def draw_radial_gradient(image, primary_colors, complementary_colors, **parameters):
    width, height = image.size

    primary_color = random.choice(primary_colors)
    complementary_color = random.choice(complementary_colors)

    center_color = generate_random_shade_color(primary_color)
    edge_color = generate_random_shade_color(complementary_color)
    draw = ImageDraw.Draw(image)

    # Random center point
    cx, cy = random.randint(0, width), random.randint(0, height)

    # Maximum distance from the center to a corner
    max_radius = max(
        ((cx - 0) ** 2 + (cy - 0) ** 2) ** 0.5,
        ((cx - width) ** 2 + (cy - 0) ** 2) ** 0.5,
        ((cx - 0) ** 2 + (cy - height) ** 2) ** 0.5,
        ((cx - width) ** 2 + (cy - height) ** 2) ** 0.5,
    )

    for r in range(int(max_radius), 0, -1):
        blend = r / max_radius
        r_color = int(center_color[0] * blend + edge_color[0] * (1 - blend))
        g_color = int(center_color[1] * blend + edge_color[1] * (1 - blend))
        b_color = int(center_color[2] * blend + edge_color[2] * (1 - blend))
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=(r_color, g_color, b_color))

    return image


def draw_solid_color(image, primary_colors, complementary_colors, **parameters):
    width, height = image.size

    primary_color = random.choice(primary_colors)
    color = generate_random_shade_color(primary_color)
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, width, height], fill=color)

    return image


def draw_ordered_triangles(image, primary_colors, complementary_colors, **parameters):
    width, height = image.size

    triangle_width = random.randint(int(width * .025), int(width * .1))
    triangle_height = random.randint(int(width * .025), int(width * .1))

    draw_ordered_triangle_(image, triangle_width, triangle_height, primary_colors, complementary_colors)

    return image


def draw_random_image(image, primary_colors, complementary_colors, container_path=None, **parameters):
    file = get_random_file(container_path)
    img = Image.open(file).resize(image.size).convert("RGBA")
    image.paste(img, (0, 0), img)


draw_fill_background_functions = {
    'draw_linear_gradient': draw_linear_gradient,
    'draw_radial_gradient': draw_radial_gradient,
    'draw_solid_color': draw_solid_color,
    'draw_ordered_triangles': draw_ordered_triangles,
}

draw_fill_background_functions_all = {
    'draw_linear_gradient': draw_linear_gradient,
    'draw_radial_gradient': draw_radial_gradient,
    'draw_solid_color': draw_solid_color,
    'draw_ordered_triangles': draw_ordered_triangles,

    'draw_random_image': draw_random_image
}
