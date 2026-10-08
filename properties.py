"""Scene properties for the Bullet Time add-on."""

import bpy

PRESETS = {
    "DRAFT": {"resolution_x": 640, "resolution_y": 360, "samples": 32},
    "MEDIUM": {"resolution_x": 1280, "resolution_y": 720, "samples": 128},
    "HIGH": {"resolution_x": 1920, "resolution_y": 1080, "samples": 512},
}

def subject_poll(self, obj):
    """Limit the subject picker to renderable geometry types."""
    return obj.type in {"MESH", "CURVE", "SURFACE", "META", "FONT", "VOLUME"}


class BULLETTIME_PG_props(bpy.types.PropertyGroup):
    """User-facing settings stored on the scene."""

    subject: bpy.props.PointerProperty(
        name="Subject",
        type=bpy.types.Object,
        description="The object to scatter cameras around",
        poll=subject_poll,
    )

    focal_length: bpy.props.FloatProperty(
        name="Focal Length",
        default=50.0,
        min=1.0,
        max=4000.0,
        unit="CAMERA",
        description="Focal length of the render camera",
    )

    aperture: bpy.props.FloatProperty(
        name="Aperture",
        default=8.0,
        min=0.1,
        max=64.0,
        description="F-stop aperture of the render camera",
    )

    radius: bpy.props.FloatProperty(
        name="Radius",
        default=5.0,
        min=0.1,
        description="Distance from subject to place cameras",
    )

    count: bpy.props.IntProperty(
        name="Count",
        default=8,
        min=1,
        max=100,
        description="Number of camera positions to generate",
    )

    path_shape: bpy.props.EnumProperty(
        name="Path Shape",
        items=[
            ("ARC", "Arc", "Cameras along a partial arc"),
            ("SPHERE", "Sphere", "Cameras distributed over a sphere"),
            ("CIRCLE", "Circle", "Cameras along a full circle"),
        ],
        default="ARC",
        description="Distribution shape for camera positions",
    )

    arc_start_angle: bpy.props.FloatProperty(
        name="Start Angle",
        default=0.0,
        min=-360.0,
        max=360.0,
        subtype="ANGLE",
        description="Start angle of the arc in degrees",
    )

    arc_end_angle: bpy.props.FloatProperty(
        name="End Angle",
        default=180.0,
        min=-360.0,
        max=360.0,
        subtype="ANGLE",
        description="End angle of the arc in degrees",
    )

    elevation: bpy.props.FloatProperty(
        name="Elevation",
        default=0.0,
        min=-90.0,
        max=90.0,
        subtype="ANGLE",
        description="Elevation angle of the camera path",
    )

    quality_preset: bpy.props.EnumProperty(
        name="Quality",
        items=[
            ("DRAFT", "Draft", "640x360, 32 samples"),
            ("MEDIUM", "Medium", "1280x720, 128 samples"),
            ("HIGH", "High", "1920x1080, 512 samples"),
        ],
        default="MEDIUM",
        description="Render quality preset",
    )

    output_dir: bpy.props.StringProperty(
        name="Output Directory",
        default="//renders/",
        subtype="DIR_PATH",
        description="Directory where rendered images are saved",
    )


def register():
    bpy.utils.register_class(BULLETTIME_PG_props)
    bpy.types.Scene.bullet_time_props = bpy.props.PointerProperty(type=BULLETTIME_PG_props)


def unregister():
    del bpy.types.Scene.bullet_time_props
    bpy.utils.unregister_class(BULLETTIME_PG_props)
