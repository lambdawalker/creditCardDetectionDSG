bl_info = {
    "name": "Material Randomizer Pro (HSV + Features)",
    "author": "Gemini AI",
    "version": (1, 10, 0),
    "blender": (4, 0, 0),
    "location": "Node Editor > Sidebar > Randomizer",
    "description": "Advanced material randomization with Texture Swapping, ColorRamps, and Smart Group Limits. Includes internal preset storage and list filtering.",
    "category": "Material",
}

import colorsys
import json
import random
import zlib
import os
import math

import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    EnumProperty,
    IntProperty,
    PointerProperty,
    StringProperty
)
from bpy.types import PropertyGroup, NodeSocket, Node, Panel, Operator, UIList


# ------------------------------------------------------------------------
#   Core Logic: Randomization
# ------------------------------------------------------------------------

def get_random_value(min_val, max_val, dist_type, seed_val):
    """Calculates a random value based on distribution type using a specific seed."""
    random.seed(seed_val)

    # Ensure min is actually min
    real_min = min(min_val, max_val)
    real_max = max(min_val, max_val)

    if dist_type == 'UNIFORM':
        return random.uniform(real_min, real_max)

    elif dist_type == 'GAUSSIAN':
        mu = (real_min + real_max) / 2
        sigma = (real_max - real_min) / 6  # 99.7% within range
        val = random.gauss(mu, sigma)
        return max(real_min, min(val, real_max))  # Clamp to stay in range

    elif dist_type == 'STEPPED':
        steps = 5
        if real_max == real_min: return real_min
        step_val = (real_max - real_min) / steps
        return real_min + (round(random.random() * steps) * step_val)

    return real_min


def randomize_socket_color(socket, props, socket_seed):
    """
    Performs randomization in HSV space, then converts to RGB for the socket.
    """
    # 1. Gather HSV Ranges directly from properties
    h_min, h_max = props.min_h, props.max_h
    s_min, s_max = props.min_s, props.max_s
    v_min, v_max = props.min_v, props.max_v
    a_min, a_max = props.min_a, props.max_a

    # Fix zeroes if max is accidentally 0 (though 0 is valid for Hue, usually users want range)
    if h_max == 0 and h_min == 0: h_max = 1.0  # Default full range if untouched

    # 2. Randomize in HSV Space
    h_final = get_random_value(h_min, h_max, props.distribution_type, socket_seed + 1)
    s_final = get_random_value(s_min, s_max, props.distribution_type, socket_seed + 2)
    v_final = get_random_value(v_min, v_max, props.distribution_type, socket_seed + 3)
    a_final = get_random_value(a_min, a_max, props.distribution_type, socket_seed + 4)

    # 3. Wrap Hue
    h_final = h_final % 1.0

    # 4. Convert to RGB
    r, g, b = colorsys.hsv_to_rgb(h_final, s_final, v_final)

    # 5. Apply
    socket.default_value = (r, g, b, a_final)


def randomize_texture(node, node_props, seed):
    """Swaps the texture image from a directory."""
    folder = node_props.texture_folder
    if not folder or not os.path.exists(folder):
        return

    # Cache file list? For now, simple listdir is safer for dynamic folders
    valid_exts = {'.png', '.jpg', '.jpeg', '.tif', '.tiff', '.exr', '.bmp'}
    try:
        files = sorted([
            f for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f)) and os.path.splitext(f)[1].lower() in valid_exts
        ])
    except Exception:
        return

    if not files:
        return

    random.seed(seed)
    choice = random.choice(files)
    filepath = os.path.join(folder, choice)

    # Avoid reloading if already set
    if node.image and node.image.filepath == filepath:
        return

    try:
        # Load with check_existing to prevent memory bloating
        img = bpy.data.images.load(filepath, check_existing=True)
        node.image = img
    except:
        pass


def randomize_ramp(node, node_props, seed):
    """Randomizes ColorRamp stops."""
    ramp = node.color_ramp
    random.seed(seed)

    for i, elt in enumerate(ramp.elements):
        # Seed per element
        e_seed = seed + (i * 53)

        # 1. Randomize Position (Jitter)
        if node_props.ramp_pos_jitter > 0:
            random.seed(e_seed)
            jitter = random.uniform(-node_props.ramp_pos_jitter, node_props.ramp_pos_jitter)
            new_pos = elt.position + jitter
            elt.position = max(0.0, min(1.0, new_pos))

        # 2. Randomize Color
        # Convert current color to HSV, apply jitter, convert back
        curr_r, curr_g, curr_b, curr_a = elt.color
        h, s, v = colorsys.rgb_to_hsv(curr_r, curr_g, curr_b)

        random.seed(e_seed + 1)
        h_new = (h + random.uniform(-node_props.ramp_range_h, node_props.ramp_range_h)) % 1.0

        random.seed(e_seed + 2)
        s_new = max(0.0, min(1.0, s + random.uniform(-node_props.ramp_range_s, node_props.ramp_range_s)))

        random.seed(e_seed + 3)
        v_new = max(0.0, min(1.0, v + random.uniform(-node_props.ramp_range_v, node_props.ramp_range_v)))

        r, g, b = colorsys.hsv_to_rgb(h_new, s_new, v_new)
        elt.color = (r, g, b, curr_a)


def get_stable_hash(s):
    return zlib.crc32(s.encode('utf-8')) & 0xffffffff


