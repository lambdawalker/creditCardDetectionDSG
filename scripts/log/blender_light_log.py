def build_light_log(light):
    energy = light.data.energy

    try:
        temperature = light.data.node_tree.nodes.get("Blackbody").inputs[0].default_value
    except:
        temperature = None

    euler = light.rotation_euler
    location = light.location

    return {
        "energy": energy,
        "temperature": temperature,
        "rotation_euler": (euler.x, euler.y, euler.z),
        "location": (location.x, location.y, location.z)
    }
