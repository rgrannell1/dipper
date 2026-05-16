"""GroupState: active group selection, names, and annotations."""

from dipper.constants import GROUP_COUNT
from dipper.state.line import GroupAnnotation


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
