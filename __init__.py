
import bpy
from . import properties
from .panels import ui
from .operators import camera_prune, camera_render, camera_scatter


def register():
    properties.register()
    ui.register()
    camera_prune.register()
    camera_render.register()
    camera_scatter.register()

def unregister():
    ui.unregister()
    properties.unregister()
    camera_prune.unregister()
    camera_render.unregister()
    camera_scatter.unregister()
    