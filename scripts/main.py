import os

from scripts.blender.render.render_card_side import query_root_path, render_card_side
from scripts.render_bulk import render_bulk


def render_card_side_for_index(bucket_parameters, camera, image_index: int, output_path: str, root: str, scene, restrict_side: str):
    card_side = "front"
    if (restrict_side == "both" and image_index % 2 == 0) or restrict_side == "back":
        card_side = "back"

    render_card_side(root, output_path, bucket_parameters, image_index, scene, camera, card_side)


def render_data_set():
    data_set_name = "testX"
    distribution = [
        {"name": "train", "starting": 0, "limit": 20},
        {"name": "val", "starting": 0, "limit": 20},
        {"name": "test", "starting": 0, "limit": 20}
    ]

    render_bulk(
        data_set_name,
        distribution,
        render_card_side_for_index
    )


def render_post_validation():
    root = query_root_path()

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
                                "container_path": os.path.join(root, "assets/images/real_cards/post_validation_source")
                            }
                        }
                    ],
                    "draw_fields": False
                }
            }
        },
    ]

    render_bulk(
        data_set_name,
        distribution,
        render_card_side_for_index,
        restrict_side="front"
    )


def render_test_front(samples_limit=5):
    data_set_name = "TEST"
    distribution = [
        {"name": "train", "starting": 0, "limit": samples_limit},
    ]
    render_bulk(
        data_set_name,
        distribution,
        render_card_side_for_index,
        restrict_side="front"
    )


def render_test_back(samples_limit=5):
    data_set_name = "TEST"
    distribution = [
        {"name": "train", "starting": 0, "limit": samples_limit},
    ]
    render_bulk(
        data_set_name,
        distribution,
        render_card_side_for_index,
        restrict_side="back"
    )
