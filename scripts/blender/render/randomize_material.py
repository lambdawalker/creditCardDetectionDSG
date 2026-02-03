import bpy

from scripts.blender.material.update import randomize_material_parameters_from_template


def randomize_card_front_plastic():
    file_path = "./assets/materials_randomization/Front.json"
    randomize_material_parameters_from_template(file_path)
