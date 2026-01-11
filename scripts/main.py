import os.path
import random
from types import SimpleNamespace

import bpy
import bpy

from scripts.ImageSequence import ImageSequence
from scripts.id_card import render_id_simple_card


def setup_memory_optimized_settings():
    bpy.context.preferences.edit.use_global_undo = False


def main(wd, buckets, total_size):
    dataset_name = "IdCardV0.5"

    id_ds = ImageSequence("Y:/ai/datasets/local/plain_idV0.0.5/img")
    background_ds = ImageSequence("Y:/ai/datasets/local/indoorsV2/img")
    root = os.path.join(wd, "output", dataset_name)

    # render_id_simple_card(
    #     "TEST",
    #     random.randint(0, total_size - 1),
    #     root,
    #     id_ds,
    #     background_ds
    # )
    #
    setup_memory_optimized_settings()

    for progress_info in progress_generator(buckets):
        render_id_simple_card(
            progress_info.bucket_name,
            progress_info.index,
            root,
            id_ds,
            background_ds
        )


def progress_generator(buckets):
    """
    Generator that yields progress information for each item across all buckets.

    Yields:
        dict: Contains 'bucket_name', 'index', 'local_count', and 'bucket' info
    """
    local_count = 0

    for bucket in buckets:
        start = bucket.get('start', 0)
        size = bucket['size']
        end = start + size
        bucket_name = bucket['name']

        for i in range(start, end):
            yield SimpleNamespace(
                bucket_name=bucket_name,
                index=i,
                local_count=local_count,
            )
            local_count += 1
            print(f"PROGRESS:{local_count}", flush=True)
            # cleanup_after_render()


