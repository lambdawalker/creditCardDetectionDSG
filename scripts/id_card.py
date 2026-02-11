import os
import random

import bpy
from PIL import Image
from lambdawalker.blender.find_materials import find_materials_by_regex
from lambdawalker.blender.images.assign_image_to_texture import assign_image_to_texture
from lambdawalker.blender.material.randomize import randomize_material
from lambdawalker.blender.material.update import set_material_to_mesh
from lambdawalker.blender.query.get_scene_and_camera import get_scene_and_camera
from lambdawalker.blender.render.render_scene import render_scene
from lambdawalker.blender.spatial.compute_pixel_bounding_box import compute_obj_pixel_bounding_box
from lambdawalker.file.path.ensure_directory import ensure_directory_for_file
from lambdawalker.yolo.log.vis_log import draw_bounding_boxes
from lambdawalker.yolo.log.yolo_log import create_yolo_description

from scripts.randomizer import randomize_environment, randomize_card_position_and_rotation


def render_id_simple_card(bucket_name, global_index: int, output_path: str, id_ds, photo_id_ds, background_ds, classes):
    to_clean = []
    scene, camera = get_scene_and_camera()

    next_output_file = f"{output_path}/images/{bucket_name}/{global_index + 1}.jpg"
    output_file = f"{output_path}/images/{bucket_name}/{global_index}.jpg"

    if os.path.exists(next_output_file) and os.path.exists(output_file):
        return

    card_object_name = "card"
    card_object = bpy.data.objects.get(card_object_name)

    record = id_ds[global_index]
    objects_info = record.objects[0]
    object_class = objects_info["class"]

    randomize_card_position_and_rotation(
        card_object, object_class=object_class
    )

    id_card_image_pil, photo_image_pil = _prepare_card_images(record, photo_id_ds, objects_info)
    to_clean.append(id_card_image_pil)

    id_card_image_blender, hologram_image_blender = _setup_card_material(
        card_object_name, objects_info, id_card_image_pil, photo_image_pil
    )
    to_clean.extend([id_card_image_blender, hologram_image_blender])

    background_image_pil = _setup_background(global_index, background_ds)
    to_clean.append(background_image_pil)

    to_clean = to_clean + randomize_environment(background_image_pil)

    ensure_directory_for_file(output_file)
    render_scene(output_file)

    _cleanup_blender_resources(to_clean)

    card_bounding_box = compute_obj_pixel_bounding_box(scene, card_object, camera)
    bounding_box_data = [{"class": object_class, "boundingBox": card_bounding_box}]

    _save_yolo_annotations(output_path, bucket_name, global_index, scene, bounding_box_data, classes)
    _save_visualization(output_path, bucket_name, global_index, output_file, bounding_box_data)


def _prepare_card_images(record, photo_id_ds, objects_info):
    id_card_image_pil = record.image.to_pil()
    photo_id = objects_info["photo_id"]
    photo_record = photo_id_ds[photo_id]
    photo_image_pil = photo_record.image.to_pil()

    if objects_info["class"] == "vertical_card":
        id_card_image_pil = id_card_image_pil.rotate(-90, expand=1)
        photo_image_pil = photo_image_pil.rotate(-90, expand=1)

    return id_card_image_pil, photo_image_pil


def _setup_card_material(card_object_name, objects_info, id_card_image_pil, photo_image_pil):
    subtype = objects_info["subtype"]
    possible_materials = find_materials_by_regex(f"{subtype}.*") + find_materials_by_regex("df.*")
    material = random.choice(possible_materials)
    set_material_to_mesh(card_object_name, material)

    id_card_image_blender = assign_image_to_texture(material, "color_img", id_card_image_pil)
    hologram_image_blender = assign_image_to_texture(material, "hologram_img", photo_image_pil)

    randomize_material(material, random.randint(0, 99999999999))
    return id_card_image_blender, hologram_image_blender


def _setup_background(global_index, background_ds):
    mod_index = global_index % len(background_ds)
    print(f"Using background {mod_index}")
    return background_ds[mod_index].image.to_pil()


def _save_visualization(output_path, bucket_name, global_index, output_file, bounding_box_data):
    output_file_vis = f"{output_path}/vis/{bucket_name}/{global_index}.jpg"
    ensure_directory_for_file(output_file_vis)
    draw_bounding_boxes(output_file, bounding_box_data, output_file_vis)


def _cleanup_blender_resources(to_clean):
    for data in to_clean:
        if data is None:
            continue
        elif isinstance(data, Image.Image):
            data.close()
        elif isinstance(data, bpy.types.Image):
            data.buffers_free()
            bpy.data.images.remove(data, do_unlink=True)

    bpy.context.view_layer.update()
    bpy.data.orphans_purge(do_recursive=True)


def _save_yolo_annotations(output_path, bucket_name, global_index, scene, bounding_box_data, classes):
    render = scene.render
    render_scale = render.resolution_percentage / 100.0
    width, height = (render.resolution_x * render_scale, render.resolution_y * render_scale)

    yolo_data = create_yolo_description(
        bounding_box_data,
        width, height,
        classes
    )

    yolo_txt_path = f"{output_path}/labels/{bucket_name}/{global_index}.txt"
    ensure_directory_for_file(yolo_txt_path)

    with open(yolo_txt_path, 'w') as yolo_file:
        yolo_file.write(yolo_data)