def randomize_node(node, base_seed):
    """Randomizes a single node based on global seed + local offset."""
    if not getattr(node, "randomizer_enabled", False):
        return

    node_id = get_stable_hash(node.name)
    # Include local seed offset allows re-rolling just this node
    local_offset = getattr(node.randomizer_node_props, "seed_offset", 0)
    node_seed = base_seed + (node_id * 31) + local_offset

    # --- Special Node Type Handling ---
    if node.type == 'TEX_IMAGE':
        randomize_texture(node, node.randomizer_node_props, node_seed)

    elif node.type == 'VALTORGB':  # ColorRamp
        randomize_ramp(node, node.randomizer_node_props, node_seed)

    # --- Standard Socket Handling ---
    for i, socket in enumerate(node.inputs):
        props = socket.randomizer_props

        if props.is_locked or socket.is_linked:
            continue

        # Include socket-specific offset for single-property randomization
        socket_seed = node_seed + (i * 7919) + props.seed_offset

        if socket.type == 'VALUE':
            val = get_random_value(props.min_float, props.max_float, props.distribution_type, socket_seed)
            socket.default_value = val

        elif socket.type == 'VECTOR':
            v_mode = props.vector_mode

            # X Calculation
            x = get_random_value(props.min_vec[0], props.max_vec[0], props.distribution_type, socket_seed + 1)

            if v_mode == 'UNIFORM':
                # X controls all
                y = x
                z = x
            else:
                # Independent
                y = get_random_value(props.min_vec[1], props.max_vec[1], props.distribution_type, socket_seed + 2)
                z = get_random_value(props.min_vec[2], props.max_vec[2], props.distribution_type, socket_seed + 3)

            # Snapping / Quantization
            if v_mode == 'SNAP_90':
                # 90 degrees = pi/2
                # We assume input is radians (standard for Mapping Node Rotation)
                step = math.pi / 2
                x = round(x / step) * step
                y = round(y / step) * step
                z = round(z / step) * step
            elif v_mode == 'INTEGER':
                x = round(x)
                y = round(y)
                z = round(z)

            socket.default_value = (x, y, z)

        elif socket.type == 'RGBA':
            randomize_socket_color(socket, props, socket_seed)


def randomize_material(material, context):
    if not material or not material.use_nodes:
        return

    base_seed = material.randomizer_seed
    nodes = material.node_tree.nodes

    for node in nodes:
        randomize_node(node, base_seed)


# ------------------------------------------------------------------------
#   Helpers
# ------------------------------------------------------------------------

def get_socket_limits(target_node, target_socket):
    found_min = None
    found_max = None
    subtype = None

    # 1. Try to find Group Interface limits & Subtype
    if target_node.type == 'GROUP' and target_node.node_tree:
        if hasattr(target_node.node_tree, "interface"):
            for item in target_node.node_tree.interface.items_tree:
                if item.identifier == target_socket.identifier:
                    if hasattr(item, "min_value"): found_min = item.min_value
                    if hasattr(item, "max_value"): found_max = item.max_value
                    if hasattr(item, "subtype"): subtype = item.subtype
                    break

    # 2. Fallback to direct socket limits if interface didn't provide them
    if found_min is None: found_min = getattr(target_socket, "min_value", -10000.0)
    if found_max is None: found_max = getattr(target_socket, "max_value", 10000.0)

    # 3. Check if limits are effectively "Infinite" / Undefined
    limit_undefined = (found_min <= -10000.0 and found_max >= 10000.0)

    if limit_undefined:
        # A. Try Subtype Defaults
        if subtype == 'FACTOR': return 0.0, 1.0
        if subtype == 'PERCENTAGE': return 0.0, 100.0
        if subtype in {'ANGLE', 'EULER'}: return 0.0, math.pi * 2
        if subtype == 'COLOR': return 0.0, 1.0

        # B. Name-Based Heuristics (Standard PBR names)
        name_lower = target_socket.name.lower()

        # Scale: Prevent 0.0, assume user wants variation around current size
        if 'scale' in name_lower:
            val = 1.0
            if hasattr(target_socket, "default_value"):
                dv = target_socket.default_value
                val = dv[0] if hasattr(dv, "__len__") else dv
            if val == 0: val = 1.0
            return val * 0.5, val * 1.5

        # PBR Maps: Always 0-1
        if any(k in name_lower for k in {'roughness', 'metallic', 'specular', 'transmission', 'alpha', 'fac', 'factor'}):
            return 0.0, 1.0

        # C. Try Default Value Heuristic (Applied to any node with undefined limits)
        val = 0.0
        if hasattr(target_socket, "default_value"):
            dv = target_socket.default_value
            if hasattr(dv, "__len__"):
                val = dv[0]  # Just use X for heuristic if vector
            else:
                val = dv

        if val > 0: return 0.0, val * 2.0
        if val < 0: return val * 2.0, 0.0
        # If val is 0, we fall through to standard clamping or 0-1 if mostly positive context
        # But let's return 0-1 as a safe generic default for undefined positive-ish params
        return 0.0, 1.0

    return found_min, found_max


