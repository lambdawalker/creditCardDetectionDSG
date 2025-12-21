from io import BytesIO
from xml.etree import ElementTree as ET

import cairosvg
from PIL import Image


def svg_to_pil_image(svg_path, width=None, height=None):
    """
    Convert an SVG file to a PIL RGBA image, optionally resizing while maintaining aspect ratio.

    Parameters:
    svg_path (str): Path to the SVG file.
    width (int): Desired width of the output image.
    height (int): Desired height of the output image.

    Returns:
    PIL.Image: The converted PIL image in RGBA format.
    """
    try:
        # Load SVG data
        with open(svg_path, 'rb') as f:
            svg_data = f.read()

        svg_w, svg_h = get_svg_size(svg_path)

        if width is None and height is not None:
            width = height * svg_w / svg_h

        if height is None and width is not None:
            height = width * svg_h / svg_w


        if width and height:
            svg_data = cairosvg.svg2png(bytestring=svg_data, output_width=width, output_height=height)
        else:
            svg_data = cairosvg.svg2png(bytestring=svg_data)

        # Convert PNG data to PIL image
        pil_image = Image.open(BytesIO(svg_data)).convert("RGBA")

        return pil_image

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def compute_stencil_scale_factor(size_a, size_b):
    """
    Compute the scale factor to fit size_b within size_a while maintaining proportions.

    Parameters:
    size_a (tuple): Target size (width, height).
    size_b (tuple): Original size (width, height).

    Returns:
    float: Scale factor.
    """
    width_a, height_a = size_a
    width_b, height_b = size_b

    # Calculate the scaling factors for width and height
    scale_width = width_a / width_b
    scale_height = height_a / height_b

    return min(scale_width, scale_height)


def get_svg_size(svg_path):
    """
    Get the size of an SVG file.

    Parameters:
    svg_path (str): Path to the SVG file.

    Returns:
    tuple: Width and height of the SVG.
    """
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()

        # The SVG namespace
        namespace = {'svg': 'http://www.w3.org/2000/svg'}

        # Get the width and height attributes
        width = root.attrib.get('width')
        height = root.attrib.get('height')

        if width is None or height is None:
            # If width and height are not directly specified, try to get the viewBox attribute
            viewBox = root.attrib.get('viewBox')
            if viewBox:
                _, _, width, height = viewBox.split()

        # Convert width and height to float
        width = float(width)
        height = float(height)

        return width, height

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None
