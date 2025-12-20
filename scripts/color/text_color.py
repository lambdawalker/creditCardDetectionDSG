import math

from scripts.color.ColorPallet import ColorPalette


def luminance(r, g, b):
    a = [r / 255.0, g / 255.0, b / 255.0]
    for i in range(3):
        if a[i] <= 0.03928:
            a[i] = a[i] / 12.92
        else:
            a[i] = math.pow((a[i] + 0.055) / 1.055, 2.4)
    return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722


def contrast_ratio(rgb1, rgb2):
    lum1 = luminance(*rgb1)
    lum2 = luminance(*rgb2)
    if lum1 > lum2:
        return (lum1 + 0.05) / (lum2 + 0.05)
    else:
        return (lum2 + 0.05) / (lum1 + 0.05)


def recursive_extract_tuples_from_dict(d, result=None):
    if result is None:
        result = []

    for key, value in d.items():
        if isinstance(value, tuple):
            result.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, tuple):
                    result.append(item)
        elif isinstance(value, dict):
            recursive_extract_tuples_from_dict(value, result)

    return result


def best_text_color_from_palette(pallet: ColorPalette):
    black = (0, 0, 0)
    white = (255, 255, 255)

    colors = [black, white]

    best_color = None

    primary = pallet.primary
    complementary = pallet.get_complementary()

    primary_contrast = [(c, contrast_ratio(c, primary)) for c in colors]
    complementary_contrast = [(c, contrast_ratio(c, complementary)) for c in colors]

    highest_contrast = 0

    for color, contrast in primary_contrast + complementary_contrast:
        if contrast > highest_contrast:
            highest_contrast = contrast
            best_color = color

    return best_color