def apply_group_storage(node, specific_socket=None):
    """
    Attempts to read randomized limits from the Group Input node inside the Group Tree.
    Returns True if data was found and applied.
    """
    if node.type != 'GROUP' or not node.node_tree:
        return False

    # Find the Group Input Node inside the tree
    group_input = None
    for n in node.node_tree.nodes:
        if n.type == 'GROUP_INPUT':
            group_input = n
            break

    if not group_input or "randomizer_limits_json" not in group_input:
        return False

    try:
        data = json.loads(group_input["randomizer_limits_json"])
    except:
        return False

    sockets_to_process = [specific_socket] if specific_socket else node.inputs
    did_apply = False

    for sock in sockets_to_process:
        if sock.name in data:
            s_data = data[sock.name]
            p = sock.randomizer_props

            if "min_f" in s_data: p.min_float = s_data["min_f"]
            if "max_f" in s_data: p.max_float = s_data["max_f"]
            if "min_v" in s_data: p.min_vec = s_data["min_v"]
            if "max_v" in s_data: p.max_vec = s_data["max_v"]

            if "min_hsv" in s_data:
                p.min_h, p.min_s, p.min_v, p.min_a = s_data["min_hsv"]
            if "max_hsv" in s_data:
                p.max_h, p.max_s, p.max_v, p.max_a = s_data["max_hsv"]

            did_apply = True

    return did_apply


# --- Preset Helpers ---

def capture_preset_data(mat):
    """Captures all randomizer settings for the material into a dict."""
    data = {"material_name": mat.name, "seed": mat.randomizer_seed, "nodes": {}}
    for node in mat.node_tree.nodes:
        if getattr(node, "randomizer_enabled", False):
            np = node.randomizer_node_props
            node_data = {
                "enabled": True,
                "tex_folder": np.texture_folder,
                "ramp_h": np.ramp_range_h, "ramp_s": np.ramp_range_s, "ramp_v": np.ramp_range_v, "ramp_j": np.ramp_pos_jitter,
                "seed_off": np.seed_offset,
                "sockets": {}
            }
            for socket in node.inputs:
                p = socket.randomizer_props
                s_data = {
                    "locked": p.is_locked, "dist": p.distribution_type, "vec_mode": p.vector_mode,
                    "min_f": p.min_float, "max_f": p.max_float,
                    "min_v": list(p.min_vec), "max_v": list(p.max_vec),
                    "min_hsv": [p.min_h, p.min_s, p.min_v, p.min_a],
                    "max_hsv": [p.max_h, p.max_s, p.max_v, p.max_a]
                }
                node_data["sockets"][socket.name] = s_data
            data["nodes"][node.name] = node_data
    return data


def apply_preset_data(mat, data):
    """Applies a data dict to the material randomizer settings."""
    mat.randomizer_seed = data.get("seed", 0)

    # Reset current state first
    for node in mat.node_tree.nodes:
        if hasattr(node, "randomizer_enabled"): node.randomizer_enabled = False

    # Apply data
    for node_name, node_data in data.get("nodes", {}).items():
        node = mat.node_tree.nodes.get(node_name)
        if node:
            node.randomizer_enabled = node_data.get("enabled", False)
            np = node.randomizer_node_props
            np.texture_folder = node_data.get("tex_folder", "")
            np.ramp_range_h = node_data.get("ramp_h", 0.1)
            np.ramp_range_s = node_data.get("ramp_s", 0.1)
            np.ramp_range_v = node_data.get("ramp_v", 0.1)
            np.ramp_pos_jitter = node_data.get("ramp_j", 0.05)
            np.seed_offset = node_data.get("seed_off", 0)

            for sock_name, s_data in node_data.get("sockets", {}).items():
                sock = node.inputs.get(sock_name)
                if sock:
                    p = sock.randomizer_props
                    p.is_locked = s_data.get("locked", False)
                    p.distribution_type = s_data.get("dist", 'UNIFORM')
                    p.vector_mode = s_data.get("vec_mode", 'FREE')
                    p.min_float = s_data.get("min_f", 0.0)
                    p.max_float = s_data.get("max_f", 1.0)
                    p.min_vec = s_data.get("min_v", (0, 0, 0))
                    p.max_vec = s_data.get("max_v", (1, 1, 1))
                    if "min_hsv" in s_data:
                        p.min_h, p.min_s, p.min_v, p.min_a = s_data["min_hsv"]
                        p.max_h, p.max_s, p.max_v, p.max_a = s_data["max_hsv"]
                    p.is_initialized = True


# ------------------------------------------------------------------------
#   Update Handlers
# ------------------------------------------------------------------------

def on_main_update(self, context):
    mat = context.object.active_material
    if mat and mat.randomizer_auto_update:
        randomize_material(mat, context)
        mat.node_tree.interface_update(context)


# --- Sync Helpers ---
def sync_rgb_to_hsv(props, is_min):
    if props.is_updating: return
    props.is_updating = True
    try:
        col = props.min_col if is_min else props.max_col
        h, s, v = colorsys.rgb_to_hsv(max(0, min(1, col[0])), max(0, min(1, col[1])), max(0, min(1, col[2])))
        if is_min:
            props.min_h, props.min_s, props.min_v, props.min_a = h, s, v, col[3]
        else:
            props.max_h, props.max_s, props.max_v, props.max_a = h, s, v, col[3]
    finally:
        props.is_updating = False


def sync_hsv_to_rgb(props, is_min):
    if props.is_updating: return
    props.is_updating = True
    try:
        if is_min:
            r, g, b = colorsys.hsv_to_rgb(props.min_h, props.min_s, props.min_v)
            props.min_col = (r, g, b, props.min_a)
        else:
            r, g, b = colorsys.hsv_to_rgb(props.max_h, props.max_s, props.max_v)
            props.max_col = (r, g, b, props.max_a)
    finally:
        props.is_updating = False


def update_min_rgb(self, context): sync_rgb_to_hsv(self, is_min=True); on_main_update(self, context)


def update_max_rgb(self, context): sync_rgb_to_hsv(self, is_min=False); on_main_update(self, context)


