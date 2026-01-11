import random

from scripts.color.conversion import hsl_to_rgb


def generate_random_shade_color(base_color, min_distance=.1, color_range=.20):
    factor = random.uniform(min_distance / 2, color_range / 2)
    factor = random.choice([-factor, factor])

    return tuple(
        min(
            max(
                0,
                int(
                    base_color[i] * (1 + factor)
                )
            ),
            255
        )
        for i in range(3)
    )


def generate_random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    return r, g, b


def generate_muted_color():
    hue = random.randint(0, 360)
    saturation = random.randint(0, 40)
    lightness = random.randint(10, 50)

    return hsl_to_rgb(hue, saturation, lightness)
