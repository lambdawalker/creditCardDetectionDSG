import bpy
import numpy as np
from PIL import Image


def load_image_from_file(file_path):
    return bpy.data.images.load(file_path)


def convert_pil_to_blender_image(pil_image, image_name="TempImage"):
    pil_image = pil_image.convert('RGBA')
    width, height = pil_image.size
    pixel_data = np.array(pil_image).flatten()
    blender_image = bpy.data.images.new(image_name, width=width, height=height, alpha=True)
    corrected_pixel_data = np.flipud(pixel_data.reshape((height, width, 4))).flatten()
    blender_image.pixels = (corrected_pixel_data / 255.0).tolist()
    return blender_image


def convert_numpy_to_blender_image(np_image, image_name="TempImage"):
    if np_image.ndim == 2:  # Grayscale
        height, width = np_image.shape
        pixel_data = np.stack((np_image,) * 3 + (np.ones_like(np_image),), axis=-1).flatten()
    elif np_image.ndim == 3 and np_image.shape[2] == 3:  # RGB
        height, width, _ = np_image.shape
        pixel_data = np.dstack((np_image, np.ones((height, width)) * 255)).flatten()
    elif np_image.ndim == 3 and np_image.shape[2] == 4:  # RGBA
        height, width, _ = np_image.shape
        pixel_data = np_image.flatten()
    else:
        raise ValueError("Unsupported NumPy array format")

    blender_image = bpy.data.images.new(image_name, width=width, height=height, alpha=True)
    blender_image.pixels = [v / 255 for v in pixel_data]

    return blender_image


def create_blender_image(image_input, image_name="TempImage"):
    if isinstance(image_input, bpy.types.Image):
        return image_input
    elif isinstance(image_input, str):
        return load_image_from_file(image_input)
    elif isinstance(image_input, Image.Image):
        return convert_pil_to_blender_image(image_input, image_name)
    elif isinstance(image_input, np.ndarray):
        return convert_numpy_to_blender_image(image_input, image_name)
    else:
        raise ValueError("Unsupported image input type")
