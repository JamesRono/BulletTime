"""Render operator — scatter camera points and batch-render the subject."""

import os

import bpy

from ..adapters.render_pipeline import RenderPipeline
from ..engine.geometry import scatter_camera_points


class BULLETTIME_OT_render_cameras(bpy.types.Operator):
    """Scatter camera points around the subject and render each one to disk."""

    bl_idname = "bullettime.camera_render"
    bl_label = "Render"
    bl_options = {"REGISTER"}  # noqa: RUF012

    _TEMP_CAMERA_NAME = "BulletTime_Camera"

    def execute(self, context): # type: ignore[override]
        pipeline = RenderPipeline(context)

        scene = context.scene
        props = scene.bullet_time_props

        if props.subject is None:
            self.report({"ERROR"}, "Select a subject object before rendering.")
            return {"CANCELLED"}

        subject = props.subject

        #Pruning for valid points would happen here, but that won't be in the MVP
        generated_points = scatter_camera_points(context, subject, props)

        if not generated_points:
            pipeline.update_pipeline_stats(props, 0, 0, 0)
            self.report({"ERROR"}, "No camera points were generated.")
            return {"CANCELLED"}

        # This distinction will be useful for later once I add pruning.
        # That's when there will be a difference between generated and used points
        render_points = generated_points
        pipeline.update_pipeline_stats(
            props,
            len(render_points),
            len(render_points),
            0,
        )

        # Make the output file
        output_dir = bpy.path.abspath(props.output_dir)
        os.makedirs(output_dir, exist_ok=True)

        pipeline.execute(render_points, props)

        self.report(
            {"INFO"},
            (
                f"Rendered {len(render_points)} image(s) from "
                f"{len(generated_points)} generated point(s) to {output_dir}"
            ),
        )
        return {"FINISHED"}



def register():
    bpy.utils.register_class(BULLETTIME_OT_render_cameras)


def unregister():
    bpy.utils.unregister_class(BULLETTIME_OT_render_cameras)