def update_min_hsv(self, context): sync_hsv_to_rgb(self, is_min=True); on_main_update(self, context)


def update_max_hsv(self, context): sync_hsv_to_rgb(self, is_min=False); on_main_update(self, context)


def update_node_enable(self, context):
    if not self.randomizer_enabled: return

    # 1. Try to load persistent limits from the Group Input first
    if self.type == 'GROUP':
        # If any data was applied, we consider this initialized
        if apply_group_storage(self):
            for socket in self.inputs:
                socket.randomizer_props.is_initialized = True

    # 2. Initialize remaining uninitialized sockets with heuristics
    for socket in self.inputs:
        props = socket.randomizer_props
        if props.is_initialized: continue

        if socket.type in {'VALUE', 'INT'}:
            mn, mx = get_socket_limits(self, socket)
            props.min_float = mn
            props.max_float = mx
            props.is_initialized = True
        elif socket.type == 'VECTOR':
            mn, mx = get_socket_limits(self, socket)
            props.min_vec = (mn, mn, mn)
            props.max_vec = (mx, mx, mx)
            props.is_initialized = True
        elif socket.type == 'RGBA':
            props.is_initialized = True


# ------------------------------------------------------------------------
#   Property Groups
# ------------------------------------------------------------------------

class RandomizerNodeProps(PropertyGroup):
    """Properties specific to the Node type (not just sockets)"""

    # Local offset allows "Re-rolling" this specific node without changing global seed
    seed_offset: IntProperty(default=0)

    # -- Texture Image Props --
    texture_folder: StringProperty(
        name="Folder",
    )

    # -- Color Ramp Props --
    ramp_range_h: FloatProperty(name="Hue ±", default=0.1, min=0.0, max=0.5, update=on_main_update)
    ramp_range_s: FloatProperty(name="Sat ±", default=0.1, min=0.0, max=1.0, update=on_main_update)
    ramp_range_v: FloatProperty(name="Val ±", default=0.1, min=0.0, max=1.0, update=on_main_update)
    ramp_pos_jitter: FloatProperty(name="Pos Jitter", default=0.05, min=0.0, max=1.0, update=on_main_update, description="Randomize position of stops")


class RandomizerSocketProps(PropertyGroup):
    is_updating: BoolProperty(default=False)
    is_locked: BoolProperty(name="Lock", default=False)
    is_initialized: BoolProperty(default=False)

    # Allows re-rolling just this specific socket
    seed_offset: IntProperty(default=0)

    distribution_type: EnumProperty(
        name="Distribution",
        items=[('UNIFORM', "Uniform", ""), ('GAUSSIAN', "Gaussian", ""), ('STEPPED', "Stepped", "")],
        default='UNIFORM', update=on_main_update
    )

    # --- Vector Logic ---
    vector_mode: EnumProperty(
        name="Mode",
        items=[
            ('FREE', "Free", "Independent XYZ"),
            ('UNIFORM', "Uniform Scale", "X controls Y and Z"),
            ('SNAP_90', "Snap 90°", "Quantize to 90 degree steps (PI/2)"),
            ('INTEGER', "Integer", "Round to nearest integer"),
        ],
        default='FREE', update=on_main_update
    )

    min_float: FloatProperty(name="Min", default=0.0, update=on_main_update)
    max_float: FloatProperty(name="Max", default=1.0, update=on_main_update)

    min_vec: FloatVectorProperty(name="Min XYZ", default=(0.0, 0.0, 0.0), size=3, update=on_main_update)
    max_vec: FloatVectorProperty(name="Max XYZ", default=(1.0, 1.0, 1.0), size=3, update=on_main_update)

    min_col: FloatVectorProperty(name="Min", subtype='COLOR', size=4, default=(0, 0, 0, 1), update=update_min_rgb)
    max_col: FloatVectorProperty(name="Max", subtype='COLOR', size=4, default=(1, 0, 0, 1), update=update_max_rgb)

    min_h: FloatProperty(name="H", min=0.0, max=1.0, update=update_min_hsv)
    min_s: FloatProperty(name="S", min=0.0, max=1.0, update=update_min_hsv)
    min_v: FloatProperty(name="V", min=0.0, max=1.0, update=update_min_hsv)
    min_a: FloatProperty(name="A", min=0.0, max=1.0, default=1.0, update=update_min_hsv)

    max_h: FloatProperty(name="H", min=0.0, max=1.0, default=1.0, update=update_max_hsv)
    max_s: FloatProperty(name="S", min=0.0, max=1.0, default=1.0, update=update_max_hsv)
    max_v: FloatProperty(name="V", min=0.0, max=1.0, default=1.0, update=update_max_hsv)
    max_a: FloatProperty(name="A", min=0.0, max=1.0, default=1.0, update=update_max_hsv)


# ------------------------------------------------------------------------
#   UI & Operators
# ------------------------------------------------------------------------

