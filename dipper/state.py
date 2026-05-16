"""Sub-state classes that AppState delegates to."""

from dataclasses import dataclass

from dipper.constants import GROUP_COUNT


@dataclass
class LineState:
    text: str
    group: int = 0


@dataclass
class GroupAnnotation:
    group: int
    text: str = ""


class SearchState:
    """Tracks active search pattern, match positions, and cursor within matches."""

    def __init__(self) -> None:
        self.pattern: str = ""
        self.indices: list[int] = []
        self.cursor: int = 0

    def set(self, pattern: str, indices: list[int]) -> None:
        self.pattern = pattern
        self.indices = indices
        self.cursor = 0

    def clear(self) -> None:
        self.pattern = ""
        self.indices = []
        self.cursor = 0

    def advance(self) -> int | None:
        if not self.indices:
            return None
        self.cursor = (self.cursor + 1) % len(self.indices)
        return self.indices[self.cursor]

    def retreat(self) -> int | None:
        if not self.indices:
            return None
        self.cursor = (self.cursor - 1) % len(self.indices)
        return self.indices[self.cursor]

    def select_all(self, lines: list[LineState], active_group: int) -> list[int]:
        """Assign all matched lines to active_group. Returns list of changed indices."""
        changed = list(self.indices)
        for line_idx in changed:
            lines[line_idx].group = active_group
        return changed


class RangeFillState:
    """Tracks a pending range-fill anchor and the group it was set for."""

    def __init__(self) -> None:
        self.anchor: int | None = None
        self.anchor_group: int = 1

    def set_anchor(self, idx: int, group: int) -> None:
        self.anchor = idx
        self.anchor_group = group

    def clear_anchor(self) -> None:
        self.anchor = None

    def fill(self, lines: list[LineState], end_idx: int, active_group: int) -> range:
        """Fill from anchor to end_idx with active_group. Returns affected range. Clears anchor."""
        if self.anchor is None:
            raise RuntimeError("fill called with no anchor set")
        if not (0 <= end_idx < len(lines)):
            raise IndexError(f"end index {end_idx} out of range")
        start = min(self.anchor, end_idx)
        end = max(self.anchor, end_idx)
        affected = range(start, end + 1)
        for line_idx in affected:
            lines[line_idx].group = active_group
        self.clear_anchor()
        return affected


class GroupState:
    """Tracks the active group selection, group names, and annotations."""

    def __init__(self, group_names: dict[int, str], active_group: int = 1) -> None:
        self._active: int = active_group
        self.names: dict[int, str] = dict(group_names)
        self.annotations: dict[int, GroupAnnotation] = {}

    @property
    def active(self) -> int:
        return self._active

    @active.setter
    def active(self, value: int) -> None:
        if not (1 <= value <= GROUP_COUNT):
            raise ValueError(f"active_group must be 1-{GROUP_COUNT}, got {value}")
        self._active = value

    def set_annotation(self, group: int, text: str) -> None:
        if text:
            self.annotations[group] = GroupAnnotation(group=group, text=text)
        else:
            self.annotations.pop(group, None)

    def set_name(self, group: int, name: str) -> None:
        if name:
            self.names[group] = name
        else:
            self.names.pop(group, None)

    def label(self, group: int) -> str:
        return self.names.get(group, f"group {group}")

    def reset(self) -> None:
        self._active = 1
        self.names.clear()
        self.annotations.clear()


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
