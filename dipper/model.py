# Single source of truth for all application state — document, search, and range-fill.

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


class AppState:
    """All mutable state for one dipper session.

    Invariants enforced by every mutating method:
    - active_group is always in 1..GROUP_COUNT
    - line.group is always 0 or 1..GROUP_COUNT
    - range_anchor is None or a valid line index
    - range_anchor_group equals active_group at the moment the anchor was set
    - match_cursor is always within bounds of match_indices (or 0 when empty)
    - switching active_group always clears the range anchor
    """

    def __init__(
        self,
        lines: list[LineState],
        group_names: dict[int, str] | None = None,
        active_group: int = 1,
    ) -> None:
        if not (1 <= active_group <= GROUP_COUNT):
            raise ValueError(f"active_group must be 1-{GROUP_COUNT}, got {active_group}")
        self._lines: list[LineState] = lines
        self._annotations: dict[int, GroupAnnotation] = {}
        self._group_names: dict[int, str] = dict(group_names or {})
        self._active_group: int = active_group
        # search state
        self._search_pattern: str = ""
        self._match_indices: list[int] = []
        self._match_cursor: int = 0
        # range-fill state
        self._range_anchor: int | None = None
        self._range_anchor_group: int = active_group

    # ── read-only properties ──────────────────────────────────────────────────

    @property
    def lines(self) -> list[LineState]:
        return self._lines

    @property
    def annotations(self) -> dict[int, GroupAnnotation]:
        return self._annotations

    @property
    def group_names(self) -> dict[int, str]:
        return self._group_names

    @property
    def search_pattern(self) -> str:
        return self._search_pattern

    @property
    def match_indices(self) -> list[int]:
        return self._match_indices

    @property
    def match_cursor(self) -> int:
        return self._match_cursor

    @property
    def range_anchor(self) -> int | None:
        return self._range_anchor

    @property
    def range_anchor_group(self) -> int:
        return self._range_anchor_group

    # ── active_group: validated property ─────────────────────────────────────

    @property
    def active_group(self) -> int:
        return self._active_group

    @active_group.setter
    def active_group(self, value: int) -> None:
        if not (1 <= value <= GROUP_COUNT):
            raise ValueError(f"active_group must be 1-{GROUP_COUNT}, got {value}")
        self._active_group = value
        self._range_anchor = None  # switching group always invalidates the anchor

    # ── document mutations ────────────────────────────────────────────────────

    def toggle_line(self, idx: int) -> None:
        if not (0 <= idx < len(self._lines)):
            raise IndexError(f"line index {idx} out of range [0, {len(self._lines)})")
        line = self._lines[idx]
        line.group = 0 if line.group == self._active_group else self._active_group

    def set_line_group(self, idx: int, group: int) -> None:
        if not (0 <= idx < len(self._lines)):
            raise IndexError(f"line index {idx} out of range")
        if group != 0 and not (1 <= group <= GROUP_COUNT):
            raise ValueError(f"group must be 0 or 1-{GROUP_COUNT}, got {group}")
        self._lines[idx].group = group

    def set_annotation(self, group: int, text: str) -> None:
        if text:
            self._annotations[group] = GroupAnnotation(group=group, text=text)
        else:
            self._annotations.pop(group, None)

    def set_group_name(self, group: int, name: str) -> None:
        if name:
            self._group_names[group] = name
        else:
            self._group_names.pop(group, None)

    # ── range-fill mutations ──────────────────────────────────────────────────

    def set_range_anchor(self, idx: int | None) -> None:
        if idx is not None and not (0 <= idx < len(self._lines)):
            raise IndexError(f"anchor index {idx} out of range")
        self._range_anchor = idx
        self._range_anchor_group = self._active_group

    def fill_range(self, end_idx: int) -> range:
        """Fill from anchor to end_idx with active_group. Returns affected range. Clears anchor."""
        if self._range_anchor is None:
            raise RuntimeError("fill_range called with no anchor set")
        if not (0 <= end_idx < len(self._lines)):
            raise IndexError(f"end index {end_idx} out of range")
        start = min(self._range_anchor, end_idx)
        end = max(self._range_anchor, end_idx)
        affected = range(start, end + 1)
        for i in affected:
            self._lines[i].group = self._active_group
        self._range_anchor = None
        return affected

    # ── search mutations ──────────────────────────────────────────────────────

    def set_search(self, pattern: str, indices: list[int]) -> None:
        self._search_pattern = pattern
        self._match_indices = indices
        self._match_cursor = 0

    def clear_search(self) -> None:
        self._search_pattern = ""
        self._match_indices = []
        self._match_cursor = 0

    def next_match(self) -> int | None:
        if not self._match_indices:
            return None
        self._match_cursor = (self._match_cursor + 1) % len(self._match_indices)
        return self._match_indices[self._match_cursor]

    def prev_match(self) -> int | None:
        if not self._match_indices:
            return None
        self._match_cursor = (self._match_cursor - 1) % len(self._match_indices)
        return self._match_indices[self._match_cursor]

    def select_all_matches(self) -> list[int]:
        """Assign all matched lines to active_group. Returns list of changed indices."""
        changed = list(self._match_indices)
        for idx in changed:
            self._lines[idx].group = self._active_group
        return changed

    # ── queries ───────────────────────────────────────────────────────────────

    def selected_groups(self) -> set[int]:
        return {line.group for line in self._lines if line.group != 0}

    def group_label(self, group: int) -> str:
        return self._group_names.get(group, f"group {group}")

    def nearest_group(self, cursor: int) -> int | None:
        best_group = None
        best_distance = None
        for idx, line in enumerate(self._lines):
            if line.group == 0:
                continue
            distance = abs(idx - cursor)
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_group = line.group
        return best_group

    def nearest_annotated_group(self, cursor: int) -> int | None:
        best_group = None
        best_distance = None
        for idx, line in enumerate(self._lines):
            if line.group == 0 or line.group not in self._annotations:
                continue
            distance = abs(idx - cursor)
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_group = line.group
        return best_group


# Backward-compatible alias so existing imports of DocumentModel continue to work.
DocumentModel = AppState
