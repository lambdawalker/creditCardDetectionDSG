import os
import random
from collections import defaultdict


def get_all_font_files_by_thickness(root_dir):
    font_extensions = {'.ttf', '.otf', '.woff', '.woff2'}
    fonts_by_thickness = defaultdict(list)

    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in font_extensions):
                font_name, font_extension = os.path.splitext(file)
                if '-' in font_name:
                    base_name, thickness = font_name.rsplit('-', 1)
                    font_path = os.path.join(subdir, file)
                    fonts_by_thickness[thickness].append(font_path)

    return fonts_by_thickness


def get_random_font_path_by_thickness(root_dir, thickness):
    fonts_by_thickness = get_all_font_files_by_thickness(root_dir)

    if thickness not in fonts_by_thickness:
        raise ValueError(f"No fonts found with thickness '{thickness}'")

    return random.choice(fonts_by_thickness[thickness])


