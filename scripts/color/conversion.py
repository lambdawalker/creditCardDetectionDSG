import colorsys


def rgb_to_hex(color):
    return '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])


def hsl_to_rgb(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
    return int(r), int(g), int(b)


def rgb_to_hsl(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360.0, s * 100.0, l * 100.0
