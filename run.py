import json
import math
import os
import subprocess
import threading

from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, SpinnerColumn, MofNCompleteColumn

from scripts.ImageSequence import ImageSequence


def start_blender_instance(progress, task_id, blender_path, blend_file, script_path, data, restart_every=80):
    chunk_size = sum(item['size'] for item in data["buckets"])
    task = progress.add_task(f"[cyan]Instance {task_id}", total=chunk_size, status="[yellow]Initializing...")

    completed_total = 0
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    while completed_total < chunk_size:
        # Update data for the current 'restart' segment
        # We need to tell the Blender script where to resume for each bucket
        current_offset_in_chunk = 0
        temp_data = json.loads(json.dumps(data))  # Deep copy

        remaining_to_skip = completed_total

        for bucket in temp_data["buckets"]:
            # If we've already finished this bucket in previous runs, set size to 0
            if remaining_to_skip >= bucket['size']:
                remaining_to_skip -= bucket['size']
                bucket['size'] = 0
            else:
                # Adjust the start offset and reduce size by what we've already done
                bucket['start'] = bucket.get('start', 0) + remaining_to_skip
                bucket['size'] -= remaining_to_skip
                remaining_to_skip = 0

        command = [
            blender_path, blend_file,
            "--background", "--python", script_path,
            "--", json.dumps(temp_data)
        ]

        full_output = []
        progress_since_restart = 0

        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env
            )

            progress.update(task, status=f"[green]Running (Part {completed_total})")

            for line in iter(process.stdout.readline, ""):
                full_output.append(line)
                line_clean = line.strip()

                if task_id == 5:
                    pass
                    #print(f"W{task_id}>" ,line_clean, end="\n")

                if "Traceback" in line_clean or "Error:" in line_clean:
                    has_python_error = True

                if line_clean.startswith("PROGRESS:"):
                    # Assuming PROGRESS: value is absolute to the CURRENT sub-process run
                    # or relative to the start of the script
                    val = int(float(line_clean.split(":")[1]))

                    # Track incremental progress
                    increment = val - progress_since_restart
                    completed_total += increment
                    progress_since_restart = val

                    progress.update(task, completed=completed_total)

                    # CHECK FOR RESTART TRIGGER
                    if progress_since_restart >= restart_every:
                        progress.update(task, status="[bold blue]Restarting for Memory...")
                        process.terminate()
                        break

            process.wait()

            # Handle legitimate crashes
            if process.returncode != 0 and not progress_since_restart >= restart_every:
                # ... [Keep your existing error logging logic here] ...
                progress.update(task, status="[bold red]CRASHED")
                break  # Exit the while loop on actual errors

        except Exception as e:
            progress.update(task, status=f"[bold red]System Error")
            print(f"\nInternal Wrapper Error: {e}")
            break

    if completed_total >= chunk_size:
        progress.update(task, status="[bold green]Success")


def run_blender_with_progress(blender_path, blend_file, script_path, jobs):
    # Added a {task.fields[status]} column to the UI
    with Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("• {task.fields[status]}"),
            TimeElapsedColumn(),
            SpinnerColumn(),
            TimeRemainingColumn(),
            SpinnerColumn(),
            MofNCompleteColumn()
    ) as progress:

        threads = []
        for i, job_config in enumerate(jobs):
            t = threading.Thread(
                target=start_blender_instance,
                args=(progress, i, blender_path, blend_file, script_path, job_config)
            )
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

    print("\nAll processes finished. Check current directory for crash logs if any instance failed.")


def yolo_splits(dataset_size):
    """
    Returns YOLO-style dataset splits with absolute limits.

    Rules:
    - < 1,000 samples → 85 / 10 / 5
    - 1,000–9,999     → 80 / 10 / 10
    - >= 10,000       → 75 / 15 / 10
    """

    if dataset_size < 1_000:
        ratios = {"train": 0.85, "val": 0.10, "test": 0.05}
    elif dataset_size < 10_000:
        ratios = {"train": 0.80, "val": 0.10, "test": 0.10}
    else:
        ratios = {"train": 0.75, "val": 0.15, "test": 0.10}

    train_size = int(dataset_size * ratios["train"])
    val_size = int(dataset_size * ratios["val"])
    test_size = dataset_size - train_size - val_size

    return [
        {"name": "train", "size": train_size},
        {"name": "val", "size": val_size},
        {"name": "test", "size": test_size}
    ]


def split_workload_with_offsets(metadata, n):
    total_size = sum(item['size'] for item in metadata)
    target_capacity = total_size / n

    # Track the current read-head for each named split
    # e.g., {'train': 0, 'val': 0, 'test': 0}
    offsets = {item['name']: 0 for item in metadata}

    # Work on a copy to avoid mutating input
    remaining_work = [dict(item) for item in metadata]

    buckets = []

    for i in range(n):
        current_bucket = []
        filled_in_this_bucket = 0

        # The last bucket should just take everything left to avoid rounding errors
        is_last_bucket = (i == n - 1)

        while remaining_work:
            item = remaining_work[0]
            name = item['name']

            # How much space is left in this worker's bucket?
            space_left = target_capacity - filled_in_this_bucket

            if not is_last_bucket and item['size'] > space_left:
                # Partial fit: take only what we need
                take = math.floor(space_left)
                if take > 0:
                    entry = {'name': name, 'size': take}
                    if offsets[name] > 0:
                        entry['start'] = offsets[name]

                    current_bucket.append(entry)
                    offsets[name] += take + 1
                    item['size'] -= take
                    filled_in_this_bucket += take

                # Bucket is full, move to next worker
                break
            else:
                # Full fit: take the whole remaining chunk of this split
                take = item['size']
                entry = {'name': name, 'size': take}
                if offsets[name] > 0:
                    entry['start'] = offsets[name]

                current_bucket.append(entry)
                offsets[name] += take + 1
                filled_in_this_bucket += take
                remaining_work.pop(0)  # This split is fully allocated

        buckets.append(current_bucket)

    return buckets


def main(instances=8):
    id_dataset = ImageSequence("Y:/ai/datasets/local/plain_idV0.0.5/img")
    dataset_size = len(id_dataset)

    buckets = yolo_splits(dataset_size)
    buckets_per_process = split_workload_with_offsets(buckets, instances)
    print(f"Working Directory: {os.getcwd()}")
    print(f"Dataset Size: {dataset_size}")

    jobs = [
        {
            "wd": os.getcwd(),
            "buckets": bpp, "total_size": dataset_size
        } for bpp in buckets_per_process
    ]

    run_blender_with_progress(
        blender_path=r"C:\Program Files\Blender Foundation\Blender 5.0\blender.exe",
        blend_file="bitmapMaterialMask.blend",
        script_path="scripts/init.py",
        jobs=jobs
    )


if __name__ == "__main__":
    main()
