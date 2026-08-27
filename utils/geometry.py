"""Camera point generation relative to a subject object."""

import math
from dataclasses import dataclass

from mathutils import Matrix, Vector


@dataclass
class CameraPoint:
    """World-space camera pose relative to the subject."""

    location: Vector
    direction: Vector
    azimuth: float
    elevation: float


_AXIS_MAP = {
    "X": Vector((1.0, 0.0, 0.0)),
    "-X": Vector((-1.0, 0.0, 0.0)),
    "Y": Vector((0.0, 1.0, 0.0)),
    "-Y": Vector((0.0, -1.0, 0.0)),
}


def _get_evaluated_object(obj, context):
    """Return the subject with modifiers and transforms applied."""
    if context is None:
        return obj
    depsgraph = context.evaluated_depsgraph_get()
    return obj.evaluated_get(depsgraph)


def get_subject_center(obj, context=None):
    """World-space center of the subject bounding box."""
    eval_obj = _get_evaluated_object(obj, context)
    local_center = sum((Vector(corner) for corner in eval_obj.bound_box), Vector()) / 8
    return eval_obj.matrix_world @ local_center


def _get_frame_vectors(obj, front_axis, front_offset_rad, context=None):
    """Build front, right, and up vectors for azimuth/elevation placement."""
    eval_obj = _get_evaluated_object(obj, context)
    local_front = _AXIS_MAP[front_axis]
    world_front = (eval_obj.matrix_world.to_3x3() @ local_front).normalized()
    up = (eval_obj.matrix_world.to_3x3() @ Vector((0.0, 0.0, 1.0))).normalized()

    rot = Matrix.Rotation(front_offset_rad, 4, up)
    front = (rot @ world_front).normalized()

    front_h = front - up * front.dot(up)
    if front_h.length < 1e-6:
        fallback = Vector((1.0, 0.0, 0.0))
        if abs(up.dot(fallback)) > 0.99:
            fallback = Vector((0.0, 1.0, 0.0))
        front_h = fallback - up * fallback.dot(up)
    front_h.normalize()

    right = up.cross(front_h).normalized()
    return front_h, right, up


def _point_from_angles(center, radius, front_h, right, up, azimuth_rad, elevation_rad):
    """Convert spherical angles into a camera point looking at the center."""
    horiz = math.cos(elevation_rad) * (
        math.cos(azimuth_rad) * front_h + math.sin(azimuth_rad) * right
    )
    vert = math.sin(elevation_rad) * up
    offset = horiz + vert
    if offset.length < 1e-6:
        offset = front_h
    else:
        offset.normalize()

    location = center + radius * offset
    direction = (center - location).normalized()
    azimuth_deg = math.degrees(azimuth_rad)
    elevation_deg = math.degrees(elevation_rad)
    return CameraPoint(location, direction, azimuth_deg, elevation_deg)


def _angles_from_location(location, center, front_h, right, up):
    """Derive azimuth and elevation from a world-space camera location."""
    offset = location - center
    if offset.length < 1e-6:
        return 0.0, 0.0
    offset.normalize()
    azimuth_rad = math.atan2(offset.dot(right), offset.dot(front_h))
    elevation_rad = math.asin(max(-1.0, min(1.0, offset.dot(up))))
    return math.degrees(azimuth_rad), math.degrees(elevation_rad)


def generate_arc_points(obj, props, context=None):
    """Place cameras evenly along an arc at a fixed elevation."""
    center = get_subject_center(obj, context)
    front_h, right, up = _get_frame_vectors(
        obj, props.front_axis, props.front_offset, context
    )

    start = props.arc_start_angle
    end = props.arc_end_angle
    elevation_rad = props.elevation
    count = props.density

    if count == 1:
        azimuths = [(start + end) / 2]
    else:
        step = (end - start) / (count - 1)
        azimuths = [start + step * i for i in range(count)]

    return [
        _point_from_angles(
            center, props.radius, front_h, right, up, azimuth, elevation_rad
        )
        for azimuth in azimuths
    ]


def generate_sphere_points(obj, props, context=None):
    """Distribute cameras evenly over a sphere using a Fibonacci lattice."""
    center = get_subject_center(obj, context)
    front_h, right, up = _get_frame_vectors(
        obj, props.front_axis, props.front_offset, context
    )

    count = props.density
    golden_ratio = (1.0 + math.sqrt(5.0)) / 2.0
    points = []

    for i in range(count):
        theta = 2.0 * math.pi * i / golden_ratio
        phi = math.acos(1.0 - 2.0 * (i + 0.5) / count)

        x = math.cos(theta) * math.sin(phi)
        y = math.sin(theta) * math.sin(phi)
        z = math.cos(phi)

        local_offset = Vector((x, y, z))
        world_offset = (
            front_h * local_offset.x
            + right * local_offset.y
            + up * local_offset.z
        )
        if world_offset.length < 1e-6:
            continue
        world_offset.normalize()

        location = center + props.radius * world_offset
        direction = (center - location).normalized()
        azimuth, elevation = _angles_from_location(location, center, front_h, right, up)
        points.append(CameraPoint(location, direction, azimuth, elevation))

    return points
