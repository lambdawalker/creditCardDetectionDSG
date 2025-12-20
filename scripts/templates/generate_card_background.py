import random

from PIL import Image

from scripts.color.ColorPallet import ColorPalette
from scripts.log.card_log import CardLog
from scripts.templates.generators.backgorund.draw_base import draw_fill_background_functions, draw_fill_background_functions_all
from scripts.templates.generators.backgorund.draw_details import draw_details_functions
from scripts.templates.get_random_member import get_random_member


def get_uniform_colors(palette: ColorPalette):
    return palette.get_primary_group(), palette.get_primary_group()


def get_contrasting_colors(palette: ColorPalette):
    return palette.get_primary_group(), palette.get_complementary_group()


color_selection = {
    "uniform": get_uniform_colors,
    "contrast": get_contrasting_colors
}


def generate_card_background(palette, width=300, height=180, paint_operation_cap=4, color_profile=None, paint_order=None, card_log: CardLog = None):
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    color_profile, pick_colors = get_random_member(
        color_selection,
        color_profile
    )

    card_log.color_profile = color_profile

    if paint_order is None:
        paint_operations = [
            get_random_member(draw_fill_background_functions) + ({},)
        ]

        paint_operations_limit = random.randint(0, paint_operation_cap)
        for i in range(1, paint_operations_limit + 1):
            paint_operations.append(
                get_random_member(draw_details_functions) + ({},)
            )
    else:
        base = paint_order[0]
        if isinstance(base, str):
            base = {
                "name": base
            }

        base_name = base["name"]
        paint_operations = [
            (base_name, draw_fill_background_functions_all[base_name], base)
        ]

        for operation_desc in paint_order[1:]:
            if isinstance(operation_desc, str):
                operation_desc = {
                    "name": operation_desc
                }

            operation_name = operation_desc["name"]
            paint_operations.append(
                (operation_name, draw_details_functions[operation_name], operation_desc)
            )

    primary_colors, complementary_colors = pick_colors(palette)
    card_log.color_selection = primary_colors, complementary_colors

    opacity = 255
    diminishing = int(opacity * .8 / paint_operation_cap)

    for operation_name, operation, operation_desc in paint_operations:
        card_log.paint_order.append(operation_name)

        primary_colors_ = add_opacity(primary_colors, opacity)
        complementary_colors_ = add_opacity(complementary_colors, opacity)

        operation(
            image,
            primary_colors_,
            complementary_colors_,
            **operation_desc.get("parameters", {})
        )

        opacity = opacity - diminishing

    return image


def add_opacity(tuples_list, opacity_value):
    result = []
    for tup in tuples_list:
        result.append((*tup, opacity_value))
    return result
