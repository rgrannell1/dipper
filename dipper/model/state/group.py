"""GroupState: active group selection, names, and per-block annotations."""

from dipper.commons.constants import GROUP_COUNT


class GroupState:
    """Tracks the active group selection, group names, and per-block annotations.

    Block annotations are keyed by (group, 0-based block_start_idx).
    """

    def __init__(self, group_names: dict[int, str], active_group: int = 1) -> None:
        self._active: int = active_group
        self.names: dict[int, str] = dict(group_names)
        self.block_annotations: dict[tuple[int, int], str] = {}

    @property
    def active(self) -> int:
        return self._active

    @active.setter
    def active(self, value: int) -> None:
        if not (1 <= value <= GROUP_COUNT):
            raise ValueError(f"active_group must be 1-{GROUP_COUNT}, got {value}")
        self._active = value

    def set_annotation(self, group: int, block_start: int, text: str) -> None:
        key = (group, block_start)
        if text:
            self.block_annotations[key] = text
        else:
            self.block_annotations.pop(key, None)

    def block_annotation(self, group: int, block_start: int) -> str:
        return self.block_annotations.get((group, block_start), "")

    def cleanup_annotations(self, group: int, valid_starts: set[int]) -> None:
        """Remove annotations for blocks of this group that no longer start at a valid index."""
        stale = [key for key in self.block_annotations if key[0] == group and key[1] not in valid_starts]
        for key in stale:
            del self.block_annotations[key]

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
        self.block_annotations.clear()
