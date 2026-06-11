import bpy


class BULLETTIME_PT_main_panel(bpy.types.Panel):
    bl_label = "Bullet Time"
    bl_idname = "BULLETTIME_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Bullet Time"

    def draw(self, context):
        layout = self.layout
        props = context.scene.bullet_time_props

        # Subject
        layout.label(text="Subject")
        layout.prop(props, "subject", text="")

        layout.separator()

        # Camera Settings
        layout.label(text="Camera")
        layout.prop(props, "focal_length")
        layout.prop(props, "aperture")

        layout.separator()

        # Scatter Settings
        layout.label(text="Scatter")
        layout.prop(props, "radius")
        layout.prop(props, "density")
        layout.prop(props, "path_shape")

        # Conditional fields based on path shape
        if props.path_shape == "ARC":
            layout.prop(props, "arc_start_angle")
            layout.prop(props, "arc_end_angle")
        elif props.path_shape == "CIRCLE":
            layout.prop(props, "elevation")

        layout.separator()

        # Front direction
        layout.label(text="Subject Facing")
        layout.prop(props, "front_axis")
        layout.prop(props, "front_offset")

        layout.separator()

        # Operators
        layout.operator("bullettime.camera_scatter", text="Scatter Cameras")
        layout.operator("bullettime.camera_prune", text="Prune Cameras")
        layout.operator("bullettime.camera_render", text="Render")


def register():
    bpy.utils.register_class(BULLETTIME_PT_main_panel)


def unregister():
    bpy.utils.unregister_class(BULLETTIME_PT_main_panel)