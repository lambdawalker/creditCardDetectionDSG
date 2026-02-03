import json

import bpy

from scripts.blender.material.random_values import generate_random_value, identify_value
from .query import output_surface_node


def update_parameter(material, node, input_name, new_value):
    node = node if node is not None else output_surface_node(material)

    if isinstance(node, str):
        node = material.node_tree.nodes[node]

    inpt = node.inputs[input_name]
    inpt.default_value = new_value

    for link in inpt.links:
        if link.is_valid:
            link.to_socket.default_value = new_value


def randomize_material_parameters(template, material_name=None):
    material_name = material_name if material_name is not None else template.get("name")

    if not material_name:
        raise ValueError("No material name provided in the data.")

    material = bpy.data.materials.get(material_name)

    if material is None:
        available = sorted(m.name for m in bpy.data.materials)
        preview = ", ".join(available[:50])
        more = "" if len(available) <= 50 else f" … (+{len(available) - 50} more)"
        raise ValueError(
            f"Material '{material_name}' not found.\n"
            f"Available materials ({len(available)}): {preview}{more}"
        )

    material_nodes = material.node_tree.nodes

    for node_data in template["nodes"]:
        node_name = node_data["name"]
        inputs = node_data["inputs"]
        node = material_nodes[node_name]

        for input_data in inputs:
            input_name = input_data["name"]

            if "randomize" in input_data and input_data["randomize"]:
                default_value = input_data.get("defaultValue")
                value_type = input_data.get("inputType", None)
                sub_value_type = input_data.get("subType", None)

                try:
                    computed_value_type, computed_sub_value_type = identify_value(default_value)
                except:
                    raise Exception(f"Could not process default_value [{default_value}] of input [{input_name}] for material [{material_name}]")

                value_type = value_type if value_type is not None else computed_value_type
                sub_value_type = sub_value_type if sub_value_type is not None else computed_sub_value_type

                value_range = input_data.get("range")
                new_value = generate_random_value(value_type, sub_value_type, default_value=default_value, value_range=value_range)
            else:
                new_value = input_data.get("defaultValue")

            transform_instruction = input_data.get("transform")
            transformer = transformers.get(transform_instruction)

            if transformer is not None:
                new_value = transformer(new_value)

            update_parameter(material, node, input_name, new_value)


def read_json_from_disk(filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data


def randomize_material_parameters_from_template(filepath, material_name=None):
    data = read_json_from_disk(filepath)
    randomize_material_parameters(data, material_name)


# n_ = normalized to 0-1
def n_hsva_to_n_rgba(value):
    r = None
    g = None
    b = None

    h, s, v, a = value
    if s == 0.0:
        r = g = b = v
        return r, g, b

    i = int(h * 6)  # assuming h is in [0, 1]
    f = (h * 6) - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))

    i = i % 6

    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    elif i == 5:
        r, g, b = v, p, q

    if None in (r, g, b):
        raise Exception("could not convert from normalized hsva to normalized rgba")

    return r, g, b, a


transformers = {
    "hsvaToRbga": n_hsva_to_n_rgba
}


def set_material_to_mesh_by_name(
        obj_name: str,
        mat_name: str,
        *,
        create_if_missing: bool = True,
        slot_index: int | None = None,
        assign_to_all_faces: bool = False
) -> bpy.types.Material:
    """
    Assign a material (by name) to a mesh object (by name).

    Parameters
    ----------
    obj_name : str
        Name of the object in the scene (must be type 'MESH').
    mat_name : str
        Name of the material datablock.
    create_if_missing : bool
        If True, create the material if it doesn't exist.
    slot_index : int | None
        If None, uses the first slot if exists, else appends.
        If int, ensures that slot exists and sets it.
    assign_to_all_faces : bool
        If True, assigns the material to all polygons (enters edit mode).

    Returns
    -------
    bpy.types.Material
        The assigned material.

    Raises
    ------
    ValueError
        If object not found, wrong type, or material missing (and not creating).
    """

    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        raise ValueError(f"Object '{obj_name}' not found.")

    if obj.type != 'MESH' or obj.data is None:
        raise ValueError(f"Object '{obj_name}' is not a mesh.")

    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        if not create_if_missing:
            raise ValueError(f"Material '{mat_name}' not found.")
        mat = bpy.data.materials.new(name=mat_name)

    # Ensure object has material slots
    mats = obj.data.materials

    if slot_index is None:
        if len(mats) == 0:
            mats.append(mat)
            slot_index = 0
        else:
            mats[0] = mat
            slot_index = 0
    else:
        if slot_index < 0:
            raise ValueError("slot_index must be >= 0")
        while len(mats) <= slot_index:
            mats.append(None)
        mats[slot_index] = mat

    # Optionally assign to all faces (material_index per polygon)
    if assign_to_all_faces:
        if bpy.context.object != obj:
            bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        # Enter edit mode, select all, assign material
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        obj.active_material_index = slot_index
        bpy.ops.object.material_slot_assign()
        bpy.ops.object.mode_set(mode='OBJECT')

    return mat
