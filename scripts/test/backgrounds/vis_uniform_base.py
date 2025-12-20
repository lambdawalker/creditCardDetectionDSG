from scripts.color.generate_color import generate_random_color
from scripts.color.ColorPallet import ColorPalette
from scripts.color.vis import visualize_palette
from scripts.generators.backgorund.generate_base import ordered_triangles
from scripts.generators.backgorund.generate_random_uniform_background import generate_random_uniform_background


def test_generate_random_uniform_background_base():

    pallet = ColorPalette()
    print(pallet)

    main_color, image = generate_random_uniform_background(800, 600, pallet)

    image.show()
    visualize_palette(pallet)


