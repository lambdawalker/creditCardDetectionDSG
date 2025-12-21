import random


def randomize_light_properties(light, intensity_range=None, color_range=None, temperature_range=None):
    # Randomize intensity if range is provided
    intensity = None

    if intensity_range is not None:
        intensity = random.uniform(intensity_range[0], intensity_range[1])
        light.data.energy = intensity

    # Randomize color if range is provided
    if color_range is not None:
        color = (
            random.uniform(color_range[0][0], color_range[1][0]),
            random.uniform(color_range[0][1], color_range[1][1]),
            random.uniform(color_range[0][2], color_range[1][2])
        )
        light.data.color = color

    # Randomize temperature if range is provided
    if temperature_range is not None:
        light.data.use_nodes = True
        nodes = light.data.node_tree.nodes
        blackbody_node = nodes.get("Blackbody")

        if blackbody_node is None:
            blackbody_node = nodes.new(type='ShaderNodeBlackbody')

        output_node = nodes.get("Emission")
        if output_node is None:
            output_node = nodes.get("Emission")

        if not light.data.node_tree.links:
            light.data.node_tree.links.new(blackbody_node.outputs[0], output_node.inputs[0])

        temperature = random.uniform(temperature_range[0], temperature_range[1])
        blackbody_node.inputs[0].default_value = temperature

    return intensity
