from scripts.color.ColorPallet import ColorPalette
from scripts.templates.convert_svg_to_png import prepare_svg_as_stencil



def apply_stencil(image1, image2, stencil):
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
    if image1.size != image2.size:
        raise ValueError("The first two images must be of the same size.")

    # Create a new image for the result
    result = image1.copy()

    # Paste the second image onto the first using the stencil as a mask
    result.paste(image2, (0, 0), stencil)

    return result


def create_card_background_with_big_logo(svg_path, width, height):
    """
    Create a card background with a big logo using randomly generated backgrounds and color palettes.

    Parameters:
    svg_path (str): Path to the SVG file for the logo.
    width (int): Width of the card background.
    height (int): Height of the card background.

    Returns:
    PIL.Image, tuple: The final card background image with the big logo applied and the bounding box of the logo.
    """
    palette = ColorPalette()
    complementary_palette = ColorPalette(palette.get_complementary())

    background_a = generate_random_uniform_background(
        width=width, height=height, palette=palette
    )

    background_b = generate_random_uniform_background(
        width=width, height=height, palette=complementary_palette
    )

    stencil, bounding_box = prepare_svg_as_stencil(svg_path, width, height)

    if stencil is not None:
        result_image = apply_stencil(background_a, background_b, stencil)
        return result_image, bounding_box
    else:
        raise ValueError("Failed to convert SVG to PNG and create stencil.")


if __name__ == "__main__":
    # Example usage
    svg_path = 'HSBC.svg'
    width = 900
    height = 540
    result_image, bounding_box = create_card_background_with_big_logo(svg_path, width, height)
    result_image.save('result.png')

    print(f"Bounding box of the logo: {bounding_box}")
