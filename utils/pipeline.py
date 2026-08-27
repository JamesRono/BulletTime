"""In-memory state for the scatter → prune → render pipeline."""

from dataclasses import dataclass, field


@dataclass
class PipelineState:
    generated_points: list = field(default_factory=list)
    valid_points: list = field(default_factory=list)
    invalid_points: list = field(default_factory=list)


_state = PipelineState()


def reset_pipeline_state():
    """Clear all cached point lists before a new run."""
    _state.generated_points = []
    _state.valid_points = []
    _state.invalid_points = []


def store_generated_points(points):
    """Store the full scatter output before pruning."""
    _state.generated_points = list(points)
    _state.valid_points = []
    _state.invalid_points = []


def store_prune_result(valid_points, invalid_points):
    """Store valid and rejected points after the prune step."""
    _state.valid_points = list(valid_points)
    _state.invalid_points = list(invalid_points)


def get_valid_points():
    """Return the current list of points that passed pruning."""
    return list(_state.valid_points)


def get_generated_points():
    """Return the most recently scattered point list."""
    return list(_state.generated_points)
