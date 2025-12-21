import json
import os.path
from io import BytesIO
from types import SimpleNamespace

from PIL import Image
from jinja2 import Template
from playwright.sync_api import sync_playwright

from scripts.color.ColorPallet import ColorPalette
from scripts.color.conversion import rgb_to_hex
from scripts.color.text_color import best_text_color_from_palette
from scripts.common.file import ensure_output_directory
from scripts.log.Profiler import Profiler
from scripts.log.card_log import CardLog

from scripts.render.LocalResourcesHandler import LocalResourceHandler
from scripts.render.fields import gen
from scripts.templates.generators.backgorund.generate_card_background import generate_card_background

handle_local_image = LocalResourceHandler()


def render_layer(page, html_content: str):
    """
    Renders HTML content to a PNG in memory, extracts bounding boxes, and specifically
    handles local image loading using Playwright's route() method.
    """
    profiler = Profiler()
    captured_elements_data = []

    page.route(handle_local_image.match_pattern, handle_local_image)
    page.set_content(html_content)

    page.wait_for_selector('.card')

    card = page.query_selector('.card')
    image_bytes = card.screenshot(omit_background=True)

    elements = page.query_selector_all('*[capture="true"]')

    for i, element in enumerate(elements):
        bounding_box = element.bounding_box()

        if bounding_box:
            tag_name = element.evaluate('e => e.tagName')

            element_info = {
                "index": i,
                "tag": tag_name,
                "bounding_box": {
                    "x": bounding_box["x"],
                    "y": bounding_box["y"],
                    "width": bounding_box["width"],
                    "height": bounding_box["height"]
                },
                "source": element.get_attribute('src') if tag_name == 'IMG' else "Text Element"
            }
            captured_elements_data.append(element_info)

    return image_bytes, captured_elements_data


def render_layers(template_path, output_path=None, data=None, css=""):
    valid_extensions = ['.html', '.j2']
    layers = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        for template in os.listdir(template_path):
            file_ext = os.path.splitext(template)[1]
            if file_ext not in valid_extensions:
                continue

            print(f"Processing template {template}")

            with open(os.path.join(template_path, template), 'r') as f:
                html_template = f.read()

            layer_name = os.path.splitext(template)[0]

            template = Template(html_template)

            rendered_html = template.render(
                data=data,
                gen=gen,
                css=css
            )

            image_bytes, captured_elements_data = render_layer(
                page, rendered_html
            )

            pil_image = Image.open(BytesIO(image_bytes))

            layers[layer_name] = SimpleNamespace(
                name=layer_name,
                elements=captured_elements_data,
                image=pil_image
            )

            if output_path is not None:
                output_file_path = os.path.join(output_path, f"{layer_name}.png")
                ensure_output_directory(output_file_path)

                with open(output_file_path, 'wb') as f:
                    f.write(image_bytes)

        browser.close()

    return layers


def render_template(template_path, output_path=None):
    profiler = Profiler()

    card_log = CardLog()

    palette = ColorPalette()
    card_log.palette = palette

    text_color = best_text_color_from_palette(palette)
    text_color_hex = rgb_to_hex(text_color)

    common_data_path = os.path.join(template_path, "meta/common.json")

    with open(common_data_path, 'r') as f:
        common_data = json.load(f)

    meta_data_path = os.path.abspath(f"{template_path}/meta/meta.json")

    with open(meta_data_path, 'r') as f:
        meta_data = json.load(f)

    css = f"""
    body {{
        color: {text_color_hex};
    }}
    """

    layers = render_layers(template_path, output_path, common_data, css)
    first_layer = layers[meta_data["order"][0]]

    width = first_layer.image.width
    height = first_layer.image.height

    card_background = generate_card_background(
        palette,
        width,
        height,
        card_log=card_log,
    )

    layers["background_layer"] = SimpleNamespace(
        name="background_layer",
        elements=[],
        image=card_background
    )

    return layers, card_log
