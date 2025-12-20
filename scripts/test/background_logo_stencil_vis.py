from scripts.color.generate_pallet import ColorPalette
from scripts.common.svg_stencil import prepare_svg_as_stencil, apply_stencil
from scripts.templates.generators.backgorund.generate_card_background import generate_card_background


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

    background_a = generate_card_background(palette, color_profile="uniform")
    background_b = generate_card_background(complementary_palette, color_profile="uniform")

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
    result_image.show()
    # result_image.save('result.png')

    print(f"Bounding box of the logo: {bounding_box}")
