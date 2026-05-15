# Data model for line state and group annotations

from dataclasses import dataclass, field


@dataclass
class LineState:
    text: str
    group: int = 0  # 0 means unselected


@dataclass
class GroupAnnotation:
    group: int
    text: str = ""


@dataclass
class DocumentModel:
    lines: list[LineState] = field(default_factory=list)
    annotations: dict[int, GroupAnnotation] = field(default_factory=dict)
    group_names: dict[int, str] = field(default_factory=dict)
    active_group: int = 1
    header_group_name: str | None = None

    def header_group(self) -> int | None:
        """Resolve header_group_name to a group number, or None if not found."""
        if self.header_group_name is None:
            return None
        for num, name in self.group_names.items():
            if name == self.header_group_name:
                return num
        return None

    def group_label(self, group: int) -> str:
        return self.group_names.get(group, f"group {group}")

    def toggle_line(self, idx: int) -> None:
        line = self.lines[idx]
        if line.group == self.active_group:
            line.group = 0
        else:
            line.group = self.active_group

    def set_annotation(self, group: int, text: str) -> None:
        self.annotations[group] = GroupAnnotation(group=group, text=text)

    def selected_groups(self) -> set[int]:
        return {line.group for line in self.lines if line.group != 0}

    def nearest_group(self, cursor: int) -> int | None:
        """Return the group whose nearest selected line is closest to cursor."""
        best_group = None
        best_distance = None
        for idx, line in enumerate(self.lines):
            if line.group == 0:
                continue
            distance = abs(idx - cursor)
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_group = line.group
        return best_group

    def nearest_annotated_group(self, cursor: int) -> int | None:
        """Return the group with a note whose nearest selected line is closest to cursor."""
        best_group = None
        best_distance = None
        for idx, line in enumerate(self.lines):
            if line.group == 0:
                continue
            if line.group not in self.annotations:
                continue
            distance = abs(idx - cursor)
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_group = line.group
        return best_group
