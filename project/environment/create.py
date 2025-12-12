import platform
import random
import string

from project.environment.conda_interface import create_conda_environment


def generate_random_string(length: int = 5) -> str:
    """
    Generates a random string of uppercase letters.

    Args:
        length (int): Length of the string to generate. Defaults to 5.

    Returns:
        str: Randomly generated string of specified length.
    """
    letters = string.ascii_uppercase  # Create a sequence of uppercase letters
    random_string = ''.join(random.choice(letters) for _ in range(length))  # Randomly choose letters
    return random_string


def create(root: str = "./", python_version: str = None) -> None:
    """
    Creates a Conda environment for a project and writes environment details to files.

    Args:
        python_version:
        root (str): The root directory where environment files will be created. Defaults to the current directory.

    Writes:
        - Python version to e-pyver.env
        - Environment name to e-name.env

    Reads:
        - Pip packages to be installed from e-pip-packages.env
    """
    python_version = python_version if python_version is not None else platform.python_version()  # Get the current Python version
    env_name = f"syntheticDataset-{generate_random_string()}"  # Generate a unique environment name

    print(f"\n\nWorking on {root}")

    with open(f"{root}/e-name.env", "w") as f:
        f.write(env_name)

    with open(f"{root}/e-pip-packages.env", "r") as f:
        pip_packages = [p.strip() for p in f.readlines()]

    create_conda_environment(
        env_name,
        python_version,
        pip_packages=pip_packages
    )
