from PIL import ImageFont

from scripts.common.get_all_font_files_by_thickness import get_random_font_path_by_thickness


def get_font(fonts_path, font_size):
    if fonts_path is None:
        return ImageFont.load_default()
    else:
        try:
            font_path = get_random_font_path_by_thickness(fonts_path, "Bold")
            return ImageFont.truetype(font_path, font_size)
        except IOError:
            return ImageFont.load_default()



