import random

from PIL import Image

from scripts.color.ColorPallet import ColorPalette
from scripts.common.dict_operations import get_random_member_from_dict
from scripts.log.card_log import CardLog
from scripts.templates.generators.backgorund.build_operations_from_paint_order import build_operations_from_paint_order
from scripts.templates.generators.backgorund import draw_border_functions
from scripts.templates.generators.backgorund.draw_base import draw_fill_background_functions
from scripts.templates.generators.backgorund.draw_details import draw_details_functions



def get_uniform_colors(palette: ColorPalette):
    return palette.get_primary_group(), palette.get_primary_group()


def get_contrasting_colors(palette: ColorPalette):
    return palette.get_primary_group(), palette.get_complementary_group()


color_selection = {
    "uniform": get_uniform_colors,
    "contrast": get_contrasting_colors
}


def generate_card_background(palette, width=900, height=540, paint_operation_cap=4, color_profile=None, paint_order=None, card_log: CardLog = None):
    card_log = card_log if card_log is not None else CardLog()

    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    color_profile, pick_colors = get_random_member_from_dict(
        color_selection,
        color_profile
    )

    card_log.color_profile = color_profile

    paint_operations = build_operations(paint_operation_cap, paint_order)

    primary_colors, complementary_colors = pick_colors(palette)
    card_log.color_selection = primary_colors, complementary_colors

    opacity = 255
    diminishing = int(opacity * .8 / paint_operation_cap)

    for operation_name, operation, operation_desc in paint_operations:
        card_log.paint_order.append(operation_name)

        operation(
            image,
            primary_colors,
            complementary_colors,
            **operation_desc.get("parameters", {
                "opacity": opacity
            })
        )

        opacity = opacity - diminishing

    return image


def get_random_operation(operations):
    return get_random_member_from_dict(operations) + ({},)


def build_operations(paint_operation_cap, paint_order):
    if paint_order is not None:
        paint_operations = build_operations_from_paint_order(paint_order)
    else:
        paint_operations = [
            get_random_operation(draw_fill_background_functions)
        ]

        paint_operations_limit = random.randint(0, paint_operation_cap)

        for i in range(1, paint_operations_limit + 1):
            paint_operations.append(
                get_random_operation(draw_details_functions)
            )

        if random.random() > .7:
            paint_operations.append(
                get_random_operation(draw_border_functions)
            )

    return paint_operations
