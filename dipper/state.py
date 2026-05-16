# Sub-state classes that AppState delegates to.

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
