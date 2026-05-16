"""AppState: thin coordinator that delegates to sub-state objects."""

from dipper.commons.constants import GROUP_COUNT
from dipper.model.state.group import GroupState
from dipper.model.state.line import LineState
from dipper.model.state.range_fill import RangeFillState
from dipper.model.state.search import SearchState


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
        self._undo: tuple | None = None

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

    # ── block helpers ─────────────────────────────────────────────────────────

    def blocks(self, group: int) -> list[tuple[int, int]]:
        """Return sorted list of (start_idx, end_idx) for contiguous runs of group in lines."""
        result: list[tuple[int, int]] = []
        start: int | None = None
        for idx, line in enumerate(self._lines):
            if line.group == group:
                if start is None:
                    start = idx
            elif start is not None:
                result.append((start, idx - 1))
                start = None
        if start is not None:
            result.append((start, len(self._lines) - 1))
        return result

    def block_at(self, idx: int) -> tuple[int, int] | None:
        """Return (group, block_start_idx) for the line at idx, or None if unselected."""
        group = self._lines[idx].group
        if group == 0:
            return None
        start = idx
        while start > 0:
            if self._lines[start - 1].group != group:
                break
            start -= 1
        return (group, start)

    def remove_stale_block_annotations(self, group: int, old_blocks: list[tuple[int, int]]) -> None:
        """Remove annotations for any old block that no longer exists with the same (start, end)."""
        new_blocks_set = set(self.blocks(group))
        for old_start, old_end in old_blocks:
            if (old_start, old_end) not in new_blocks_set:
                self.groups.block_annotations.pop((group, old_start), None)

    # ── document mutations ────────────────────────────────────────────────────

    def toggle_line(self, idx: int) -> None:
        if not (0 <= idx < len(self._lines)):
            raise IndexError(f"line index {idx} out of range [0, {len(self._lines)})")
        line = self._lines[idx]
        old_group = line.group
        new_group = 0 if line.group == self.groups.active else self.groups.active
        affected = {old_group, new_group} - {0}
        old_block_map = {grp: self.blocks(grp) for grp in affected}
        line.group = new_group
        for grp in affected:
            self.remove_stale_block_annotations(grp, old_block_map[grp])

    def set_line_group(self, idx: int, group: int) -> None:
        if not (0 <= idx < len(self._lines)):
            raise IndexError(f"line index {idx} out of range")
        if group != 0 and not (1 <= group <= GROUP_COUNT):
            raise ValueError(f"group must be 0 or 1-{GROUP_COUNT}, got {group}")
        old_group = self._lines[idx].group
        affected = {old_group, group} - {0}
        old_block_map = {grp: self.blocks(grp) for grp in affected}
        self._lines[idx].group = group
        for grp in affected:
            self.remove_stale_block_annotations(grp, old_block_map[grp])

    # ── undo buffer ───────────────────────────────────────────────────────────

    def take_snapshot(self) -> None:
        """Save current mutable state for a single-level undo."""
        self._undo = (
            [line.group for line in self._lines],
            dict(self.groups.names),
            dict(self.groups.block_annotations),
        )

    def undo(self) -> bool:
        """Restore the last snapshot. Returns True if a snapshot was available."""
        if self._undo is None:
            return False
        line_groups, names, block_annotations = self._undo
        self._undo = None
        for idx, grp in enumerate(line_groups):
            self._lines[idx].group = grp
        self.groups.names = dict(names)
        self.groups.block_annotations = dict(block_annotations)
        return True

    # ── full reset ────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Reset all session state to initial values. Cursor position is not affected."""
        for line in self._lines:
            line.group = 0
        self.groups.reset()
        self.search.clear()
        self.range_fill.clear_anchor()


# Backward-compatible alias so existing imports of DocumentModel continue to work.
DocumentModel = AppState
