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


def next_diff_hunk_start(indices: list[int], cursor: int) -> int | None:
    """Return the first diff hunk start strictly after cursor, or None."""
    index_set = set(indices)
    for idx in indices:
        if idx <= cursor:
            continue
        if idx - 1 not in index_set:
            return idx
    return None


def prev_diff_hunk_start(indices: list[int], cursor: int) -> int | None:
    """Return the last diff hunk start strictly before cursor, or None."""
    index_set = set(indices)
    result = None
    for idx in indices:
        if idx >= cursor:
            break
        if idx - 1 not in index_set:
            result = idx
    return result


def next_block_start(lines: list[LineState], cursor: int) -> int | None:
    """Return the index of the first block start strictly after cursor, or None."""
    for idx in range(cursor + 1, len(lines)):
        if lines[idx].group == 0:
            continue
        prev_group = lines[idx - 1].group if idx > 0 else 0
        if prev_group != lines[idx].group:
            return idx
    return None


def prev_block_start(lines: list[LineState], cursor: int) -> int | None:
    """Return the index of the last block start strictly before cursor, or None."""
    result = None
    for idx in range(cursor):
        if lines[idx].group == 0:
            continue
        prev_group = lines[idx - 1].group if idx > 0 else 0
        if prev_group != lines[idx].group:
            result = idx
    return result


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
