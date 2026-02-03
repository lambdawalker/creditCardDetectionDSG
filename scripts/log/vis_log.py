from PIL import Image, ImageDraw, ImageFont


def draw_bounding_boxes(image_path, annotations, output_path):
    """
    Draw bounding boxes and print their type over the image.

    Args:
        image_path (str): The path to the input image.
        annotations (list): The list of annotations containing type and bounding box.
        output_path (str): The path to save the output image.
    """
    # Open the image
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Optionally, load a font
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    for annotation in annotations:
        bbox_type = annotation["class"]
        x0, y0, x1, y1 = annotation["boundingBox"]

        # Draw the bounding box
        draw.rectangle([x0, y0, x1, y1], outline="red", width=2)

    # Save the output image
    original_width, original_height = image.size

    # Calculate the new dimensions (a quarter of the original size)
    new_width = int(original_width / 2)
    new_height = int(original_height / 2)

    # Resize the image
    resized_image = image.resize((new_width, new_height))
    resized_image.save(output_path)