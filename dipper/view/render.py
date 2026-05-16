"""View layer: pure render helpers"""

from __future__ import annotations

from rich.style import Style
from rich.text import Text
from textual.widgets import ListItem, Static

from dipper.commons.constants import GROUP_COLOURS
from dipper.model.state import AppState, nearest_annotated_block, selected_groups

# --- pure render helpers ---


def gutter_text(line_num: str, highlighted: bool) -> Text:
    style = "bold yellow" if highlighted else "dim"
    return Text(f"{line_num} ", style=style)


def indicator_text(group: int, anchor_group: int, is_anchor: bool) -> Text:
    if group != 0:
        return group_dot(GROUP_COLOURS[group])
    if is_anchor:
        return group_diamond(GROUP_COLOURS[anchor_group])
    return Text("  ")


def group_dot(colour: str) -> Text:
    return Text("● ", style=Style(color=colour, bold=True))


def group_diamond(colour: str) -> Text:
    return Text("◆ ", style=Style(color=colour, bold=True))


def coloured_circle_markup(colour: str, content: str) -> str:
    return f"[{colour}]●{content}[/]"


def search_hit_text(pattern: str, pos: int, total: int) -> Text:
    result = Text()
    result.append(f"  |  /{pattern} [{pos}/{total}]", style="bold yellow")
    return result


def search_miss_text(pattern: str) -> Text:
    result = Text()
    result.append(f"  |  /{pattern} [no matches]", style="dim yellow")
    return result


def group_used_dot(group: int) -> Text:
    return Text("● ", style=Style(color=GROUP_COLOURS[group], bold=True))


def group_name_text(group: int, name: str) -> Text:
    colour = GROUP_COLOURS[group]
    if name:
        return Text(name, style=Style(color=colour, bold=True))
    return Text(f"group {group}", style="dim")


def group_line_count_text(count: int) -> Text:
    label = f"{count} line{'s' if count != 1 else ''}"
    return Text(f"  —  {label}", style="dim")


def group_row_text(model: AppState, group: int) -> Text:
    colour = GROUP_COLOURS[group]
    count = sum(1 for line in model.lines if line.group == group)
    name = model.groups.names.get(group, "")
    result = Text()
    result.append_text(group_dot(colour))
    result.append_text(group_name_text(group, name))
    result.append_text(group_line_count_text(count))
    return result


def group_modal_title(group: int) -> str:
    colour = GROUP_COLOURS[group]
    return coloured_circle_markup(colour, f"  group {group}")


def annotation_modal_title(group: int, label: str, start_line: int = 0, end_line: int = 0) -> str:
    colour = GROUP_COLOURS[group]
    if start_line and end_line and start_line != end_line:
        range_str = f"lines {start_line}-{end_line}"
    elif start_line:
        range_str = f"line {start_line}"
    else:
        range_str = ""
    suffix = f"  —  {range_str}" if range_str else ""
    return coloured_circle_markup(colour, f" {label}{suffix}")


def group_row_item(model: AppState, grp: int) -> ListItem:
    return ListItem(Static(group_row_text(model, grp), markup=False, id=f"gs-{grp}"), id=f"gr-{grp}")


def search_section_text(model: AppState) -> Text:
    pattern = model.search.pattern
    result = Text()
    if not pattern:
        return result
    if model.search.indices:
        pos = model.search.cursor + 1
        total = len(model.search.indices)
        result.append_text(search_hit_text(pattern, pos, total))
    else:
        result.append_text(search_miss_text(pattern))
    return result


def annotation_section_text(model: AppState, cursor_idx: int) -> Text:
    annotation = nearest_annotated_block(model.lines, model.groups.block_annotations, cursor_idx)
    result = Text()
    if annotation:
        result.append(f"  |  {annotation}", style="italic dim")
    return result


def status_bar_text(model: AppState, filename: str, cursor_idx: int = 0) -> Text:
    active = model.active_group
    colour = GROUP_COLOURS[active]
    result = Text(no_wrap=True, overflow="ellipsis")
    result.append_text(group_dot(colour))
    result.append(model.groups.label(active), style=Style(color=colour, bold=True))
    used = sorted(selected_groups(model.lines))
    if used:
        result.append("  |  ", style="dim")
        for grp in used:
            result.append_text(group_used_dot(grp))
    result.append_text(annotation_section_text(model, cursor_idx))
    result.append_text(search_section_text(model))
    result.append(f"  |  {filename}", style="dim")
    return result
