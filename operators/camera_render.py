"""Render operator — scatter camera points and batch-render the subject."""

import os

import bpy
from mathutils import Matrix

from ..utils.naming import make_filepath
from ..utils.pipeline import reset_pipeline_state, store_generated_points
from ..engine.scatter import scatter_camera_points
from ..properties import PRESETS


class BULLETTIME_OT_render_cameras(bpy.types.Operator):
    """Scatter camera points around the subject and render each one to disk."""

    bl_idname = "bullettime.camera_render"
    bl_label = "Render"
    bl_options = {"REGISTER"}

    _TEMP_CAMERA_NAME = "BulletTime_Camera"

    def execute(self, context):
        scene = context.scene
        props = scene.bullet_time_props

        if props.subject is None:
            self.report({"ERROR"}, "Select a subject object before rendering.")
            return {"CANCELLED"}

        subject = props.subject

        reset_pipeline_state()

        generated_points = scatter_camera_points(context, subject, props)
        store_generated_points(generated_points)

        if not generated_points:
            self._update_pipeline_stats(props, 0, 0, 0)
            self.report({"ERROR"}, "No camera points were generated.")
            return {"CANCELLED"}

        render_points = generated_points
        self._update_pipeline_stats(
            props,
            len(render_points),
            len(render_points),
            0,
        )

        # Make the output file
        output_dir = bpy.path.abspath(props.output_dir)
        os.makedirs(output_dir, exist_ok=True)

        saved = self._save_render_state(scene)
        camera = self._get_or_create_camera(context)

        try:
            self._apply_camera_settings(camera, props)
            self._apply_quality_settings(scene, props.quality_preset)

            wm = context.window_manager
            wm.progress_begin(0, len(render_points))

            for index, point in enumerate(render_points):
                rotation = point.direction.to_track_quat("-Z", "Y").to_matrix().to_4x4()
                camera.matrix_world = Matrix.Translation(point.location) @ rotation

                filepath = make_filepath(
                    output_dir, subject.name, point.azimuth, point.elevation
                )
                scene.render.filepath = filepath
                scene.camera = camera

                bpy.ops.render.render(write_still=True)
                wm.progress_update(index + 1)

            wm.progress_end()
        finally:
            self._restore_render_state(scene, saved)

        self.report(
            {"INFO"},
            (
                f"Rendered {len(render_points)} image(s) from "
                f"{len(generated_points)} generated point(s) to {output_dir}"
            ),
        )
        return {"FINISHED"}

    def _update_pipeline_stats(self, props, generated, valid, pruned):
        """Write run statistics back to the scene properties."""
        props.last_generated_count = generated
        props.last_valid_count = valid
        props.last_pruned_count = pruned

    def _get_or_create_camera(self, context):
        """Return the temporary render camera, creating it if needed."""
        camera_obj = bpy.data.objects.get(self._TEMP_CAMERA_NAME)
        if camera_obj is None:
            camera_data = bpy.data.cameras.new(self._TEMP_CAMERA_NAME)
            camera_obj = bpy.data.objects.new(self._TEMP_CAMERA_NAME, camera_data)
            context.scene.collection.objects.link(camera_obj)
        return camera_obj

    def _apply_camera_settings(self, camera_obj, props):
        """Apply focal length and depth-of-field settings to the render camera."""
        camera_obj.data.lens = props.focal_length
        if hasattr(camera_obj.data, "dof"):
            camera_obj.data.dof.aperture_fstop = props.aperture

    def _apply_quality_settings(self, scene, preset):
        """Apply resolution, format, and sample count from a quality preset."""



        settings = PRESETS.get(preset, PRESETS["MEDIUM"])
        scene.render.resolution_x = settings["resolution_x"]
        scene.render.resolution_y = settings["resolution_y"]
        scene.render.image_settings.file_format = "PNG"

        engine = scene.render.engine
        samples = settings["samples"]
        if engine == "CYCLES":
            scene.cycles.samples = samples
        elif engine == "BLENDER_EEVEE":
            scene.eevee.taa_render_samples = samples
        elif engine == "BLENDER_EEVEE_NEXT":
            scene.eevee.taa_render_samples = samples

    def _restore_render_state(self, scene, state):
        """Restore render settings saved before the batch started."""
        scene.camera = state["camera"]
        scene.render.resolution_x = state["resolution_x"]
        scene.render.resolution_y = state["resolution_y"]
        scene.render.filepath = state["filepath"]
        scene.render.image_settings.file_format = state["file_format"]

        engine = state["engine"]
        if "samples" in state:
            if engine == "CYCLES":
                scene.cycles.samples = state["samples"]
            elif engine in {"BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"}:
                scene.eevee.taa_render_samples = state["samples"]


def register():
    bpy.utils.register_class(BULLETTIME_OT_render_cameras)


def unregister():
    bpy.utils.unregister_class(BULLETTIME_OT_render_cameras)
