import math

import bpy

from scripts.blender.material.update import randomize_material_parameters_from_template
from scripts.blender.randomize_light_properties import randomize_light_properties
from scripts.blender.spatial.randomize_position_and_rotation import randomize_position_and_rotation
from scripts.blender.spatial.randomize_position_in_donut import randomize_position_in_donut
from scripts.common.file import path_from_root


def randomize_environment():
    randomize_light()
    randomize_table_material()
    randomize_camera()


def randomize_light():
    light_name = "Light"  # Replace with your light name
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


def randomize_table_material():
    file_path = path_from_root("./assets/materials_randomization/Solar Panels.json")
    randomize_material_parameters_from_template(file_path)


def randomize_camera():
    object_name = "Camera"
    obj = bpy.data.objects.get(object_name)

    position_range = ("1mm", "1mm", "30mm")
    point = ("0mm", "0mm", "260mm")
    rotation_range = (math.radians(1), math.radians(1), math.radians(1))  # X, Y, Z ranges for rotation in radians
    randomize_position_and_rotation(obj, position_range, rotation_range, point)
