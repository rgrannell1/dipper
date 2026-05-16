# AppState: coordinator that delegates to sub-state objects in state.py.

from dipper.constants import GROUP_COUNT
from dipper.state import GroupAnnotation, GroupState, LineState, RangeFillState, SearchState


class AppState:
    """Coordinator: owns document lines; delegates group, search, and range-fill to sub-states.

    Invariants:
    - active_group is always in 1..GROUP_COUNT
    - line.group is always 0 or 1..GROUP_COUNT
    - range_anchor is None or a valid line index
    - switching active_group always clears the range anchor
    - match_cursor is always within bounds of match_indices (or 0 when empty)
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
        self._groups = GroupState(group_names or {}, active_group)
        self._search = SearchState()
        self._range_fill = RangeFillState()

    # ── read-only properties ──────────────────────────────────────────────────

    @property
    def lines(self) -> list[LineState]:
        return self._lines

    @property
    def annotations(self) -> dict[int, GroupAnnotation]:
        return self._groups.annotations

    @property
    def group_names(self) -> dict[int, str]:
        return self._groups.names

    @property
    def search_pattern(self) -> str:
        return self._search.pattern

    @property
    def match_indices(self) -> list[int]:
        return self._search.indices

    @property
    def match_cursor(self) -> int:
        return self._search.cursor

    @property
    def range_anchor(self) -> int | None:
        return self._range_fill.anchor

    @property
    def range_anchor_group(self) -> int:
        return self._range_fill.anchor_group

    # ── active_group: validated, clears range anchor on change ───────────────

    @property
    def active_group(self) -> int:
        return self._groups.active

    @active_group.setter
    def active_group(self, value: int) -> None:
        self._groups.active = value  # raises ValueError if out of range
        self._range_fill.clear_anchor()

    # ── document mutations ────────────────────────────────────────────────────

    def toggle_line(self, idx: int) -> None:
        if not (0 <= idx < len(self._lines)):
            raise IndexError(f"line index {idx} out of range [0, {len(self._lines)})")
        line = self._lines[idx]
        line.group = 0 if line.group == self._groups.active else self._groups.active

    def set_line_group(self, idx: int, group: int) -> None:
        if not (0 <= idx < len(self._lines)):
            raise IndexError(f"line index {idx} out of range")
        if group != 0 and not (1 <= group <= GROUP_COUNT):
            raise ValueError(f"group must be 0 or 1-{GROUP_COUNT}, got {group}")
        self._lines[idx].group = group

    def set_annotation(self, group: int, text: str) -> None:
        self._groups.set_annotation(group, text)

    def set_group_name(self, group: int, name: str) -> None:
        self._groups.set_name(group, name)

    # ── range-fill mutations ──────────────────────────────────────────────────

    def set_range_anchor(self, idx: int | None) -> None:
        if idx is not None and not (0 <= idx < len(self._lines)):
            raise IndexError(f"anchor index {idx} out of range")
        if idx is None:
            self._range_fill.clear_anchor()
        else:
            self._range_fill.set_anchor(idx, self._groups.active)

    def fill_range(self, end_idx: int) -> range:
        """Fill from anchor to end_idx with active_group. Returns affected range. Clears anchor."""
        if self._range_fill.anchor is None:
            raise RuntimeError("fill_range called with no anchor set")
        if not (0 <= end_idx < len(self._lines)):
            raise IndexError(f"end index {end_idx} out of range")
        start = min(self._range_fill.anchor, end_idx)
        end = max(self._range_fill.anchor, end_idx)
        affected = range(start, end + 1)
        for line_idx in affected:
            self._lines[line_idx].group = self._groups.active
        self._range_fill.clear_anchor()
        return affected

    # ── search mutations ──────────────────────────────────────────────────────

    def set_search(self, pattern: str, indices: list[int]) -> None:
        self._search.set(pattern, indices)

    def clear_search(self) -> None:
        self._search.clear()

    def next_match(self) -> int | None:
        return self._search.advance()

    def prev_match(self) -> int | None:
        return self._search.retreat()

    # ── full reset ────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Reset all session state to initial values. Cursor position is not affected."""
        for line in self._lines:
            line.group = 0
        self._groups.reset()
        self._search.clear()
        self._range_fill.clear_anchor()

    def select_all_matches(self) -> list[int]:
        """Assign all matched lines to active_group. Returns list of changed indices."""
        changed = list(self._search.indices)
        for line_idx in changed:
            self._lines[line_idx].group = self._groups.active
        return changed

    # ── queries ───────────────────────────────────────────────────────────────

    def selected_groups(self) -> set[int]:
        return {line.group for line in self._lines if line.group != 0}

    def group_label(self, group: int) -> str:
        return self._groups.label(group)

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
            if line.group == 0 or line.group not in self._groups.annotations:
                continue
            distance = abs(idx - cursor)
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_group = line.group
        return best_group


# Backward-compatible alias so existing imports of DocumentModel continue to work.
DocumentModel = AppState
