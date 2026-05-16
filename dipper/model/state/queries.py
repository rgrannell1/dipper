"""Query functions over collections of LineState."""

from dipper.model.state.line import LineState


def selected_groups(lines: list[LineState]) -> set[int]:
    """Return the set of non-zero group numbers present in lines."""
    return {line.group for line in lines if line.group != 0}


def nearest_group(lines: list[LineState], cursor: int) -> int | None:
    """Return the group of the nearest assigned line to cursor, or None."""
    best_group = None
    best_distance = None
    for idx, line in enumerate(lines):
        if line.group == 0:
            continue
        distance = abs(idx - cursor)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_group = line.group
    return best_group


def nearest_annotated_group(lines: list[LineState], annotations: dict, cursor: int) -> int | None:
    """Return the group of the nearest annotated assigned line to cursor, or None."""
    best_group = None
    best_distance = None
    for idx, line in enumerate(lines):
        if line.group == 0 or line.group not in annotations:
            continue
        distance = abs(idx - cursor)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_group = line.group
    return best_group
