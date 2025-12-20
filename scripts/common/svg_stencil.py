import random
from io import BytesIO

import cairosvg
from PIL import Image

from scripts.common.convert_svg_to_png import get_svg_size, compute_stencil_scale_factor


def prepare_svg_as_stencil(svg_path, canvas_width=None, canvas_height=None):
    """
    Convert an SVG file to a PNG file and scale it to fit within the specified canvas size.
    The SVG will be placed at a random position inside the canvas.

    Parameters:

    svg_path (str): Path to the SVG file.
    canvas_width (int): Width of the target canvas.
    canvas_height (int): Height of the target canvas.

    Returns:
    PIL.Image, tuple: The converted and scaled stencil image and the bounding box of the logo.
    """
    try:
        size = get_svg_size(svg_path)
        scale = compute_stencil_scale_factor((canvas_width, canvas_height), size)
        scale = scale * (random.random() * .6 + .35)

        png_data = cairosvg.svg2png(url=svg_path, scale=scale)
        stencil = Image.open(BytesIO(png_data))

        stencil_width, stencil_height = stencil.size

        # Generate random position
        pad_left = random.randint(0, canvas_width - stencil_width)
        pad_top = random.randint(0, canvas_height - stencil_height)

        # Create a new image with the same size as canvas and paste the stencil at a random position
        stencil_padded = Image.new("RGBA", (canvas_width, canvas_height), 0)  # Assuming stencil is grayscale (L mode)
        stencil_padded.paste(stencil, (pad_left, pad_top))

        # Calculate bounding box
        bounding_box = ((pad_left, pad_top), (pad_left + stencil_width, pad_top + stencil_height))

        return stencil_padded, bounding_box

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None


def apply_stencil(image, donor_image, stencil):
    """
    Apply a stencil image to overlay image2 onto image1.

    Parameters:
    image1 (PIL.Image): The base image.
    image2 (PIL.Image): The image to overlay.
    stencil (PIL.Image): The stencil image.

    Returns:
    PIL.Image: The resulting image after applying the stencil.
    """
    # Ensure the first two images are the same size
    if image.size != donor_image.size:
        raise ValueError("The first two images must be of the same size.")

    # Paste the second image onto the first using the stencil as a mask
    image.paste(donor_image, (0, 0), stencil)

    return image
