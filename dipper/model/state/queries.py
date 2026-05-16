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


def nearest_block(lines: list[LineState], cursor: int) -> tuple[int, int] | None:
    """Return (group, block_start_idx) of the nearest block to cursor, or None."""
    best: tuple[int, int] | None = None
    best_distance: int | None = None
    for idx, line in enumerate(lines):
        if line.group == 0:
            continue
        prev_group = lines[idx - 1].group if idx > 0 else None
        is_block_start = prev_group is None or prev_group != line.group
        if not is_block_start:
            continue
        distance = abs(idx - cursor)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best = (line.group, idx)
    return best


def nearest_annotated_block(
    lines: list[LineState],
    block_annotations: dict[tuple[int, int], str],
    cursor: int,
) -> str | None:
    """Return annotation text for the annotated block nearest to cursor, or None."""
    best_text: str | None = None
    best_distance: int | None = None
    for (_group, start_idx), text in block_annotations.items():
        distance = abs(start_idx - cursor)
        if best_distance is None or distance < best_distance:
            best_distance = distance
            best_text = text
    return best_text
