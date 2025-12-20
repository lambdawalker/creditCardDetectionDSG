from scripts.color.generate_color import generate_random_color
from scripts.color.generate_pallet import compute_analogous_colors, compute_complementary_color, triadic_colors


class ColorPalette:
    def __init__(self, primary_color=None):
        self.primary = primary_color if primary_color is not None else generate_random_color()

    def get_primary_group(self, separation=0.025):
        return [self.primary] + compute_analogous_colors(self.primary, separation)

    def get_close_analogous(self, separation=0.025):
        return compute_analogous_colors(self.primary, separation)

    def get_analogous(self, separation=0.095):
        return compute_analogous_colors(self.primary, separation)

    def get_complementary(self):
        return compute_complementary_color(self.primary)

    def get_close_complementary(self, separation=0.025):
        complementary = self.get_complementary()
        return compute_analogous_colors(complementary, separation)

    def get_complementary_group(self, separation=0.025):
        complementary = self.get_complementary()
        return [complementary] + self.get_close_complementary(separation)

    def get_triadic(self):
        return triadic_colors(self.primary)

    def to_dict(self):
        return {
            "primary": self.primary,
            "primary_group": self.get_primary_group(),
            "analogous": self.get_analogous(),
            "close_analogous": self.get_close_analogous(),
            "complementary": self.get_complementary(),
            "close_complementary": self.get_close_complementary(),
            "triadic": self.get_triadic(),
            "complementary_group": self.get_complementary_group()
        }



