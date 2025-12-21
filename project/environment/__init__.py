import os
import site

from project.environment.conda_interface import get_conda_env_location


def read_name_from_disk(root: str):
    with open(os.path.join(root, "e-name.env"), "r") as f:
        return f.read().strip()


def setup(root: str, env_name: str = None):
    """
    Configures the Python environment to use libraries from a specified Conda environment.
    This setup is particularly important when using Blender, which needs to access Python libraries managed by Conda.

    Raises:
        Exception: When an error occurs during the subprocess execution or if the 'conda' command fails.
        Exception: If the environment is not found.
    """

    env_name = env_name if env_name is not None else read_name_from_disk(root)

    environment_location = get_conda_env_location(env_name)
    site_packages = os.path.join(environment_location, "Lib/site-packages")
    site.addsitedir(site_packages)

    return env_name, environment_location
