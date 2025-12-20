import datetime
import math
import os
import time

from scripts.blender.query.get_scene_and_camera import get_scene_and_camera
from scripts.blender.render.render_card_side import render_card_side
from scripts.common.file import path_from_root, append_line_to_file


def render_post_validation():
    data_set_name = "post_validation"
    distribution = [
        {
            "name": "post_validation", "starting": 250, "limit": 500,
            "side_parameters": {
                "front": {
                    "paint_order": [
                        {
                            "name": "draw_random_image",
                            "parameters": {
                                "container_path": path_from_root("./assets/images/real_cards/post_validation_source")
                            }
                        }
                    ],
                    "draw_fields": False
                }
            }
        },
    ]

    render_bulk(data_set_name, distribution, restrict_side="front")


def render_data_set():
    data_set_name = "testX"
    distribution = [
        {"name": "train", "starting": 123, "limit": 1200},
        # {"name": "val", "starting": 0, "limit": 800},
        # {"name": "test", "starting": 0, "limit": 800}
    ]

    render_bulk(data_set_name, distribution, render_worker=2)


def render_test_front(samples_limit=5):
    data_set_name = "TEST-FRONT"
    distribution = [
        {"name": "train", "starting": 0, "limit": samples_limit},
    ]

    render_bulk(data_set_name, distribution, restrict_side="front")


def render_test_back(samples_limit=5):
    data_set_name = "TEST-BACK"
    distribution = [
        {"name": "train", "starting": 0, "limit": samples_limit},
    ]
    render_bulk(data_set_name, distribution, restrict_side="back")


def render_bulk(data_set_name, distribution, restrict_side="both", render_worker=None, workers=3):
    workers_flag_path = path_from_root(f"./project/")
    workers_count = len([wff for wff in os.listdir(workers_flag_path) if wff.endswith(".wrk")])

    worker_flag_path = path_from_root(f"./project/worker_{workers_count}.wrk")
    append_line_to_file(worker_flag_path, "")

    render_worker = workers_count

    scene, camera = get_scene_and_camera()

    print(f"Rendering {data_set_name}.")

    dataset_total_items = sum(value["limit"] - value["starting"] for value in distribution)

    start_time = time.time()
    total_counter = 0
    render_counter = 0

    batch_size = math.ceil(dataset_total_items / workers)
    skip_until = render_worker * batch_size
    stop_on = (render_worker + 1) * batch_size

    elements_remaining = batch_size

    for bucket_parameters in distribution:
        bucket_name = bucket_parameters["name"]
        output_path = path_from_root("./output", data_set_name)
        starting = bucket_parameters["starting"]
        limit = bucket_parameters["limit"]

        for i in range(starting, limit):
            total_counter += 1

            if total_counter < skip_until:
                continue
            if total_counter > stop_on:
                continue

            print()
            print("-----------")
            print(f"    Rendering bucket [{bucket_name}]. Render item {i}. Worker {render_worker}")
            print()

            render_start_time = time.time()

            card_side = "front"
            if (restrict_side == "both" and i % 2 == 0) or restrict_side == "back":
                card_side = "back"

            while True:
                try:
                    render_card_side(output_path, bucket_parameters, i, scene, camera, card_side)
                    break
                except Exception as e:
                    print(f"Error rendering.")
                    print(e)
                    append_line_to_file(f"./worker{render_worker}", str(e))

            render_counter += 1
            elements_remaining -= 1

            render_end_time = time.time()
            render_elapsed_time = render_end_time - render_start_time
            time_remaining = datetime.timedelta(seconds=render_elapsed_time * elements_remaining)

            print(f"    Render time: {round(render_elapsed_time, 2)}s.")
            print(f"    Total time remaining {time_remaining}")
            print(f"    Rendered {render_counter} of {batch_size} total items. {elements_remaining} total items remaining.")

    os.remove(worker_flag_path)

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\n\n!!!DONE!!!")
    print(f"Total elapsed time: {round(elapsed_time / 60 / 60, 3)}h")
