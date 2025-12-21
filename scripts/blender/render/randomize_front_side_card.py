import random

import bpy

from scripts.blender.images.assign_image_to_texture import assign_image_to_texture
from scripts.blender.spatial.compute_pixel_bounding_box import compute_vectors_pixel_bounding_box
from scripts.blender.material.update import randomize_material_parameters_from_template
from scripts.blender.spatial.compute_3d_bbox_positions import compute_3d_bbox_positions
from scripts.blender.render.spatial import randomize_card_position_and_rotation, calculate_center_and_plane_size
from scripts.common.file import path_from_root
from scripts.templates.generators.chip_generator import generate_monochromatic_chip

from scripts.templates.render_template import render_template


def randomize_front_side_card(card_object, **side_parameters):
    if isinstance(card_object, str):
        card_object = bpy.data.objects.get(card_object)

    randomize_card_position_and_rotation(card_object, side="front")

    randomize_chip()
    bpy.context.view_layer.update()

    image, relative_bounding_boxes, card_log = render_template(
         width=900, height=540, side="front", **side_parameters
    )

    assign_image_to_texture("Front", "Color", image)
    center, size = calculate_center_and_plane_size(card_object)

    scene = bpy.context.scene
    camera = scene.camera  # Ensure the scene has a camera

    data = []

    for box in relative_bounding_boxes:
        bounding_box3d = compute_3d_bbox_positions(
            center,
            card_object.rotation_euler,
            size,
            box["relativeBoundingBox"]
        )

        data.append({
            "type": box["type"],
            "boundingBox3d": bounding_box3d,
            "boundingBox": compute_vectors_pixel_bounding_box(
                scene,
                bounding_box3d,
                camera
            )
        })

    return data, card_log


def randomize_card_front_plastic():
    file_path = path_from_root("./assets/materials_randomization/Front.json")
    randomize_material_parameters_from_template(file_path)


def randomize_chip():
    file_path = path_from_root("./assets/materials_randomization/Chip.json")
    randomize_material_parameters_from_template(file_path)

    chip_image = generate_monochromatic_chip(n=random.randint(2, 4), image_width=400, padding_percentage=0.05)
    assign_image_to_texture("Chip", "HeightMap", chip_image)



