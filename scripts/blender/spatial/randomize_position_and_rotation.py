import random
from mathutils import Vector, Euler
from scripts.blender.spatial.parce_distance import parse_distance


def randomize_position_and_rotation(obj, pos_range, rot_range, ori_position=("0m", "0m", "0m"), ori_rotation=(0, 0, 0)):
    pos_x_range = parse_distance(pos_range[0])
    pos_y_range = parse_distance(pos_range[1])
    pos_z_range = parse_distance(pos_range[2])

    pos_x = parse_distance(ori_position[0]) + random.uniform(-pos_x_range, pos_x_range)
    pos_y = parse_distance(ori_position[1]) + random.uniform(-pos_y_range, pos_y_range)
    pos_z = parse_distance(ori_position[2]) + random.uniform(-pos_z_range, pos_z_range)

    obj.location = Vector((pos_x, pos_y, pos_z))

    # Generate random rotation within range (radians)
    rot_x = random.uniform(-rot_range[0], rot_range[0]) + ori_rotation[0]
    rot_y = random.uniform(-rot_range[1], rot_range[1]) + ori_rotation[1]
    rot_z = random.uniform(-rot_range[2], rot_range[2]) + ori_rotation[2]

    # Apply random rotation
    obj.rotation_euler = Euler((rot_x, rot_y, rot_z), 'XYZ')