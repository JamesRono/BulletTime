"""Debug helpers for visualizing scattered camera points in the viewport."""

import bpy
from mathutils import Matrix


PREVIEW_COLLECTION = "BulletTime_Preview"
PREVIEW_PREFIX = "BT_Point_"


def clear_preview_empties():
    """Remove all preview empties created by the debug tools."""
    removed = 0
    for obj in list(bpy.data.objects):
        if obj.name.startswith(PREVIEW_PREFIX):
            bpy.data.objects.remove(obj, do_unlink=True)
            removed += 1

    collection = bpy.data.collections.get(PREVIEW_COLLECTION)
    if collection and not collection.objects:
        bpy.data.collections.remove(collection)

    return removed

def _get_or_create_preview_collection(context):
    """Return the collection used to hold preview empties."""
    collection = bpy.data.collections.get(PREVIEW_COLLECTION)
    if collection is None:
        collection = bpy.data.collections.new(PREVIEW_COLLECTION)
        context.scene.collection.children.link(collection)
    return collection


def create_point_empties(context, points):
    """Place arrow empties at each camera point for viewport debugging."""
    clear_preview_empties()
    collection = _get_or_create_preview_collection(context)

    for index, point in enumerate(points):
        empty = bpy.data.objects.new(
            f"{PREVIEW_PREFIX}{index:03d}",
            None,
        )
        empty.empty_display_type = "ARROWS"
        empty.empty_display_size = max(context.scene.bullet_time_props.radius * 0.05, 0.1)
        empty.show_name = True

        rotation = point.direction.to_track_quat("-Z", "Y").to_matrix().to_4x4()
        empty.matrix_world = Matrix.Translation(point.location) @ rotation

        collection.objects.link(empty)

    return len(points)
