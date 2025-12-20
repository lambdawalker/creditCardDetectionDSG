import os.path

import bpy
from scripts.blender.images.assign_image_to_texture import assign_image_to_texture
from scripts.blender.render.randomize_environment import randomize_environment
from scripts.blender.render.render_scene import render_scene
from scripts.blender.render.spatial import randomize_card_position_and_rotation
from scripts.blender.spatial.compute_pixel_bounding_box import compute_obj_pixel_bounding_box
from scripts.log.file import ensure_output_directory
from scripts.log.vis_log import draw_bounding_boxes
from scripts.log.yolo_log import create_yolo_description
from scripts.render.render import render_template
from scripts.render_bulk import render_bulk


def render_id_card(bucket_parameters, camera, image_index: int, output_path: str, root: str, scene):
    randomize_environment(root)

    card_object_name = "card"
    card_object = bpy.data.objects.get(card_object_name)
    print(card_object)
    randomize_card_position_and_rotation(card_object, side="front")

    template_path = os.path.join(root, "assets/templates/2016")
    layers, card_log = render_template(template_path)

    bucket = bucket_parameters["name"]
    output_file = f"{output_path}/images/{bucket}/{image_index}.jpg"
    ensure_output_directory(output_file)

    for layer_name in ["background", "photo", "text", "hologram"]:
        layer_name = f"{layer_name}_layer"

        assign_image_to_texture(
            "compose",
            layer_name,
            layers[layer_name].image
        )

    render_scene(output_file)

    card_bounding_box = compute_obj_pixel_bounding_box(scene, card_object, camera)

    bounding_box_data = [
        {"type": "creditCardFront", "boundingBox": card_bounding_box},
    ]

    render = scene.render
    render_scale = render.resolution_percentage / 100.0
    width, height = (render.resolution_x * render_scale, render.resolution_y * render_scale)

    yolo_data = create_yolo_description(
        bounding_box_data,
        width, height
    )

    yolo_txt_path = f"{output_path}/labels/{bucket}/{image_index}.txt"
    ensure_output_directory(yolo_txt_path)

    with open(yolo_txt_path, 'w') as yolo_file:
        yolo_file.write(yolo_data)

    output_file_vis = f"{output_path}/vis/{bucket}/{image_index}.jpg"
    ensure_output_directory(output_file_vis)

    draw_bounding_boxes(
        output_file,
        bounding_box_data,
        output_file_vis,
    )


def render_data_set():
    data_set_name = "IdCard_V_0_0_0"

    distribution = [
        {"name": "train", "starting": 0, "limit": 1000},
        {"name": "val", "starting": 0, "limit": 250},
        {"name": "test", "starting": 0, "limit": 250}
    ]

    render_bulk(
        data_set_name,
        distribution,
        render_id_card
    )
