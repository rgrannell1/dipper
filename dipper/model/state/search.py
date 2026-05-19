"""SearchState: active search pattern, match positions, and cursor within matches."""

from dataclasses import dataclass, field

from dipper.commons.constants import DEFAULT_SEARCH_COLOUR
from dipper.model.state.line import LineState


@dataclass
class SearchOverlays:
    """Per-line colour and gutter mark overrides, used for diff highlighting."""

    line_colours: dict[int, str] = field(default_factory=dict)
    line_marks: dict[int, str] = field(default_factory=dict)


class SearchState:
    """Tracks active search pattern, match positions, cursor within matches, and highlight colour."""

    def __init__(self) -> None:
        self.pattern: str = ""
        self.indices: list[int] = []
        self.cursor: int = 0
        self.colour: str = DEFAULT_SEARCH_COLOUR
        self.line_colours: dict[int, str] = {}
        self.line_marks: dict[int, str] = {}

    def set(self, pattern: str, indices: list[int], colour: str = DEFAULT_SEARCH_COLOUR, overlays: SearchOverlays | None = None) -> None:  # noqa: E501
        self.pattern = pattern
        self.indices = indices
        self.cursor = 0
        self.colour = colour
        resolved = overlays or SearchOverlays()
        self.line_colours = resolved.line_colours
        self.line_marks = resolved.line_marks

    def clear(self) -> None:
        self.pattern = ""
        self.indices = []
        self.cursor = 0
        self.colour = DEFAULT_SEARCH_COLOUR
        self.line_colours = {}
        self.line_marks = {}

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
