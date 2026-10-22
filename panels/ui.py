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
        box.prop(props, "count")

        if props.path_shape == "ARC":
            box.prop(props, "arc_start_angle")
            box.prop(props, "arc_end_angle")
            box.prop(props, "elevation")

        elif props.path_shape == "CIRCLE":
            self.arc_start_angle = 0.0
            self.arc_end_angle = 360.0
            box.prop(props, "elevation")


        layout.separator()

        box = layout.box()
        box.label(text="Output", icon="FILE_IMAGE")
        box.prop(props, "quality_preset")
        box.prop(props, "output_dir")

        layout.separator()

        box = layout.box()
        box.label(text="Preview", icon="GHOST_DISABLED")
        row = box.row(align=True)
        row.operator("bullettime.preview_points", text="Preview Camera Points", icon="EMPTY_ARROWS")
        row.operator("bullettime.clear_preview_points", text="", icon="TRASH")

        layout.separator()

        col = layout.column(align=True)
        col.scale_y = 3
        col.operator("bullettime.camera_render", text="Render", icon="RENDER_STILL")


def register():
    bpy.utils.register_class(BULLETTIME_PT_main_panel)


def unregister():
    bpy.utils.unregister_class(BULLETTIME_PT_main_panel)
