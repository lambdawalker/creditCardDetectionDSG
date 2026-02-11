import json
import os
import site
import subprocess
import sys
from typing import List, Tuple

import bpy



def list_conda_environments() -> List[Tuple[str, str]]:
    result = subprocess.run(['conda', 'info', '--envs'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Error executing conda command: {result.stderr}")

    envs = []
    for line in result.stdout.split('\n'):
        if line.startswith('#') or not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 2:
            envs.append((parts[0], parts[-1]))

    return envs


def get_conda_env_location(env_name: str) -> str:
    environments = list_conda_environments()
    for env, location in environments:
        if env == env_name:
            return location

    print(environments)
    raise Exception(f"Environment '{env_name}' not found.")


def read_name_from_disk(root: str):
    name_path = os.path.join(root, "e-name.env")

    if not os.path.exists(name_path):
        raise Exception(f"Environment name not found at {name_path}")

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


def setup_path():
    root = os.path.dirname(bpy.data.filepath)
    if root not in sys.path:
        sys.path.append(root)

    setup(root)
    return root


def get_json_args():
    try:
        idx = sys.argv.index("--")
        return json.loads(sys.argv[idx + 1])
    except (ValueError, IndexError):
        return {}


setup_path()

from scripts.main import main  # dont move

# Passing all arguments from JSON to the main function
data = get_json_args()
main(**data)
