"""Bullet Time — procedural multi-angle rendering for Blender."""

import bpy

from . import properties
from .panels import ui
from .operators import camera_render, preview_points


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
