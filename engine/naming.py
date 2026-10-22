"""Output filename helpers for rendered images."""

import os
import re


def sanitize_name(name):
    """Make a Blender object name safe for use in a filename."""
    cleaned = re.sub(r"[^\w\-]+", "_", name.strip())
    return cleaned or "subject"


def make_filename(subject_name, azimuth, elevation, extension="png"):
    """Build a filename from subject-relative azimuth and elevation."""
    name = sanitize_name(subject_name)
    az = round(azimuth) % 360
    el = round(elevation)
    sign = "+" if el >= 0 else "-"
    return f"{name}_az{az:03d}_el{sign}{abs(el):03d}.{extension}"


def make_filepath(output_dir, subject_name, azimuth, elevation, extension="png"):
    """Return the full output path for one rendered frame."""
    filename = make_filename(subject_name, azimuth, elevation, extension)
    return os.path.join(output_dir, filename)
