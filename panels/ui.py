import bpy

class BULLETTIME_PT_main_panel(bpy.types.Panel):
    """Main UI panel"""

    bl_label = "Bullet Time"
    bl_idname = "BULLETTIME_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bullet Time"

    def draw(self, context):

        layout = self.layout
        props = context.scene.bullet_time_props
        box = layout.box()

        box.label(text="Subject", icon="OBJECT_DATA")
        box.prop(props, "subject", text="")

        layout.separator()

        box = layout.box()
        box.label(text="Camera", icon="OUTLINER_OB_CAMERA")
        box.prop(props, "focal_length")
        box.prop(props, "aperture")

        layout.separator()

        box = layout.box()
        box.label(text="Camera Path", icon="CURVE_PATH")
        box.prop(props, "path_shape")
        box.prop(props, "radius")
        box.prop(props, "density")

        if props.path_shape == "ARC":
            box.prop(props, "arc_start_angle")
            box.prop(props, "arc_end_angle")
            box.prop(props, "elevation")

        layout.separator()

        box = layout.box()
        box.label(text="Subject Facing", icon="ORIENTATION_GIMBAL")
        box.prop(props, "front_axis")
        box.prop(props, "front_offset")

        layout.separator()

        box = layout.box()
        box.label(text="Output", icon="FILE_IMAGE")
        box.prop(props, "quality_preset")
        box.prop(props, "output_dir")

        if props.last_generated_count > 0:
            layout.separator()
            box = layout.box()
            box.label(text="Last Run", icon="INFO")
            col = box.column(align=True)
            col.label(text=f"Generated: {props.last_generated_count}")
            col.label(text=f"Rendered: {props.last_valid_count}")

        layout.separator()

        box = layout.box()
        box.label(text="Debug", icon="EMPTY_AXIS")
        row = box.row(align=True)
        row.operator("bullettime.preview_points", text="Preview Camera Points", icon="EMPTY_ARROWS")
        row.operator("bullettime.clear_preview_points", text="", icon="TRASH")

        layout.separator()

        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("bullettime.camera_render", text="Render", icon="RENDER_STILL")


def register():
    bpy.utils.register_class(BULLETTIME_PT_main_panel)


def unregister():
    bpy.utils.unregister_class(BULLETTIME_PT_main_panel)
