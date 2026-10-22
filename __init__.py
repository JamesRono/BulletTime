from . import properties
from .operators import camera_render, preview_points
from .panels import ui


def register():
    properties.register()
    ui.register()
    camera_render.register()
    preview_points.register()


def unregister():
    preview_points.unregister()
    camera_render.unregister()
    ui.unregister()
    properties.unregister()