class MRP_UL_NodeList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        node = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row(align=True)
            row.prop(node, "randomizer_enabled", text="")
            row.label(text=f"{node.name} - {node.bl_label or node.type}", icon='NODE')
            # Indicate if node has locked properties
            has_locked = any(s.randomizer_props.is_locked for s in node.inputs if hasattr(s, "randomizer_props"))
            if has_locked:
                row.label(text="", icon='LOCKED')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="")

    def draw_filter(self, context, layout):
        pass

    def filter_items(self, context, data, propname):
        nodes = getattr(data, propname)
        mat = context.object.active_material
        flt_flags = [self.bitflag_filter_item] * len(nodes)
        flt_neworder = []

        if not mat: return flt_flags, flt_neworder

        # 1. Filter by Display Name (Search)
        if mat.randomizer_search:
            search_term = mat.randomizer_search.lower()
            for i, node in enumerate(nodes):
                display_name = (node.label if node.label else node.bl_label).lower()
                if search_term not in display_name:
                    flt_flags[i] &= ~self.bitflag_filter_item

        # 2. Sorting
        items = [(i, node) for i, node in enumerate(nodes)]
        sort_mode = mat.randomizer_sort_by

        if sort_mode == 'NAME':
            items.sort(key=lambda x: (x[1].label if x[1].label else x[1].bl_label).lower())
        elif sort_mode == 'TYPE':
            items.sort(key=lambda x: (x[1].bl_label.lower(), x[1].name.lower()))
        elif sort_mode == 'ACTIVE':
            # FIX: Use 'not enabled' for descending order (True/Enabled at top)
            items.sort(key=lambda x: (not x[1].randomizer_enabled, (x[1].label if x[1].label else x[1].bl_label).lower()))
        elif sort_mode == 'LOCKED':
            def get_lock_score(n): return any(s.randomizer_props.is_locked for s in n.inputs if hasattr(s, "randomizer_props"))
            items.sort(key=lambda x: (not get_lock_score(x[1]), (x[1].label if x[1].label else x[1].bl_label).lower()))

        if mat.randomizer_sort_reverse:
            items.reverse()

        # FIX: The crucial mapping step. flt_neworder[old_index] = new_index
        flt_neworder = [0] * len(nodes)
        for new_idx, (old_idx, _) in enumerate(items):
            flt_neworder[old_idx] = new_idx

        return flt_flags, flt_neworder


class MRP_OT_ApplyRandomization(Operator):
    bl_idname = "mrp.apply_randomization"
    bl_label = "Randomize Now"

    def execute(self, context):
        mat = context.object.active_material
        if mat:
            if mat.randomizer_shuffle_seed: mat.randomizer_seed = random.randint(0, 999999)
            randomize_material(mat, context)
            mat.node_tree.interface_update(context)
        return {'FINISHED'}


class MRP_OT_RandomizeNode(Operator):
    """Randomize only this specific node by changing its local seed offset"""
    bl_idname = "mrp.randomize_node"
    bl_label = "Randomize Node"

    node_name: StringProperty()

    def execute(self, context):
        mat = context.object.active_material
        if not mat: return {'CANCELLED'}

        node = mat.node_tree.nodes.get(self.node_name)
        if node:
            # Update local offset to get new result
            node.randomizer_node_props.seed_offset = random.randint(-99999, 99999)
            randomize_node(node, mat.randomizer_seed)
            mat.node_tree.interface_update(context)

        return {'FINISHED'}


class MRP_OT_RandomizeSocket(Operator):
    """Randomize only this specific property/socket"""
    bl_idname = "mrp.randomize_socket"
    bl_label = "Randomize Property"

    node_name: StringProperty()
    socket_name: StringProperty()

    def execute(self, context):
        mat = context.object.active_material
        if not mat: return {'CANCELLED'}

        node = mat.node_tree.nodes.get(self.node_name)
        if not node: return {'CANCELLED'}

        socket = node.inputs.get(self.socket_name)
        if not socket: return {'CANCELLED'}

        # Change only this socket's seed offset
        socket.randomizer_props.seed_offset = random.randint(-99999, 99999)

        # Apply randomization (logic will pick up the new offset)
        randomize_node(node, mat.randomizer_seed)
        mat.node_tree.interface_update(context)
        return {'FINISHED'}


class MRP_OT_ResetToDefaults(Operator):
    """Reset sockets of enabled nodes to their factory defaults"""
    bl_idname = "mrp.reset_to_defaults"
    bl_label = "Reset Material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        mat = context.object.active_material
        if not mat or not mat.use_nodes:
            return {'CANCELLED'}

        tree = mat.node_tree

        for node in tree.nodes:
            if not getattr(node, "randomizer_enabled", False):
                continue

            if node.type == 'GROUP' and node.node_tree:
                if hasattr(node.node_tree, "interface"):
                    for socket in node.inputs:
                        if socket.is_linked or socket.randomizer_props.is_locked: continue
                        for item in node.node_tree.interface.items_tree:
                            if item.identifier == socket.identifier and hasattr(item, "default_value"):
                                try:
                                    socket.default_value = item.default_value
                                except:
                                    pass
                                break
                continue

            temp_node = None
            try:
                temp_node = tree.nodes.new(node.bl_idname)
                for i, socket in enumerate(node.inputs):
                    if socket.is_linked or socket.randomizer_props.is_locked: continue
                    if i < len(temp_node.inputs):
                        try:
                            socket.default_value = temp_node.inputs[i].default_value
                        except:
                            pass
            except:
                pass
            finally:
                if temp_node: tree.nodes.remove(temp_node)

        mat.node_tree.interface_update(context)
        self.report({'INFO'}, "Material Reset to Socket Defaults")
        return {'FINISHED'}


