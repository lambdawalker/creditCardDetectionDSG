import colorsys


def rgb_to_hls(r, g, b):
    return colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)


def hls_to_rgb(h, l, s):
    return tuple(round(i * 255) for i in colorsys.hls_to_rgb(h, l, s))


def adjust_lightness(color, factor):
    h, l, s = rgb_to_hls(*color)
    return hls_to_rgb(h, max(0, min(1, l * factor)), s)


def compute_analogous_colors(color, separation=.07):
    h, l, s = rgb_to_hls(*color)
    return [hls_to_rgb((h + separation) % 1.0, l, s), hls_to_rgb((h - separation) % 1.0, l, s)]


def compute_complementary_color(color):
    h, l, s = rgb_to_hls(*color)
    h = (h + 0.5) % 1.0
    return hls_to_rgb(h, l, s)


def triadic_colors(color):
    h, l, s = rgb_to_hls(*color)
    return [hls_to_rgb((h + 1 / 3) % 1.0, l, s), hls_to_rgb((h + 2 / 3) % 1.0, l, s)]


