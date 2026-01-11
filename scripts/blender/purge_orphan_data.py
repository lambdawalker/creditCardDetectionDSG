import bpy





def purge_orphan_data():
    orphan_data_types = {
        "meshes": bpy.data.meshes,
        "materials": bpy.data.materials,
        "textures": bpy.data.textures,
        "images": bpy.data.images,
        "curves": bpy.data.curves,
        "lamps": bpy.data.lights,
        "cameras": bpy.data.cameras,
        "collections": bpy.data.collections,
        "armatures": bpy.data.armatures,
        "actions": bpy.data.actions,
        "node_groups": bpy.data.node_groups,
        "particles": bpy.data.particles,
        "fonts": bpy.data.fonts,
        "speakers": bpy.data.speakers,
        "metaballs": bpy.data.metaballs,
        "lattices": bpy.data.lattices,
        "hair_curves": bpy.data.hair_curves,
        "pointclouds": bpy.data.pointclouds,
        "volumes": bpy.data.volumes,
        "gpencil": bpy.data.grease_pencils,
        "brushes": bpy.data.brushes,
        "paint_curves": bpy.data.paint_curves,
        "palettes": bpy.data.palettes,
        "movieclips": bpy.data.movieclips,
        "masks": bpy.data.masks,
        "line_styles": bpy.data.linestyles,
    }

    # Iterate over each data type and remove orphan data
    for data_type, data_blocks in orphan_data_types.items():
        orphan_data = [block for block in data_blocks if block.users == 0]
        for block in orphan_data:
            try:
                data_blocks.remove(block)
            except:
                pass
