import math
import mathutils
from torch.fx.node import base_types

from scripts.blender.spatial.randomize_position_and_rotation import randomize_position_and_rotation


def randomize_card_position_and_rotation(card_object, side="front"):
    position_range = ("5mm", "5mm", "2.5mm")
    base_position = ("0mm", "0mm", "6.5mm")

    base_rotation = (0, math.radians(180) if side == "back" else 0, 0)
    rotation_range = list(map(math.radians, (4, 5, 1.5)))

    randomize_position_and_rotation(
        card_object,
        position_range,
        rotation_range,
        base_position,
        base_rotation
    )


def calculate_center_and_plane_size(obj):
    return tuple(obj.matrix_world @ mathutils.Vector((0, 0, .0005))), obj.dimensions[:2]