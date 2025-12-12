import os

from project.environment import get_conda_env_location


def check_conda_in_path():
    """
    Checks the PATH environment variable to search for conda installation path.

    Returns:
        str: The path to conda executable if found, None otherwise.
    """
    path_env = os.environ.get('PATH', '')
    paths = path_env.split(os.pathsep)

    for path in paths:
        if "conda" in path:
            return path

    return None


if __name__ == "__main__":
    conda_path = check_conda_in_path()

    if conda_path:
        print(f"Conda found in PATH at: {conda_path}")
        conda_base_env_location = get_conda_env_location(env_name="base")
        print(f"Conda base environment location {conda_base_env_location}")
    else:
        print("Conda not found in PATH")
