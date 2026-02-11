import json
import os
import sys

import bpy
from lambdawalker.blender.conda import env


def setup_path():
    root = os.path.dirname(bpy.data.filepath)
    if root not in sys.path:
        sys.path.append(root)


    env.setup(root)
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