class MRP_OT_SetSmartLimits(Operator):
    """Set randomization limits based on Node Group definition or Name heuristics"""
    bl_idname = "mrp.set_smart_limits"
    bl_label = "Set Smart Limits"

    node_name: StringProperty()
    socket_name: StringProperty(default="")  # Empty = All sockets in node

    def execute(self, context):
        mat = context.object.active_material
        node = mat.node_tree.nodes.get(self.node_name)
        if not node: return {'CANCELLED'}

        sockets_to_update = []
        if self.socket_name:
            s = node.inputs.get(self.socket_name)
            if s: sockets_to_update.append(s)
        else:
            sockets_to_update = [s for s in node.inputs if s.randomizer_props and not s.is_linked and not s.randomizer_props.is_locked]

        # 1. Try restore from Group Input Storage
        if node.type == 'GROUP':
            apply_group_storage(node, specific_socket=sockets_to_update[0] if len(sockets_to_update) == 1 else None)

        stored_data = {}
        if node.type == 'GROUP' and node.node_tree:
            for n in node.node_tree.nodes:
                if n.type == 'GROUP_INPUT' and "randomizer_limits_json" in n:
                    try:
                        stored_data = json.loads(n["randomizer_limits_json"])
                    except:
                        pass
                    break

        for socket in sockets_to_update:
            if socket.name in stored_data:
                # Already applied by apply_group_storage or we re-apply here to be safe
                s_data = stored_data[socket.name]
                p = socket.randomizer_props
                if "min_f" in s_data: p.min_float = s_data["min_f"]
                if "max_f" in s_data: p.max_float = s_data["max_f"]
                if "min_v" in s_data: p.min_vec = s_data["min_v"]
                if "max_v" in s_data: p.max_vec = s_data["max_v"]
                if "min_hsv" in s_data: p.min_h, p.min_s, p.min_v, p.min_a = s_data["min_hsv"]
                if "max_hsv" in s_data: p.max_h, p.max_s, p.max_v, p.max_a = s_data["max_hsv"]
            else:
                props = socket.randomizer_props
                mn, mx = get_socket_limits(node, socket)

                if socket.type == 'VALUE':
                    props.min_float = mn
                    props.max_float = mx
                elif socket.type == 'VECTOR':
                    props.min_vec = (mn, mn, mn)
                    props.max_vec = (mx, mx, mx)
                elif socket.type == 'RGBA':
                    if mn <= -10000: mn = 0.0
                    if mx >= 10000: mx = 1.0
                    props.min_h, props.min_s, props.min_v = 0.0, 0.0, 0.0
                    props.max_h, props.max_s, props.max_v = 1.0, 1.0, 1.0
                    props.min_a, props.max_a = 1.0, 1.0

        self.report({'INFO'}, f"Limits updated for {self.socket_name if self.socket_name else 'Node'}")
        return {'FINISHED'}


class MRP_OT_StoreLimitsToNode(Operator):
    """Store current randomizer limits as JSON in the Group Input node"""
    bl_idname = "mrp.store_limits_node"
    bl_label = "Store Limits to Node"

    node_name: StringProperty()

    def execute(self, context):
        mat = context.object.active_material
        if not mat: return {'CANCELLED'}

        node = mat.node_tree.nodes.get(self.node_name)
        if not node or node.type != 'GROUP' or not node.node_tree:
            return {'CANCELLED'}

        group_input = None
        for n in node.node_tree.nodes:
            if n.type == 'GROUP_INPUT':
                group_input = n
                break

        if not group_input:
            self.report({'WARNING'}, "Group has no 'Group Input' node.")
            return {'CANCELLED'}

        data = {}
        for socket in node.inputs:
            if socket.type not in {'VALUE', 'VECTOR', 'RGBA'}: continue
            p = socket.randomizer_props
            s_data = {
                "min_f": p.min_float, "max_f": p.max_float,
                "min_v": list(p.min_vec), "max_v": list(p.max_vec),
                "min_hsv": [p.min_h, p.min_s, p.min_v, p.min_a],
                "max_hsv": [p.max_h, p.max_s, p.max_v, p.max_a]
            }
            data[socket.name] = s_data

        group_input["randomizer_limits_json"] = json.dumps(data)
        self.report({'INFO'}, f"Limits saved to Group Input")
        return {'FINISHED'}


class MRP_OT_SaveJSON(Operator):
    bl_idname = "mrp.save_json"
    bl_label = "Save Preset"
    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        mat = context.object.active_material
        if mat: self.filepath = f"{mat.name}.json"
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        mat = context.object.active_material
        if not mat: return {'CANCELLED'}

        data = capture_preset_data(mat)

        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)
        self.report({'INFO'}, "Preset Saved")
        return {'FINISHED'}


class MRP_OT_LoadJSON(Operator):
    bl_idname = "mrp.load_json"
    bl_label = "Load Preset"
    filepath: StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        mat = context.object.active_material
        if not mat: return {'CANCELLED'}
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            apply_preset_data(mat, data)
            self.report({'INFO'}, "Loaded")
        except Exception as e:
            self.report({'ERROR'}, f"Error: {str(e)}")
        return {'FINISHED'}


# --- New Internal Storage Operators ---

class MRP_OT_StorePresetInternal(Operator):
    bl_idname = "mrp.store_preset_internal"
    bl_label = "Store Preset to Mat"
    bl_description = "Save current settings into the Material's custom properties"

    def execute(self, context):
        mat = context.object.active_material
        if not mat: return {'CANCELLED'}

        data = capture_preset_data(mat)
        # Store as string to ensure portability
        mat["mrp_internal_preset_json"] = json.dumps(data)

        self.report({'INFO'}, "Preset Stored in Material")
        return {'FINISHED'}


