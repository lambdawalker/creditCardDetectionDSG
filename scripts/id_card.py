import os
import random

import bpy
from PIL import Image
from lambdawaker.blender.find_materials import find_materials_by_regex
from lambdawaker.blender.images.assign_image_to_texture import assign_image_to_texture
from lambdawaker.blender.material.randomize import randomize_material
from lambdawaker.blender.material.update import set_material_to_mesh
from lambdawaker.blender.query.get_scene_and_camera import get_scene_and_camera
from lambdawaker.blender.render.randomize_environment import randomize_environment
from lambdawaker.blender.render.render_scene import render_scene
from lambdawaker.blender.render.spatial import randomize_card_position_and_rotation
from lambdawaker.blender.spatial.compute_pixel_bounding_box import compute_obj_pixel_bounding_box
from lambdawaker.file.path.ensure_directory import ensure_directory_for_file



from scripts.log.vis_log import draw_bounding_boxes
from scripts.log.yolo_log import create_yolo_description


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

    id_card_image_pil = record.image.to_pil()
    to_clean.append(id_card_image_pil)
    objects_info = record.objects[0]
    object_class = objects_info["class"]

    randomize_card_position_and_rotation(
        card_object, object_class=object_class
    )

    photo_id = objects_info["photo_id"]

    photo_record = photo_id_ds[photo_id]
    photo_image_pil = photo_record.image.to_pil()

    if objects_info["class"] == "vertical_card":
        id_card_image_pil = id_card_image_pil.rotate(-90, expand=1)
        photo_image_pil = photo_image_pil.rotate(-90, expand=1)

    subtype = objects_info["subtype"]
    possible_materials = find_materials_by_regex(f"{subtype}.*") + find_materials_by_regex("df.*")

    material = random.choice(possible_materials)
    set_material_to_mesh(card_object_name, material)

    id_card_image_blender = assign_image_to_texture(
        material,
        "color_img",
        id_card_image_pil
    )

    hologram_image_blender = assign_image_to_texture(
        material,
        "hologram_img",
        photo_image_pil
    )

    randomize_material(material, random.randint(0, 99999999999))

    to_clean.append(id_card_image_blender)
    to_clean.append(hologram_image_blender)

    mod_index = global_index % len(background_ds)
    print(f"Using background {mod_index}")

    background_image_pil = background_ds[mod_index].image.to_pil()
    to_clean.append(background_image_pil)

    to_clean = to_clean + randomize_environment(background_image_pil)

    ensure_directory_for_file(output_file)
    render_scene(output_file)

    background_image_pil.close()
    id_card_image_pil.close()

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

    card_bounding_box = compute_obj_pixel_bounding_box(scene, card_object, camera)

    bounding_box_data = [
        {"class": object_class, "boundingBox": card_bounding_box},
    ]

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

    output_file_vis = f"{output_path}/vis/{bucket_name}/{global_index}.jpg"
    ensure_directory_for_file(output_file_vis)

    draw_bounding_boxes(
        output_file,
        bounding_box_data,
        output_file_vis,
    )
