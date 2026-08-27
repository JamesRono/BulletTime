"""Line-of-sight pruning for scattered camera points."""

from dataclasses import dataclass

from mathutils import Vector


@dataclass
class PruneResult:
    """Outcome of filtering camera points by visibility to the subject."""

    valid_points: list
    invalid_points: list

    @property
    def generated_count(self):
        return len(self.valid_points) + len(self.invalid_points)

    @property
    def valid_count(self):
        return len(self.valid_points)

    @property
    def pruned_count(self):
        return len(self.invalid_points)


def _is_subject_or_child(hit_obj, subject):
    """Return True if the hit object is the subject or one of its descendants."""
    obj = hit_obj
    while obj is not None:
        if obj == subject:
            return True
        obj = obj.parent
    return False


def _ray_hits_subject(context, ray_origin, direction, max_distance, subject):
    """Cast a ray and check whether the subject is the first surface hit."""
    depsgraph = context.evaluated_depsgraph_get()
    hit, _, _, _, hit_obj, _ = context.scene.ray_cast(
        depsgraph, ray_origin, direction, distance=max_distance
    )

    if hit:
        return _is_subject_or_child(hit_obj, subject)

    eval_subject = subject.evaluated_get(depsgraph)
    inv = eval_subject.matrix_world.inverted()
    local_origin = inv @ Vector(ray_origin)
    local_direction = (inv.to_3x3() @ direction).normalized()

    hit_mesh, _, _, _ = eval_subject.ray_cast(local_origin, local_direction)
    return hit_mesh


def has_line_of_sight(context, camera_point, subject, center):
    """Return True if the camera has an unobstructed view of the subject center."""
    to_center = center - camera_point.location
    distance = to_center.length
    if distance < 1e-6:
        return False

    direction = to_center / distance
    epsilon = min(0.01, distance * 0.001)
    ray_origin = camera_point.location + direction * epsilon
    ray_distance = distance - epsilon * 2

    return _ray_hits_subject(context, ray_origin, direction, ray_distance, subject)


def prune_camera_points(context, points, subject, center):
    """Split a point list into valid and rejected entries by line-of-sight."""
    valid_points = []
    invalid_points = []

    for point in points:
        if has_line_of_sight(context, point, subject, center):
            valid_points.append(point)
        else:
            invalid_points.append(point)

    return PruneResult(valid_points=valid_points, invalid_points=invalid_points)
