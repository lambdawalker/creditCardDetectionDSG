import json
import os

import bpy

from scripts.blender.purge_orphan_data import purge_orphan_data
from scripts.blender.query.get_scene_and_camera import get_scene_and_camera
from scripts.blender.query.selection import query_vertices_world_vector_in_vertex_group
from scripts.blender.render.randomize_back_side_card import randomize_back_side_card, randomize_card_back_plastic
from scripts.blender.render.randomize_environment import randomize_environment
from scripts.blender.render.randomize_front_side_card import randomize_front_side_card, randomize_card_front_plastic
from scripts.blender.render.render_scene import render_scene
from scripts.blender.spatial.compute_pixel_bounding_box import compute_obj_pixel_bounding_box, compute_vectors_pixel_bounding_box
from scripts.common.file import append_line_to_file, ensure_output_directory, find_root_path
from scripts.log.hugging_face_log import translate_to_hugging_face_format
from scripts.log.vis_log import draw_bounding_boxes
from scripts.log.yolo_log import create_yolo_description


def render_card_side(output_path, bucket_parameters, index, scene, camera, card_side):
    bucket = bucket_parameters["name"]
    output_path, bucket, index, scene, camera = setup_variables(output_path, bucket, index, scene, camera)

    # randomize_environment()  # call this first, it moves the camera and affects the computation of bounding boxes in pixel space

    card_object_name = "card"
    card_object = bpy.data.objects.get(card_object_name)
    relative_bounding_boxes = card_log = None

    if card_side == 'front':
        side_parameters = bucket_parameters.get("side_parameters", {}).get("front", {})
        relative_bounding_boxes, card_log = randomize_front_side_card(card_object, **side_parameters)
        randomize_card_front_plastic()

    elif card_side == 'back':
        side_parameters = bucket_parameters.get("side_parameters", {}).get("back", {})
        relative_bounding_boxes, card_log = randomize_back_side_card(card_object, **side_parameters)
        randomize_card_back_plastic()

    output_file = f"{output_path}/images/{bucket}/cc_{index}.jpg"
    ensure_output_directory(output_file)

    render_scene(output_file)

    card_bounding_box = compute_obj_pixel_bounding_box(scene, card_object, camera)

    if card_side == 'front':
        chip_vertices = query_vertices_world_vector_in_vertex_group(card_object, "chip")
        bounding_box_data = [
            {"type": "creditCardFront", "boundingBox": card_bounding_box},
            {"type": "chip", "boundingBox": compute_vectors_pixel_bounding_box(scene, chip_vertices, camera)}
        ]
    elif card_side == 'back':
        band_vertices = query_vertices_world_vector_in_vertex_group(card_object, "band")
        bounding_box_data = [
            {"type": "creditCardBack", "boundingBox": card_bounding_box},
            {"type": "band", "boundingBox": compute_vectors_pixel_bounding_box(scene, band_vertices, camera)}
        ]

    render = scene.render

    render_scale = render.resolution_percentage / 100.0
    width, height = (render.resolution_x * render_scale, render.resolution_y * render_scale)

    yolo_data = create_yolo_description(
        relative_bounding_boxes + bounding_box_data,
        width, height
    )

    yolo_txt_path = f"{output_path}/labels/{bucket}/cc_{index}.txt"
    ensure_output_directory(yolo_txt_path)

    with open(yolo_txt_path, 'w') as yolo_file:
        yolo_file.write(yolo_data)

    hugging_face = translate_to_hugging_face_format(
        relative_bounding_boxes + bounding_box_data,
        f"cc_{index}.jpg"
    )

    hugging_face_dump_path = f"{output_path}/images/{bucket}/metadata.jsonl"
    ensure_output_directory(hugging_face_dump_path)
    append_line_to_file(hugging_face_dump_path, json.dumps(hugging_face))

    output_file_vis = f"{output_path}/vis/{bucket}/cc_{index}.jpg"
    ensure_output_directory(output_file_vis)

    draw_bounding_boxes(
        output_file,
        relative_bounding_boxes + bounding_box_data,
        output_file_vis,
    )

    output_file_card_log = f"{output_path}/card_log/{bucket}/cc_{index}.log"
    ensure_output_directory(output_file_card_log)

    with open(output_file_card_log, 'w') as file:
        json.dump(card_log.to_dict(), file, indent=4)

    purge_orphan_data()


def setup_variables(output_path, bucket, index, scene, camera):
    bucket = bucket if bucket is not None else "test"

    if output_path is None:
        output_path = os.path.join(find_root_path(), "output", bucket)

    if scene is None:
        scene, camera = get_scene_and_camera()

    return output_path, bucket, index, scene, camera


def query_root_path():
    root = os.path.dirname(bpy.data.filepath)
    return root
