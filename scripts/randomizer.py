import math
import random

import bpy
from lambdawalker.blender.find_materials import find_materials_by_regex
from lambdawalker.blender.images.assign_image_to_texture import assign_image_to_world_node, assign_image_to_texture
from lambdawalker.blender.material.randomize import randomize_material
from lambdawalker.blender.material.update import set_material_to_mesh
from lambdawalker.blender.randomize_light_properties import randomize_light_properties
from lambdawalker.blender.spatial.randomize_position_and_rotation import randomize_position_and_rotation
from lambdawalker.blender.spatial.randomize_position_in_donut import randomize_position_in_donut


def randomize_environment(background_image_pil):
    randomize_camera()

    background_image_blender = randomize_light(background_image_pil)
    bg_image_blender = randomize_table(background_image_pil)

    return [background_image_blender, bg_image_blender]


def randomize_light(background_image_pil):
    light_name = "Light"
    light = bpy.data.objects.get(light_name)

    intensity_range = (350, 800)  # Intensity range
    temperature_range = (1000, 10000)  # Temperature range in Kelvin

    randomize_light_properties(
        light, intensity_range, temperature_range=temperature_range
    )

    position_range = ("2m", "2m", "1m")  # X, Y, Z ranges for position
    point = ("0m", "0m", "3m")
    rotation_range = (math.radians(15), math.radians(15), math.radians(15))  # X, Y, Z ranges for rotation in radians
    randomize_position_and_rotation(light, position_range, rotation_range, point)

    pos_x, pos_y = randomize_position_in_donut(1.5, 3.5)

    light.location.x = pos_x
    light.location.y = pos_y

    return assign_image_to_world_node(
        "World",
        "env_light",
        background_image_pil
    )


def randomize_table(background_image_pil):
    possible_materials = find_materials_by_regex(f"tbl.*")
    material = random.choice(possible_materials)

    set_material_to_mesh("floor", material)
    randomize_material(material, random.randint(0, 99999999999))

    return assign_image_to_texture(
        material,
        "color_img",
        background_image_pil
    )


def randomize_camera():
    object_name = "Camera"
    obj = bpy.data.objects.get(object_name)

    position_range = ("1mm", "1mm", "30mm")
    point = ("0mm", "0mm", "260mm")
    rotation_range = (math.radians(1), math.radians(1), math.radians(1))  # X, Y, Z ranges for rotation in radians
    randomize_position_and_rotation(obj, position_range, rotation_range, point)


def randomize_card_position_and_rotation(card_object, object_class="horizontal_card"):
    position_range = ("5mm", "5mm", "2.5mm")
    base_position = ("0mm", "0mm", "6.5mm")

    base_rotation = (0, 0, math.radians(90) if object_class == "vertical_card" else 0)
    rotation_range = list(map(math.radians, (4, 5, 1.5)))

    randomize_position_and_rotation(
        card_object,
        position_range,
        rotation_range,
        base_position,
        base_rotation
    )
