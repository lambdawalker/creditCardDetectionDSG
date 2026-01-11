import gc
import os

import bpy

from scripts.blender.images.assign_image_to_texture import assign_image_to_texture, assign_image_to_world_node
from scripts.blender.query.get_scene_and_camera import get_scene_and_camera
from scripts.blender.render.randomize_environment import randomize_environment
from scripts.blender.render.render_scene import render_scene
from scripts.blender.render.spatial import randomize_card_position_and_rotation
from scripts.blender.spatial.compute_pixel_bounding_box import compute_obj_pixel_bounding_box
from scripts.common.file import ensure_output_directory
from scripts.log.vis_log import draw_bounding_boxes
from scripts.log.yolo_log import create_yolo_description


def render_id_simple_card(bucket_name, global_index: int, output_path: str, id_ds, background_ds=None):
    scene, camera = get_scene_and_camera()

    next_output_file = f"{output_path}/images/{bucket_name}/{global_index + 1}.jpg"
    output_file = f"{output_path}/images/{bucket_name}/{global_index}.jpg"
    if os.path.exists(next_output_file) and os.path.exists(output_file):
        return

    card_object_name = "card"
    card_object = bpy.data.objects.get(card_object_name)

    randomize_card_position_and_rotation(card_object, side="front")
    randomize_environment()


    id_card_image_pil = id_ds[global_index]

    id_card_image_blender = assign_image_to_texture(
        "simple",
        "id_image_layer",
        id_card_image_pil
    )

    mod_index = global_index % len(background_ds)
    background_image_pil = background_ds[mod_index]

    background_image_blender = assign_image_to_world_node(
        "World",
        "background_image",
        background_image_pil
    )


    ensure_output_directory(output_file)

    render_scene(output_file)

    id_card_image_blender.buffers_free()
    background_image_blender.buffers_free()

    background_image_pil.close()
    id_card_image_pil.close()

    bpy.data.images.remove(id_card_image_blender, do_unlink=True)
    bpy.data.images.remove(background_image_blender, do_unlink=True)

    bpy.context.view_layer.update()

    del id_card_image_blender
    del background_image_blender
    del background_image_pil
    del id_card_image_pil

    gc.collect()

    bpy.ops.ed.undo_push(message="Purging Images")
    bpy.data.orphans_purge(do_recursive=True)

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

    yolo_txt_path = f"{output_path}/labels/{bucket_name}/{global_index}.txt"
    ensure_output_directory(yolo_txt_path)

    with open(yolo_txt_path, 'w') as yolo_file:
        yolo_file.write(yolo_data)

    output_file_vis = f"{output_path}/vis/{bucket_name}/{global_index}.jpg"
    ensure_output_directory(output_file_vis)

    draw_bounding_boxes(
        output_file,
        bounding_box_data,
        output_file_vis,
    )
