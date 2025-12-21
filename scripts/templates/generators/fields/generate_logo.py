import os
import os.path

from scripts.common.file import get_random_file
from scripts.common.convert_svg_to_png import svg_to_pil_image


def get_random_payment_network_logo(root_path=None, image=None, width=None, height=None):
    assets_path = os.path.join(root_path, "assets", "images", "logo_card_type")
    assets_path = os.path.abspath(assets_path)

    candidate_path = get_random_file(assets_path, ["svg"])

    # Convert SVG to PIL RGBA image
    w, h = image.size

    width = width * w if width is not None else None
    height = height * h if height is not None else None
    return svg_to_pil_image(candidate_path, width, height)
