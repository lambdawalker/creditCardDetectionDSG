import os
import time

from scripts.blender.query.get_scene_and_camera import get_scene_and_camera
from scripts.blender.render.render_card_side import query_root_path


def render_bulk(data_set_name, distribution, render_function, **params):
    root = query_root_path()
    scene, camera = get_scene_and_camera()

    print(f"Rendering {data_set_name}.")

    elements_remaining = sum(value["limit"] - value["starting"] for value in distribution)
    total_items = elements_remaining

    start_time = time.time()
    total_counter = 0

    for bucket_parameters in distribution:
        bucket_name = bucket_parameters["name"]
        output_path = str(os.path.join(root, "output", data_set_name))
        starting = bucket_parameters["starting"]
        limit = bucket_parameters["limit"]
        total_to_render = limit - starting

        for image_index in range(starting, bucket_parameters["limit"]):
            print()
            print("-----------")
            print(f"    Rendering bucket [{bucket_name}]. Render item {image_index}")
            print(f"    Range: {starting}-{limit}. Total bucket items {total_to_render}")
            print()

            elements_remaining -= 1
            total_counter += 1

            render_start_time = time.time()

            render_function(
                bucket_parameters,
                camera,
                image_index,
                output_path,
                root,
                scene,
                **params
            )

            render_end_time = time.time()
            render_elapsed_time = render_end_time - render_start_time
            time_remaining_in_hours = (render_elapsed_time * elements_remaining) / 60.0 / 60.0

            print(f"    Render time: {round(render_elapsed_time, 2)}s.")
            print(f"    Total time remaining {int(time_remaining_in_hours)}h:{round((time_remaining_in_hours % 1) * 60, 2)}m")
            print(f"    Rendered {total_counter} of {total_items} total items. {elements_remaining} total items remaining.")

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\n\n!!!DONE!!!")
    print(f"Total elapsed time: {elapsed_time}s")
