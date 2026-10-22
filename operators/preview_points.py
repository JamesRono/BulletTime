"""Make a preview of the camera points as empties in the viewport."""

import bpy

from ..adapters.preview_generated_points import (
    PREVIEW_COLLECTION,
    clear_preview_empties,
    create_point_empties,
)
from ..engine.geometry import scatter_camera_points


class BULLETTIME_OT_preview_points(bpy.types.Operator):
    """Scatter camera points and show them as arrow empties in the viewport."""

    bl_idname = "bullettime.preview_points"
    bl_label = "Preview Camera Points"
    bl_description = "Scatter points and show them as empties for debugging"
    bl_options = {"REGISTER", "UNDO"} # noqa: RUF012

    def execute(self, context): # type: ignore[override]
        props = context.scene.bullet_time_props

        if props.subject is None:
            self.report({"ERROR"}, "Select a subject object before previewing points.")
            return {"CANCELLED"}

        points = scatter_camera_points(context, props.subject, props)
        if not points:
            self.report({"ERROR"}, "No camera points were generated.")
            return {"CANCELLED"}

        count = create_point_empties(context, points)
        props.last_generated_count = count
        props.last_valid_count = count
        props.last_pruned_count = 0

        self.report(
            {"INFO"},
            f"Created {count} preview empty(s) in the '{PREVIEW_COLLECTION}' collection.",
        )
        return {"FINISHED"}


class BULLETTIME_OT_clear_preview_points(bpy.types.Operator):
    """Remove all preview empties created by Bullet Time."""

    bl_idname = "bullettime.clear_preview_points"
    bl_label = "Clear Preview Empties"
    bl_description = "Remove all Bullet Time preview empties"
    bl_options = {"REGISTER", "UNDO"} # noqa: RUF012

    def execute(self, context): # type: ignore[override]
        removed = clear_preview_empties()
        if removed == 0:
            self.report({"INFO"}, "No preview empties to remove.")
        else:
            self.report({"INFO"}, f"Removed {removed} preview empty(s).")
        return {"FINISHED"}


def register():
    bpy.utils.register_class(BULLETTIME_OT_preview_points)
    bpy.utils.register_class(BULLETTIME_OT_clear_preview_points)


def unregister():
    bpy.utils.unregister_class(BULLETTIME_OT_clear_preview_points)
    bpy.utils.unregister_class(BULLETTIME_OT_preview_points)
