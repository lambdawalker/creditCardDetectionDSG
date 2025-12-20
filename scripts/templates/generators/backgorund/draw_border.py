import random

from PIL import Image, ImageDraw

from scripts.templates.generators.backgorund.common import get_width_dependent_param

white = (255, 255, 255)
black = (0, 0, 0)


def draw_solid_border(image, primary_colors, complementary_colors, **parameters):
    # Choose a color for the border
    color = random.choice((*primary_colors, *complementary_colors, white, black))

    # Get the image dimensions
    width, height = image.size

    # Create a transparent layer to draw the border on
    transparent_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer, 'RGBA')

    # Safeguard against missing parameters
    border_thickness = get_width_dependent_param(image, .05, 1.8, 'border_thickness', **parameters)
    padding = get_width_dependent_param(image, 0.5, 3, 'padding', **parameters)

    # Calculate the coordinates for the inner rectangle (border)
    left = padding
    top = padding
    right = width - padding
    bottom = height - padding

    # Draw the inner border
    draw.rectangle(
        [left, top, right, bottom],
        outline=color,
        width=border_thickness
    )

    # Paste the transparent layer onto the original image
    image.paste(transparent_layer, (0, 0), transparent_layer)
    return image


def draw_solid_white_border(image, primary_colors, complementary_colors, **parameters):
    # Choose a color for the border
    color = white

    # Get the image dimensions
    width, height = image.size

    # Create a transparent layer to draw the border on
    transparent_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer, 'RGBA')

    # Safeguard against missing parameters
    border_thickness = get_width_dependent_param(image, .05, 1.8, 'border_thickness', **parameters)

    # Calculate the coordinates for the inner rectangle (border)
    left = 0
    top = 0
    right = width
    bottom = height

    # Draw the inner border
    draw.rectangle(
        [left, top, right, bottom],
        outline=color,
        width=border_thickness
    )

    # Paste the transparent layer onto the original image
    image.paste(transparent_layer, (0, 0), transparent_layer)
    return image


def draw_dotted_border(image, primary_colors, complementary_colors, **parameters):
    color = random.choice((*primary_colors, *complementary_colors, white, black))

    width, height = image.size

    transparent_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer, 'RGBA')

    # Safeguard against missing parameters
    border_thickness = get_width_dependent_param(image, 1, 3, 'border_thickness', **parameters)
    padding = get_width_dependent_param(image, 0.8, 3, 'padding', **parameters)
    dot_size = get_width_dependent_param(image, 0.5, 2, 'dot_size', **parameters)
    spacing = get_width_dependent_param(image, 0.5, 1, 'spacing', **parameters)

    # Calculate the coordinates for the inner rectangle (dotted border)
    left = padding
    top = padding
    right = width - padding
    bottom = height - padding

    for x in range(left, right, dot_size + spacing):
        if x + dot_size > right:
            x = right - dot_size

        draw.ellipse([(x, top), (x + dot_size, top + dot_size)], fill=color)
        draw.ellipse([(x, bottom - dot_size), (x + dot_size, bottom)], fill=color)

    # Draw the left and right dotted border
    for y in range(top, bottom, dot_size + spacing):
        if y + dot_size > bottom:
            y = bottom - dot_size

        draw.ellipse([(left, y), (left + dot_size, y + dot_size)], fill=color)
        draw.ellipse([(right - dot_size, y), (right, y + dot_size)], fill=color)

    # Paste the transparent layer onto the original image
    image.paste(transparent_layer, (0, 0), transparent_layer)
    return image


def draw_dashed_border(image, primary_colors, complementary_colors, **parameters):
    # Choose a color for the border
    color = random.choice((*primary_colors, *complementary_colors, white, black))

    # Get the image dimensions
    width, height = image.size

    # Create a transparent layer to draw the border on
    transparent_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(transparent_layer, 'RGBA')

    # Safeguard against missing parameters
    border_thickness = get_width_dependent_param(image, 0.5, 1, 'border_thickness', **parameters)
    padding = get_width_dependent_param(image, 0.7, 3, 'padding', **parameters)
    dash_length = get_width_dependent_param(image, 0.5, 3, 'dash_length', **parameters)
    spacing = get_width_dependent_param(image, 0.5, 1, 'spacing', **parameters)

    # Calculate the coordinates for the inner rectangle (dashed border)
    left = padding
    top = padding
    right = width - padding
    bottom = height - padding

    # Draw the top and bottom dashed border
    for x in range(left, right, dash_length + spacing):
        draw.line([(x, top), (min(x + dash_length, right), top)], fill=color, width=border_thickness)
        draw.line([(x, bottom), (min(x + dash_length, right), bottom)], fill=color, width=border_thickness)

    # Draw the left and right dashed border
    for y in range(top, bottom, dash_length + spacing):
        draw.line([(left, y), (left, min(y + dash_length, bottom))], fill=color, width=border_thickness)
        draw.line([(right, y), (right, min(y + dash_length, bottom))], fill=color, width=border_thickness)

    # Paste the transparent layer onto the original image
    image.paste(transparent_layer, (0, 0), transparent_layer)
    return image


# Dictionary to map function names to their corresponding functions
draw_border_functions = {
    "draw_dashed_border": draw_dashed_border,
    "draw_dotted_border": draw_dotted_border,
    "draw_solid_border": draw_solid_border,
    "draw_solid_white_border": draw_solid_white_border
}
