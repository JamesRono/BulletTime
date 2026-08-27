"""Render quality presets mapped to resolution and sample count."""

PRESETS = {
    "DRAFT": {"resolution_x": 640, "resolution_y": 360, "samples": 32},
    "MEDIUM": {"resolution_x": 1280, "resolution_y": 720, "samples": 128},
    "HIGH": {"resolution_x": 1920, "resolution_y": 1080, "samples": 512},
}


def get_quality_settings(preset):
    """Return resolution and sample settings for a quality preset name."""
    return PRESETS.get(preset, PRESETS["MEDIUM"])
