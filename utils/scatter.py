"""Scatter step — generate candidate camera points without visibility checks."""

from .geometry import generate_arc_points, generate_sphere_points


def scatter_camera_points(context, subject, props):
    """Generate all candidate camera points from the current path settings."""
    if props.path_shape == "SPHERE":
        return generate_sphere_points(subject, props, context)
    return generate_arc_points(subject, props, context)
