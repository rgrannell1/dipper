"""SearchState: active search pattern, match positions, and cursor within matches."""

from dipper.state.line import LineState


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
