"""Scene properties for the Bullet Time add-on."""

import bpy


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

    density: bpy.props.IntProperty(
        name="Density",
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

    front_axis: bpy.props.EnumProperty(
        name="Front Axis",
        items=[
            ("X", "X", "Positive X is forward"),
            ("-X", "-X", "Negative X is forward"),
            ("Y", "Y", "Positive Y is forward"),
            ("-Y", "-Y", "Negative Y is forward"),
        ],
        default="Y",
        description="Which axis defines the subject's forward direction",
    )

    front_offset: bpy.props.FloatProperty(
        name="Rotation Offset",
        default=0.0,
        min=-360.0,
        max=360.0,
        subtype="ANGLE",
        description="Additional rotation offset for front direction",
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

    last_generated_count: bpy.props.IntProperty(
        name="Generated Points",
        default=0,
        min=0,
        description="Number of camera points generated in the last run",
    )

    last_valid_count: bpy.props.IntProperty(
        name="Valid Points",
        default=0,
        min=0,
        description="Number of camera points rendered in the last run",
    )

    last_pruned_count: bpy.props.IntProperty(
        name="Pruned Points",
        default=0,
        min=0,
        description="Number of camera points removed by pruning in the last run",
    )


def register():
    bpy.utils.register_class(BULLETTIME_PG_props)
    bpy.types.Scene.bullet_time_props = bpy.props.PointerProperty(type=BULLETTIME_PG_props)


def unregister():
    del bpy.types.Scene.bullet_time_props
    bpy.utils.unregister_class(BULLETTIME_PG_props)