class MRP_OT_LoadPresetInternal(Operator):
    bl_idname = "mrp.load_preset_internal"
    bl_label = "Load Preset from Mat"
    bl_description = "Load settings from the Material's custom properties"

    @classmethod
    def poll(cls, context):
        mat = context.object.active_material
        return mat and "mrp_internal_preset_json" in mat

    def execute(self, context):
        mat = context.object.active_material
        try:
            data = json.loads(mat["mrp_internal_preset_json"])
            apply_preset_data(mat, data)
            self.report({'INFO'}, "Preset Loaded from Material")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load: {e}")
        return {'FINISHED'}


class MRP_PT_MainPanel(Panel):
    bl_label = "Randomizer Pro"
    bl_idname = "MRP_PT_main_panel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Randomizer"

    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_material and context.object.active_material.use_nodes

    def draw(self, context):
        layout = self.layout
        mat = context.object.active_material

        # Main controls
        row = layout.row(align=True)
        row.prop(mat, "randomizer_auto_update", text="Auto-Update", icon='FILE_REFRESH')
        row.prop(mat, "randomizer_seed", text="Seed")
        layout.separator()

        # External File Presets
        layout.label(text="Presets:")
        row = layout.row(align=True)
        row.operator("mrp.save_json", icon='EXPORT', text="Save File")
        row.operator("mrp.load_json", icon='IMPORT', text="Load File")

        # Internal Material Presets
        row = layout.row(align=True)
        row.operator("mrp.store_preset_internal", icon='MEMORY', text="Store to Material")
        row.operator("mrp.load_preset_internal", icon='RECOVER_LAST', text="Load from Material")

        layout.separator()

        # Randomization actions
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("mrp.apply_randomization", icon='NODETREE')
        row.operator("mrp.reset_to_defaults", icon='LOOP_BACK', text="")
        row = layout.row(align=True)
        row.prop(mat, "randomizer_shuffle_seed", text="New Seed", toggle=True, icon='DRIVER')
        layout.separator()

        # Filter & Sort
        row = layout.row(align=True)
        row.prop(mat, "randomizer_search", text="", icon='VIEWZOOM')
        row.prop(mat, "randomizer_sort_reverse", text="", icon='SORT_ASC' if not mat.randomizer_sort_reverse else 'SORT_DESC')
        row = layout.row(align=True)
        row.prop(mat, "randomizer_sort_by", expand=True)

        # Node List
        row = layout.row()
        row.template_list("MRP_UL_NodeList", "", mat.node_tree, "nodes", mat, "randomizer_active_node_index")

        if mat.node_tree.nodes and mat.randomizer_active_node_index >= 0:
            try:
                node = mat.node_tree.nodes[mat.randomizer_active_node_index]
            except IndexError:
                return

            box = layout.box()
            # Node Header with Randomize Button
            header = box.row()
            header.label(text=f"Settings: {node.name}", icon='NODE')

            if getattr(node, "randomizer_enabled", False):
                op_rand = header.operator("mrp.randomize_node", text="", icon='FILE_REFRESH')
                op_rand.node_name = node.name

            if not getattr(node, "randomizer_enabled", False):
                box.label(text="Enable checkbox above", icon='INFO')
                return

            # Property Search/Sort UI
            row = box.row(align=True)
            row.prop(mat, "randomizer_prop_search", text="", icon='VIEWZOOM')
            row.prop(mat, "randomizer_prop_sort_reverse", text="", icon='SORT_ASC' if not mat.randomizer_prop_sort_reverse else 'SORT_DESC')
            row = box.row(align=True)
            row.prop(mat, "randomizer_prop_sort_by", expand=True)
            box.separator()

            # --- Special Node Settings ---
            node_props = node.randomizer_node_props

            if node.type == 'TEX_IMAGE':
                box.label(text="Texture Swapping", icon='IMAGE_DATA')
                box.prop(node_props, "texture_folder", text="")
                box.separator()

            elif node.type == 'VALTORGB':
                box.label(text="Color Ramp Chaos", icon='COLOR')
                box.prop(node_props, "ramp_pos_jitter", slider=True)
                r = box.row(align=True)
                r.prop(node_props, "ramp_range_h")
                r.prop(node_props, "ramp_range_s")
                r.prop(node_props, "ramp_range_v")
                box.separator()

            elif node.type == 'GROUP':
                # Global Reset Limits Button for Groups
                op = box.operator("mrp.set_smart_limits", text="Reset All Limits from Group", icon='FILE_REFRESH')
                op.node_name = node.name

                # Store Limits to Node Property
                op_store = box.operator("mrp.store_limits_node", text="Store Limits to Node Prop", icon='DISK_DRIVE')
                op_store.node_name = node.name

                box.separator()

            # --- Sockets Filtering & Sorting Logic ---
            valid_sockets = []
            for socket in node.inputs:
                if socket.is_linked or socket.type not in {'VALUE', 'VECTOR', 'RGBA'}: continue
                valid_sockets.append(socket)

            # Filter
            if mat.randomizer_prop_search:
                search_term = mat.randomizer_prop_search.lower()
                valid_sockets = [s for s in valid_sockets if search_term in s.name.lower()]

            # Sort
            sort_mode = mat.randomizer_prop_sort_by
            if sort_mode == 'NAME':
                valid_sockets.sort(key=lambda s: s.name.lower())
            elif sort_mode == 'TYPE':
                valid_sockets.sort(key=lambda s: (s.type, s.name.lower()))
            elif sort_mode == 'LOCKED':
                # Locked items first (Locked=True), so use not is_locked for ascending default (False before True)
                valid_sockets.sort(key=lambda s: (not s.randomizer_props.is_locked, s.name.lower()))

            if mat.randomizer_prop_sort_reverse:
                valid_sockets.reverse()

            # --- Sockets Drawing ---
            for socket in valid_sockets:
                socket_box = box.box()
                col = socket_box.column(align=True)

                # Header Row
                h_row = col.row(align=True)

                # 1. Label on Left
                h_row.label(text=socket.name)

                # 2. Controls on Right
                props = socket.randomizer_props

                # Randomize Single Button
                op_rand_sock = h_row.operator("mrp.randomize_socket", text="", icon='FILE_REFRESH')
                op_rand_sock.node_name = node.name
                op_rand_sock.socket_name = socket.name

                # Reset Limits Button
                op_smart = h_row.operator("mrp.set_smart_limits", text="", icon='LOOP_BACK')
                op_smart.node_name = node.name
                op_smart.socket_name = socket.name

                # Lock Button (Moved to far right)
                h_row.prop(props, "is_locked", icon='LOCKED' if props.is_locked else 'UNLOCKED', text="")

                if props.is_locked: continue
                col.separator()
                col.prop(props, "distribution_type", text="")

                if socket.type == 'VALUE':
                    r = col.row(align=True)
                    r.prop(props, "min_float");
                    r.prop(props, "max_float")
                elif socket.type == 'VECTOR':
                    col.prop(props, "vector_mode", text="")
                    col.prop(props, "min_vec");
                    col.prop(props, "max_vec")
                elif socket.type == 'RGBA':
                    r1 = col.column(align=True);
                    r1.label(text="Min HSV:")
                    hsv1 = r1.row(align=True);
                    hsv1.prop(props, "min_h");
                    hsv1.prop(props, "min_s");
                    hsv1.prop(props, "min_v");
                    hsv1.prop(props, "min_a")
                    r1.prop(props, "min_col", text="")
                    col.separator()
                    r2 = col.column(align=True);
                    r2.label(text="Max HSV:")
                    hsv2 = r2.row(align=True);
                    hsv2.prop(props, "max_h");
                    hsv2.prop(props, "max_s");
                    hsv2.prop(props, "max_v");
                    hsv2.prop(props, "max_a")
                    r2.prop(props, "max_col", text="")


