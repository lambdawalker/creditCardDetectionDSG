import os
import random


def append_line_to_file(file_path, text_line):
    try:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write(text_line + "\n")
        else:
            with open(file_path, 'a') as file:
                file.write(text_line + '\n')
    except Exception as e:
        print(f"An error occurred adding metadata for {file_path}: {e}")


def ensure_output_directory(output_path):
    if output_path is not None:
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)


def get_random_file(path=None, extension_filter=None):
    extension_filter = extension_filter if extension_filter is not None else []
    options = [os.path.join(path, f) for f in os.listdir(path)]

    if len(extension_filter):
        options = [
            f for f in options
            if os.path.splitext(f) in extension_filter or os.path.isdir(f)
        ]

    option = random.choice(options)

    if os.path.isfile(option):
        return option

    return get_random_file(path=option)


root_dir = None


def find_root_path(start_path=None):
    # If start_path is None, use the current execution path
    if root_dir:
        return root_dir

    try:
        import bpy
        start_path = os.path.dirname(bpy.data.filepath)
    except:
        pass

    if start_path is None:
        start_path = os.getcwd()

    current_path = os.path.abspath(start_path)

    while current_path != os.path.dirname(current_path):  # Until we reach the root directory
        print(current_path)
        potential_flag_file = os.path.join(current_path, 'wd')

        if os.path.isfile(potential_flag_file):
            return current_path

        current_path = os.path.dirname(current_path)  # Move one level up

    return None  # Return None if no folder with 'wd' is found


def path_from_root(*path):
    # Find the root path using the find_root_path function
    root_path = find_root_path()

    if root_path is None:
        raise FileNotFoundError("Root path with 'wd' file not found.")

    # Join the root path with the provided path
    full_path = os.path.join(root_path, *path)
    full_path = os.path.abspath(full_path)

    return full_path
