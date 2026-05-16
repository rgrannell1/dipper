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
