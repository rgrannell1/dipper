# Generates the annotated output format from the document model

from dipper.constants import (
    GROUP_FORMAT,
    HEADER_FORMAT,
    MARK_FORMAT,
    SEPARATOR_LINE,
    UNDERLINE_CHAR,
    UNDERLINE_MIN,
)
from dipper.model import DocumentModel


def _encode_ranges(line_numbers: list[int]) -> str:
    if not line_numbers:
        return ""
    sorted_nums = sorted(line_numbers)
    ranges: list[str] = []
    start = end = sorted_nums[0]
    for num in sorted_nums[1:]:
        if num == end + 1:
            end = num
        else:
            ranges.append(f"{start}-{end}" if start != end else str(start))
            start = end = num
    ranges.append(f"{start}-{end}" if start != end else str(start))
    return ",".join(ranges)


def _mark_line(text: str, group: int, line_number: int) -> str:
    underline = UNDERLINE_CHAR * max(len(text), UNDERLINE_MIN)
    return MARK_FORMAT.format(group=group, line=line_number, underline=underline)


def _header_line(text: str, group: int, line_number: int) -> str:
    underline = UNDERLINE_CHAR * max(len(text), UNDERLINE_MIN)
    return HEADER_FORMAT.format(group=group, line=line_number, underline=underline)


def _group_header(group: int, name: str | None, ranges: str) -> str:
    header = GROUP_FORMAT.format(group=group, ranges=ranges)
    return f"{header} {name}" if name else header


def render_output(model: DocumentModel) -> str:
    body_lines: list[str] = []
    group_line_numbers: dict[int, list[int]] = {}
    hg = model.header_group()

    for idx, line in enumerate(model.lines):
        body_lines.append(line.text)
        if line.group != 0:
            line_number = idx + 1
            if line.group == hg:
                body_lines.append(_header_line(line.text, line.group, line_number))
            else:
                body_lines.append(_mark_line(line.text, line.group, line_number))
                group_line_numbers.setdefault(line.group, []).append(line_number)

    used_groups = sorted(g for g in model.selected_groups() if g != hg)

    if not used_groups:
        return "\n".join(body_lines)

    summary_lines: list[str] = ["", SEPARATOR_LINE, ""]
    for group in used_groups:
        annotation = model.annotations.get(group)
        annotation_text = annotation.text if annotation else ""
        name = model.group_names.get(group)
        ranges = _encode_ranges(group_line_numbers.get(group, []))
        summary_lines.append(_group_header(group, name, ranges))
        summary_lines.append(annotation_text)
        summary_lines.append("")

    return "\n".join(body_lines + summary_lines)
