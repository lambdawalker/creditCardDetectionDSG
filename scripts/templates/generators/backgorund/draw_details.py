import math
import random

import numpy as np
from PIL import ImageDraw, Image

from scripts.color.generate_color import generate_random_shade_color
from scripts.common.file import path_from_root, get_random_file
from scripts.common.svg_stencil import prepare_svg_as_stencil, apply_stencil
from scripts.templates.generators.backgorund.common import get_width_dependent_param


def draw_curved_lines(image, primary_colors, complementary_colors, **parameters):
    color = random.choice(primary_colors)
    color = (*color, parameters.get("opacity", 255))

    width, height = image.size
    transparent_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer, "RGBA")

    def random_thickness():
        return random.randint(height // 60, height // 5)

    def bezier_curve(p0, p1, p2, p3, t):
        return (
                (1 - t) ** 3 * np.array(p0)
                + 3 * (1 - t) ** 2 * t * np.array(p1)
                + 3 * (1 - t) * t ** 2 * np.array(p2)
                + t ** 3 * np.array(p3)
        )

    def random_curve_points():
        return [
            (0, random.randint(0, height)),
            (random.randint(0, width), random.randint(0, height)),
            (random.randint(0, width), random.randint(0, height)),
            (width, random.randint(0, height)),
        ]

    num_lines = random.randint(0, 30)
    thickness = random_thickness()

    for _ in range(num_lines):
        points = random_curve_points()
        curve_points = [
            bezier_curve(points[0], points[1], points[2], points[3], t)
            for t in np.linspace(0, 1, 1000)
        ]
        curve_points = [(int(x), int(y)) for x, y in curve_points]

        draw.line(curve_points, fill=color, width=thickness)

    image.paste(transparent_layer, (0, 0), transparent_layer)
    return image


def draw_random_rectangles(image, primary_colors, complementary_colors, **parameters):
    color = random.choice(primary_colors)
    color = (*color, parameters.get("opacity", 255))

    width, height = image.size
    transparent_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer, "RGBA")

    def random_thickness():
        return random.randint(height // 60, height // 5)

    def random_line_points():
        return [
            (random.randint(0, width), random.randint(0, height)),
            (random.randint(0, width), random.randint(0, height)),
        ]

    num_lines = random.randint(5, 15)

    for _ in range(num_lines):
        thickness = random_thickness()
        points = random_line_points()
        draw.line(points, fill=color, width=thickness)

    image.paste(transparent_layer, (0, 0), transparent_layer)
    return image


def draw_random_spots(image, primary_colors, complementary_colors, **parameters):
    color = random.choice(primary_colors)
    color = (*color, parameters.get("opacity", 255))

    width, height = image.size
    transparent_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer, "RGBA")

    def random_spot_size():
        return random.randint(height // 30, height // 10)

    num_spots = random.randint(10, 100)

    for _ in range(num_spots):
        spot_size = random_spot_size()
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.ellipse(
            [(x - spot_size, y - spot_size), (x + spot_size, y + spot_size)],
            fill=color,
        )

    image.paste(transparent_layer, (0, 0), transparent_layer)
    return image


def draw_random_triangles(image, primary_colors, complementary_colors, **parameters):
    color = random.choice(primary_colors)
    color = (*color, parameters.get("opacity", 255))

    width, height = image.size
    transparent_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer, 'RGBA')

    def random_triangle_points():
        return [
            (random.randint(0, width), random.randint(0, height)),
            (random.randint(0, width), random.randint(0, height)),
            (random.randint(0, width), random.randint(0, height))
        ]

    num_triangles = random.randint(2, 15)

    for _ in range(num_triangles):
        points = random_triangle_points()
        draw.polygon(points, fill=color)

    # otherwise the transparency don't work
    image.paste(transparent_layer, (0, 0), transparent_layer)
    return image


def draw_parallel_lines(image, primary_colors, complementary_colors, angle=None, thickness=None, spacing=None, opacity=255, **_):
    color = random.choice(primary_colors)
    color = (*color, opacity)

    width, height = image.size
    transparent_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer, 'RGBA')

    angle = angle if angle is not None else random.uniform(0, math.pi)
    thickness = thickness if thickness is not None else random.randint(height // 40, height // 30)
    spacing = spacing if spacing is not None else 2 * thickness

    print(f"angle: {angle}, thickness: {thickness}, spacing: {spacing} <<")

    for i in range(-height, width + height, spacing):
        x1 = i
        y1 = 0
        x2 = i + height * math.tan(angle)
        y2 = height
        draw.line([(x1, y1), (x2, y2)], fill=color, width=thickness)

    image.paste(transparent_layer, (0, 0), transparent_layer)
    return image


def draw_solid_big_logo(image, primary_colors, complementary_colors, **parameters):
    color = random.choice(complementary_colors)
    image_b = Image.new("RGBA", image.size, color)

    stencils_path = path_from_root("./assets/images/logo_stencil")
    svg_path = get_random_file(stencils_path)

    width, height = image.size
    stencil, bounding_box = prepare_svg_as_stencil(svg_path, width, height)

    if stencil is not None:
        result_image = apply_stencil(image, image_b, stencil)
        return result_image
    else:
        raise ValueError(f"Failed to apply stencil. {svg_path}")


def draw_random_circles(image, primary_colors, complementary_colors, **parameters):
    color = random.choice(primary_colors)
    color = generate_random_shade_color(color, .10)
    color = (*color, parameters.get("opacity", 255))

    width, height = image.size
    transparent_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer, "RGBA")

    def random_spot_size():
        return random.randint(height // 30, height // 10)

    num_spots = random.randint(10, 100)

    thickness = get_width_dependent_param(image, 0.8, 3, 'thickness', **parameters)

    for _ in range(num_spots):
        spot_size = random_spot_size()
        x = random.randint(0, width)
        y = random.randint(0, height)
        draw.ellipse(
            [(x - spot_size, y - spot_size), (x + spot_size, y + spot_size)],
            fill=None,
            outline=color,
            width=thickness
        )

    image.paste(transparent_layer, (0, 0), transparent_layer)
    return image


def draw_grid_dots(image, primary_colors, complementary_colors, **parameters):
    color = random.choice(primary_colors)
    color = generate_random_shade_color(color, .10)
    color = (*color, parameters.get("opacity", 255))

    width, height = image.size
    transparent_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer, "RGBA")

    def random_dot_size():
        return random.randint(height // 80, height // 30)

    def random_spacing():
        return random.randint(height // 20, height // 8)

    dot_size = random_dot_size()
    spacing = random_spacing()

    for x in range(0, width + spacing, spacing):
        for y in range(0, height + spacing, spacing):
            draw.ellipse(
                [(x - dot_size, y - dot_size), (x + dot_size, y + dot_size)],
                fill=color,
            )

    image.paste(transparent_layer, (0, 0), transparent_layer)
    return image


draw_details_functions = {
    'draw_random_rectangles': draw_random_rectangles,
    'draw_curved_lines': draw_curved_lines,
    'draw_random_spots': draw_random_spots,
    'draw_random_triangles': draw_random_triangles,
    'draw_parallel_lines': draw_parallel_lines,
    'draw_solid_big_logo': draw_solid_big_logo,
    'draw_random_circles': draw_random_circles,
    'draw_grid_dots': draw_grid_dots,
}
