import json
import os
import random

import PIL.Image
from PIL import ImageDraw, ImageFont

from scripts.color.conversion import rgb_to_hex
from scripts.color.ColorPallet import ColorPalette
from scripts.color.text_color import best_text_color_from_palette
from scripts.common.file import path_from_root, find_root_path
from scripts.common.get_font import get_font
from scripts.log.card_log import CardLog
from scripts.templates.draw_text import draw_left_justified_text, draw_right_justified_text
from scripts.templates.generators.backgorund.generate_card_background import generate_card_background
from scripts.templates.generators.fields import field_generators


def get_random_template(side="front"):
    templates_dir = path_from_root("./assets/templates", side)
    counter_file_path = os.path.join(templates_dir, 'counter.txt')

    if not os.path.exists(counter_file_path):
        raise FileNotFoundError(f"Counter file not found at '{counter_file_path}'")

    # Read the counter file to determine the number of templates
    with open(counter_file_path, 'r') as counter_file:
        template_count = int(counter_file.read().strip())

    if template_count <= 0:
        raise ValueError("No templates available")

    # Choose a random template number
    random_template_number = random.randint(1, template_count)
    random_template_name = f'template_{random_template_number}'
    random_template_path = os.path.join(templates_dir, f'{random_template_name}.json')

    if not os.path.exists(random_template_path):
        raise FileNotFoundError(f"Template '{random_template_name}' not found in '{random_template_path}'")

    # Read the content of the random template
    with open(random_template_path, 'r') as template_file:
        template = json.load(template_file)

    return template


def write_fields(template, image, text_color, card_log):
    draw = ImageDraw.Draw(image, "RGBA")

    elements_bound_boxes = []
    fonts_path = path_from_root("./assets/fonts")

    for element in template['elements']:
        element_type = element['type']
        element_parameters = element.get('parameters', {})

        field_generator = field_generators.get(element_type, None)

        field_data = field_generator(image=image, root_path=find_root_path(), **element_parameters) if field_generator is not None else element['originalText']

        x0, y0 = element['coordinates'][:2]
        # Calculate font size based on the element height
        image_width, image_height = image.size

        position = int(x0 * image_width), int(y0 * image_height)

        if isinstance(field_data, str):
            text_height_in_percentage = element['height']
            font_size = int(text_height_in_percentage * image_height) / 2

            try:
                font = get_font(fonts_path, font_size)
            except IOError:
                font = ImageFont.load_default(font_size)

            justified = element.get('justified', 'left')

            if justified == 'right':
                relative_bounding_box = draw_right_justified_text(draw, image.size, position, field_data, font, text_color)
            else:
                relative_bounding_box = draw_left_justified_text(draw, image.size, position, field_data, font, text_color)

            elements_bound_boxes.append({
                "type": element_type,
                "relativeBoundingBox": relative_bounding_box
            })

            card_log.fields.append({
                "type": element_type,
                "relativeBoundingBox": relative_bounding_box,
                "text": field_data
            })

        elif isinstance(field_data, PIL.Image.Image):
            iw, ih = field_data.size
            x0 = int(position[0] - iw / 2)
            y0 = int(position[1] - ih / 2)

            image.paste(field_data, (x0, y0), field_data)

            x1 = x0 + iw
            y1 = y0 + ih

            x0_rel = x0 / image_width
            y0_rel = y0 / image_height
            x1_rel = x1 / image_width
            y1_rel = y1 / image_height

            relative_bounding_box = x0_rel, y0_rel, x1_rel, y1_rel

            elements_bound_boxes.append({
                "type": element_type,
                "relativeBoundingBox": relative_bounding_box
            })

            card_log.fields.append({
                "type": element_type,
                "relativeBoundingBox": relative_bounding_box
            })

    return elements_bound_boxes


def render_template(width=900, height=540, side="front", palette=None, paint_order=None, color_profile=None, render_field=True, **_):
    card_log = CardLog()

    template = get_random_template(side=side)
    palette = palette if palette is not None else ColorPalette()
    card_log.palette = palette

    card_image = generate_card_background(
        palette,
        width,
        height,
        color_profile=template.get("color_profile") if color_profile is None else color_profile,
        paint_order=paint_order,
        card_log=card_log,
    )

    text_color = best_text_color_from_palette(palette)
    text_color_hex = rgb_to_hex(text_color)

    relative_bounding_boxes = write_fields(
        template,
        card_image,
        text_color_hex,
        card_log
    ) if render_field else []

    return card_image, relative_bounding_boxes, card_log
