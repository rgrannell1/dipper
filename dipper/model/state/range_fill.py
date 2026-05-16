"""RangeFillState: pending range-fill anchor and group."""

from dipper.model.state.line import LineState


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
