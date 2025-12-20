from scripts.log.blender_light_log import build_light_log


class CardLog:
    def __init__(self):
        self.paint_order = []
        self.fields = []
        self.lights = []
        self.palette = None
        self.color_selection = None
        self.color_profile = ""

    def log_light(self, light):
        light_log = build_light_log(light)

    def to_dict(self):
        return {
            'color_profile': self.color_profile,
            'paint_order': self.paint_order,
            'color_selection': self.color_selection,
            'palette': self.palette.to_dict(),
            'fields': self.fields,
        }
