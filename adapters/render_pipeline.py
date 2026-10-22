"""Manages scene state, quality settings, camera creation, and batch execution."""

import bpy
from mathutils import Matrix

from ..engine.naming import make_filepath
from ..properties import PRESETS


class RenderPipeline:

    def __init__(self, context):
        self.context = context
        self._state_backup = {}

    def save_render_state(self):
        """Preserves initial scene state before render modifications."""
        scene = self.context.scene
        state = {
            "camera": scene.camera,
            "resolution_x": scene.render.resolution_x,
            "resolution_y": scene.render.resolution_y,
            "filepath": scene.render.filepath,
            "file_format": scene.render.image_settings.file_format,
            "engine": scene.render.engine,
        }

        engine = scene.render.engine
        if engine == "CYCLES":
            state["samples"] = scene.cycles.samples
        elif engine in {"BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"}:
            state["samples"] = scene.eevee.taa_render_samples

        return state

    def restore_render_state(self):
        """Restores modified scene settings after completion."""
        if not self._state_backup:
                    return
        scene = self.context.scene
        state = self._state_backup

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

    def apply_quality_settings(self, preset):
        """Sets scene resolution and sample counts using self.context."""
        scene = self.context.scene

        # Look up the preset, falling back to MEDIUM if something goes wrong
        settings = PRESETS.get(preset, PRESETS.get("MEDIUM", {}))

        if not settings:
            return

        # Apply resolution and percentage settings
        scene.render.resolution_x = settings.get("resolution_x", 1920)
        scene.render.resolution_y = settings.get("resolution_y", 1080)
        scene.render.resolution_percentage = settings.get("resolution_percentage", 100)

        # Apply engine-specific sample counts (Cycles or Eevee)
        engine = scene.render.engine
        if "samples" in settings:
            if engine == "CYCLES":
                scene.cycles.samples = settings["samples"]
            elif engine in {"BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"}:
                scene.eevee.taa_render_samples = settings["samples"]


    def update_pipeline_stats(self, props, generated, valid, pruned):
        """Write run statistics back to the scene properties."""
        props.last_generated_count = generated
        props.last_valid_count = valid
        props.last_pruned_count = pruned

    def get_or_create_camera(self, camera_name="BulletTime_Camera"):
        """Retrieves or creates a temporary camera for rendering."""
        scene = self.context.scene
        camera_obj = bpy.data.objects.get(camera_name)
        if camera_obj is None:
            cam_data = bpy.data.cameras.new(camera_name)
            camera_obj = bpy.data.objects.new(camera_name, cam_data)
            scene.collection.objects.link(camera_obj)
        scene.camera = camera_obj
        return camera_obj

    def apply_camera_settings(self, camera_obj, props):
        camera_obj.data.lens = props.focal_length
        if hasattr(camera_obj.data, "dof"):
            camera_obj.data.dof.aperture_fstop = props.aperture

    def execute(self, render_points, props):
        """Runs the batch render loop across all generated camera points."""
        scene = self.context.scene

        # 1. Setup camera & apply quality
        camera = self.get_or_create_camera()
        self.apply_camera_settings(camera, props)

        # 2. Backup initial state
        self.save_render_state()

        wm = self.context.window_manager

        try:
            self.apply_quality_settings(props.quality_preset)
            wm.progress_begin(0, len(render_points))

            # 3. Grab output_dir and subject directly from props / context
            output_dir = props.output_dir
            subject = props.subject

            # 4. The Render Loop
            for index, point in enumerate(render_points):
                rotation = point.direction.to_track_quat("-Z", "Y").to_matrix().to_4x4()
                camera.matrix_world = Matrix.Translation(tuple(point.location)) @ rotation  # type: ignore

                filepath = make_filepath(
                    output_dir, subject.name, point.azimuth, point.elevation
                )
                scene.render.filepath = filepath
                scene.camera = camera

                bpy.ops.render.render(write_still=True)
                wm.progress_update(index + 1)

            wm.progress_end()

        finally:
            wm.progress_end()
            self.restore_render_state()
