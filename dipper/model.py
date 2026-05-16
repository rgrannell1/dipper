"""AppState: thin coordinator that delegates to sub-state objects in state.py."""

from dipper.constants import GROUP_COUNT
from dipper.state import (
    GroupState,
    LineState,
    RangeFillState,
    SearchState,
    nearest_annotated_group,
    nearest_group,
    selected_groups,
)


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
        self.groups = GroupState(group_names or {}, active_group)
        self.search = SearchState()
        self.range_fill = RangeFillState()

    # ── read-only line access ─────────────────────────────────────────────────

    @property
    def lines(self) -> list[LineState]:
        return self._lines

    # ── active_group: validated, clears range anchor on change ───────────────

    @property
    def active_group(self) -> int:
        return self.groups.active

    @active_group.setter
    def active_group(self, value: int) -> None:
        self.groups.active = value  # raises ValueError if out of range
        self.range_fill.clear_anchor()

    # ── document mutations ────────────────────────────────────────────────────

    def toggle_line(self, idx: int) -> None:
        if not (0 <= idx < len(self._lines)):
            raise IndexError(f"line index {idx} out of range [0, {len(self._lines)})")
        line = self._lines[idx]
        line.group = 0 if line.group == self.groups.active else self.groups.active

    def set_line_group(self, idx: int, group: int) -> None:
        if not (0 <= idx < len(self._lines)):
            raise IndexError(f"line index {idx} out of range")
        if group != 0 and not (1 <= group <= GROUP_COUNT):
            raise ValueError(f"group must be 0 or 1-{GROUP_COUNT}, got {group}")
        self._lines[idx].group = group

    def set_annotation(self, group: int, text: str) -> None:
        self.groups.set_annotation(group, text)

    def set_group_name(self, group: int, name: str) -> None:
        self.groups.set_name(group, name)

    # ── range-fill mutations ──────────────────────────────────────────────────

    def set_range_anchor(self, idx: int | None) -> None:
        if idx is not None and not (0 <= idx < len(self._lines)):
            raise IndexError(f"anchor index {idx} out of range")
        if idx is None:
            self.range_fill.clear_anchor()
        else:
            self.range_fill.set_anchor(idx, self.groups.active)

    def fill_range(self, end_idx: int) -> range:
        """Fill from anchor to end_idx with active_group. Returns affected range. Clears anchor."""
        if self.range_fill.anchor is None:
            raise RuntimeError("fill_range called with no anchor set")
        if not (0 <= end_idx < len(self._lines)):
            raise IndexError(f"end index {end_idx} out of range")
        return self.range_fill.fill(self._lines, end_idx, self.groups.active)

    # ── search mutations ──────────────────────────────────────────────────────

    def set_search(self, pattern: str, indices: list[int]) -> None:
        self.search.set(pattern, indices)

    def clear_search(self) -> None:
        self.search.clear()

    def next_match(self) -> int | None:
        return self.search.advance()

    def prev_match(self) -> int | None:
        return self.search.retreat()

    # ── full reset ────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Reset all session state to initial values. Cursor position is not affected."""
        for line in self._lines:
            line.group = 0
        self.groups.reset()
        self.search.clear()
        self.range_fill.clear_anchor()

    def select_all_matches(self) -> list[int]:
        """Assign all matched lines to active_group. Returns list of changed indices."""
        return self.search.select_all(self._lines, self.groups.active)

    # ── queries ───────────────────────────────────────────────────────────────

    def selected_groups(self) -> set[int]:
        return selected_groups(self._lines)

    def group_label(self, group: int) -> str:
        return self.groups.label(group)

    def nearest_group(self, cursor: int) -> int | None:
        return nearest_group(self._lines, cursor)

    def nearest_annotated_group(self, cursor: int) -> int | None:
        return nearest_annotated_group(self._lines, self.groups.annotations, cursor)


# Backward-compatible alias so existing imports of DocumentModel continue to work.
DocumentModel = AppState