classes = (
    RandomizerNodeProps,
    RandomizerSocketProps,
    MRP_UL_NodeList,
    MRP_OT_ApplyRandomization,
    MRP_OT_RandomizeNode,
    MRP_OT_RandomizeSocket,
    MRP_OT_ResetToDefaults,
    MRP_OT_SetSmartLimits,
    MRP_OT_StoreLimitsToNode,
    MRP_OT_SaveJSON,
    MRP_OT_LoadJSON,
    MRP_OT_StorePresetInternal,
    MRP_OT_LoadPresetInternal,
    MRP_PT_MainPanel,
)


def register():
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.NodeSocket.randomizer_props = PointerProperty(type=RandomizerSocketProps)
    bpy.types.Node.randomizer_node_props = PointerProperty(type=RandomizerNodeProps)
    bpy.types.Node.randomizer_enabled = BoolProperty(name="Randomize", default=False, update=update_node_enable)
    bpy.types.Material.randomizer_active_node_index = IntProperty()
    bpy.types.Material.randomizer_seed = IntProperty(name="Seed", default=0, update=on_main_update)
    bpy.types.Material.randomizer_auto_update = BoolProperty(name="Auto Update", default=False)
    bpy.types.Material.randomizer_shuffle_seed = BoolProperty(name="Shuffle Seed", default=False)

    # Node List Filter & Sort Properties
    bpy.types.Material.randomizer_search = StringProperty(name="Search", description="Filter nodes by name")
    bpy.types.Material.randomizer_sort_by = EnumProperty(
        name="Sort By",
        items=[
            ('NAME', "Name", ""),
            ('TYPE', "Type", ""),
            ('ACTIVE', "Active", ""),
            ('LOCKED', "Locked", "")
        ],
        default='NAME'
    )
    bpy.types.Material.randomizer_sort_reverse = BoolProperty(name="Reverse", default=False)

    # Property (Socket) List Filter & Sort Properties
    bpy.types.Material.randomizer_prop_search = StringProperty(name="Search Props", description="Filter properties by name")
    bpy.types.Material.randomizer_prop_sort_by = EnumProperty(
        name="Sort Props By",
        items=[
            ('NAME', "Name", ""),
            ('TYPE', "Type", ""),
            ('LOCKED', "Locked", "")
        ],
        default='NAME'
    )
    bpy.types.Material.randomizer_prop_sort_reverse = BoolProperty(name="Reverse", default=False)


def unregister():
    for cls in reversed(classes): bpy.utils.unregister_class(cls)
    del bpy.types.NodeSocket.randomizer_props
    del bpy.types.Node.randomizer_node_props
    del bpy.types.Node.randomizer_enabled
    del bpy.types.Material.randomizer_active_node_index
    del bpy.types.Material.randomizer_seed
    del bpy.types.Material.randomizer_auto_update
    del bpy.types.Material.randomizer_shuffle_seed
    del bpy.types.Material.randomizer_search
    del bpy.types.Material.randomizer_sort_by
    del bpy.types.Material.randomizer_sort_reverse
    del bpy.types.Material.randomizer_prop_search
    del bpy.types.Material.randomizer_prop_sort_by
    del bpy.types.Material.randomizer_prop_sort_reverse


if __name__ == "__main__": register()