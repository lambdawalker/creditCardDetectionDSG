import colorsys
import random

import matplotlib.pyplot as plt
import numpy as np


def hsl_to_rgb(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
    return (r, g, b)


def get_relative_luminance(h, s, l):
    r, g, b = hsl_to_rgb(h, s, l)

    def adjust(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * adjust(r) + 0.7152 * adjust(g) + 0.0722 * adjust(b)


def generate_id_palette():
    hue = random.randint(0, 360)
    saturation = random.randint(25, 60)
    lightness = random.randint(30, 85)
    primary_bg = (hue, saturation, lightness)

    if lightness > 50:
        sec_lightness = lightness - 15
    else:
        sec_lightness = lightness + 15
    sec_hue = (hue + 25) % 360
    secondary_bg = (sec_hue, saturation, sec_lightness)

    bg_lum = get_relative_luminance(*primary_bg)
    white_contrast = (1.0 + 0.05) / (bg_lum + 0.05)
    black_contrast = (bg_lum + 0.05) / (0.0 + 0.05)
    text_color = (0, 0, 100) if white_contrast > black_contrast else (0, 0, 0)

    return {
        "primary": primary_bg,
        "secondary": secondary_bg,
        "text": text_color
    }


def create_palette_visualization(palette, filename="palette_viz.png"):
    fig = plt.figure(figsize=(12, 6))

    # 1. Color Wheel (Left)
    ax1 = fig.add_subplot(1, 2, 1, projection='polar')

    # Background wheel using HSV colormap
    res_theta = 200
    res_r = 50
    theta = np.linspace(0, 2 * np.pi, res_theta)
    r = np.linspace(0, 1, res_r)
    T, RR = np.meshgrid(theta, r)

    # Use 'hsv' colormap which maps 0-1 to full hue circle
    # Theta is 0 to 2pi, so Theta/(2pi) is 0 to 1
    ax1.pcolormesh(T, RR, T / (2 * np.pi), cmap='hsv', shading='auto', alpha=0.3, zorder=0)

    ax1.set_yticklabels([])
    ax1.set_xticklabels([])
    ax1.spines['polar'].set_visible(False)
    ax1.grid(True, linestyle='--', alpha=0.5)

    # Mark the colors
    markers = {'primary': 'o', 'secondary': 's', 'text': 'D'}

    for label, (h, s, l) in palette.items():
        theta_val = np.radians(h)
        r_val = s / 100.0
        rgb = hsl_to_rgb(h, s, l)
        # Determine contrast for marker edge
        edge_color = 'white' if l < 50 else 'black'

        ax1.scatter(theta_val, r_val, color=rgb, marker=markers[label],
                    s=200, edgecolors=edge_color, linewidth=2, label=label.capitalize(), zorder=5)

    ax1.set_title("Color Wheel (Hue vs Saturation)", pad=20, fontsize=14)
    ax1.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15), ncol=3)

    # 2. Color Squares (Right)
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_axis_off()

    order = ["primary", "secondary", "text"]
    for i, name in enumerate(order):
        h, s, l = palette[name]
        rgb = hsl_to_rgb(h, s, l)

        # Draw square
        rect_y = 0.65 - i * 0.3
        rect = plt.Rectangle((0.2, rect_y), 0.6, 0.25, color=rgb, ec='black', lw=1.5)
        ax2.add_patch(rect)

        # Label
        text_contrast_color = 'white' if l < 45 else 'black'
        ax2.text(0.5, rect_y + 0.125, f"{name.upper()}\nH:{h} S:{s}% L:{l}%",
                 ha='center', va='center', weight='bold', fontsize=12,
                 color=text_contrast_color)

    ax2.set_title("Generated Palette", fontsize=14)

    plt.tight_layout()
    plt.savefig(filename, dpi=100)
    plt.close()


# Create 3 different examples
for i in range(1, 4):
    p = generate_id_palette()
    create_palette_visualization(p, f"palette_example_{i}.png")

print("Generated 3 example visualizations.")
