import os
import subprocess
from typing import List, Tuple, Optional


def get_conda_env_location(env_name: str) -> str:
    """
    Retrieves the filesystem location of a specified Conda environment by searching through the list of existing environments.

    Args:
        env_name (str): The name of the Conda environment whose path is being retrieved.

    Returns:
        str: The filesystem path of the specified Conda environment.

    Raises:
        Exception: If the specified environment is not found.
    """
    environments = list_conda_environments()
    for env, location in environments:
        if env == env_name:
            return location

    print(environments)
    raise Exception(f"Environment '{env_name}' not found.")


def list_conda_environments() -> List[Tuple[str, str]]:
    """
    Fetches and returns a list of Conda environments along with their filesystem paths by parsing the output of the 'conda info --envs' command.

    Returns:
        List[Tuple[str, str]]: A list of tuples where each tuple contains the name and path of a Conda environment.

    Raises:
        Exception: If there's an error executing the 'conda' command or parsing its output.
    """
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


def create_conda_environment(env_name: str, python_version: str = '3.8', conda_packages: Optional[list] = None, pip_packages: Optional[list] = None) -> None:
    """
    Creates a new Conda environment with specified settings for Python version and optional packages via Conda and pip.

    Args:
        env_name (str): The name of the Conda environment to create.
        python_version (str): The version of Python to install. Defaults to '3.8'.
        conda_packages (Optional[list]): A list of Conda packages to install.
        pip_packages (Optional[list]): A list of pip packages to install.

    Raises:
        Exception: If the environment creation fails or if there is an error during the installation of packages.
    """
    print(f"Creating Conda environment '{env_name}' with Python version '{python_version}'. This might take a while...")
    conda_packages = [] if conda_packages is None else conda_packages
    if "pip" not in conda_packages:
        conda_packages.append("pip")

    command = ['conda', 'create', '--name', env_name, f'python={python_version}'] + conda_packages + ["-y"]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    if result.returncode != 0:
        raise Exception(f"Error creating Conda environment: {result.stderr}")

    print(f"Environment '{env_name}' created successfully with Python {python_version}. Additional conda packages installed: {', '.join(conda_packages)}")
    if pip_packages:
        install_packages_with_pip(env_name, pip_packages)


def install_packages_with_pip(env_name: str, packages: List[str]):
    """
    Installs a list of packages using pip in a specified Conda environment.

    Args:
        env_name (str): The name of the Conda environment where the packages will be installed.
        packages (List[str]): A list of package names for installation via pip.

    Raises:
        Exception: If the installation fails.
    """
    print("Installing packages using pip...")
    env_path = get_conda_env_location(env_name)
    python_path = os.path.join(env_path, "python.exe")
    command = [python_path, '-m', 'pip', 'install'] + packages

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Error installing packages with pip: {result.stderr}")

    print(f"Additional pip packages installed: {', '.join(packages)}")
    print(result.stdout)



