"""Camera point generation relative to a subject object."""

import math
from dataclasses import dataclass

from mathutils import Vector


@dataclass
class CameraPoint:
    """World-space camera pose relative to the subject."""

    location: Vector
    direction: Vector
    azimuth: float
    elevation: float

@dataclass
class ArcConfig:
    radius: float
    start_angle: float
    end_angle: float
    elevation: float
    count: int

_AXIS_MAP = {
    "X": Vector((1.0, 0.0, 0.0)),
    "-X": Vector((-1.0, 0.0, 0.0)),
    "Y": Vector((0.0, 1.0, 0.0)),
    "-Y": Vector((0.0, -1.0, 0.0)),
}


def _get_evaluated_object(subject, context):
    """Return the subject with modifiers and transforms applied."""
    if context is None:
        return subject
    depsgraph = context.evaluated_depsgraph_get()
    return subject.evaluated_get(depsgraph)


def get_subject_center(subject, context=None):
    """World-space center of the subject bounding box."""
    eval_obj = _get_evaluated_object(subject, context)
    local_center = sum((Vector(corner) for corner in eval_obj.bound_box), Vector()) / 8
    return eval_obj.matrix_world @ local_center


def _get_frame_vectors(subject, context=None):
    """Extract forward, right, and up vectors directly from the subject's world rotation."""
    eval_obj = _get_evaluated_object(subject, context)
    matrix = eval_obj.matrix_world.to_3x3()

    # Assuming Blender's standard local axes (adjust if your models face a different axis):
    # - Local Y (or -Y) as forward, X as right, Z as up
    right = matrix @ Vector((1.0, 0.0, 0.0))
    front = matrix @ Vector((0.0, 1.0, 0.0))  # Or (0.0, -1.0, 0.0) depending on your asset setup
    up = matrix @ Vector((0.0, 0.0, 1.0))

    # If you want a strictly horizontal forward vector (ignoring pitch/tilt):
    front_h = Vector((front.x, front.y, 0.0))
    if front_h.length > 0.001:
        front_h.normalize()
    else:
        front_h = Vector((0.0, 1.0, 0.0))

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

def generate_arc_points(center, config: ArcConfig, front, right, up):
    """Place points evenly along an arc using the ArcConfig dataclass."""
    if config.count == 1:
        azimuths = [(config.start_angle + config.end_angle) / 2]
    else:
        span = config.end_angle - config.start_angle

        if math.isclose(span, 360.0, abs_tol=1e-5): # Check if this is a full circle
            # Divide by 'count' so it wraps cleanly without duplicating the start and end points ie 0/360
            step = span / config.count
            azimuths = [config.start_angle + step * i for i in range(config.count)]
        else:
            # For an open arc, divide by 'count - 1' to keep both endpoints
            step = span / (config.count - 1)
            azimuths = [config.start_angle + step * i for i in range(config.count)]

    return [
        _point_from_angles(
            center, config.radius, front, right, up, azimuth, config.elevation
        )
        for azimuth in azimuths
    ]


def generate_sphere_points(subject, props, context=None):
    """Distribute cameras evenly over a sphere using a Fibonacci lattice."""
    center = get_subject_center(subject, context)
    front_h, right, up = _get_frame_vectors(subject, context)


    count = props.count
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

def scatter_camera_points(context, subject, props):
    """Generate all candidate camera points from the current path settings."""
    center = get_subject_center(subject, context)

    # Pass props.front_offset (or props.front_offset_rad) back into the vector getter
    front_h, right, up = _get_frame_vectors(subject, context)

    if props.path_shape == "SPHERE":
        return generate_sphere_points(subject, props, context)

    if props.path_shape == "CIRCLE":
        start_angle = 0.0
        end_angle = 360.0  # Use 360.0 if your engine uses degrees instead of radians
    else:
        start_angle = props.arc_start_angle
        end_angle = props.arc_end_angle

    #Bundle the properties into your pure dataclass once. This helps keep bpy out of the engine
    config = ArcConfig(
        radius=props.radius,
        start_angle=start_angle,
        end_angle=end_angle,
        elevation=props.elevation,
        count=props.count,
    )

    return generate_arc_points(center, config, front_h, right, up)
