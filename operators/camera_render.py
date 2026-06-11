import bpy


class BULLETTIME_OT_render_cameras(bpy.types.Operator):
    bl_idname = "bullettime.camera_render"
    bl_label = "Render Cameras"

    def execute(self, context):
        return {'FINISHED'}


def register():
    bpy.utils.register_class(BULLETTIME_OT_render_cameras)


def unregister():
    bpy.utils.unregister_class(BULLETTIME_OT_render_cameras)