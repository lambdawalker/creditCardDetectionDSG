import os.path
from types import SimpleNamespace

import bpy
import bpy
from lambdawalker.dataset.DiskDataset import DiskDataset

from scripts.id_card import render_id_simple_card


def setup_memory_optimized_settings():
    bpy.context.preferences.edit.use_global_undo = False


def main(wd, buckets, dataset_name, classes, **kwargs):
    main_data_source = DiskDataset("@DS/ds.plain_id")

    photo_id_ds = DiskDataset("@DS/ds.photo_id")
    background_ds = DiskDataset("@DS/ds.indoors")


    root = os.path.join(wd, "output", dataset_name)

    setup_memory_optimized_settings()

    for progress_info in progress_generator(buckets):
        render_id_simple_card(
            progress_info.bucket_name,
            progress_info.index,
            root,
            main_data_source,
            photo_id_ds,
            background_ds,
            classes
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


