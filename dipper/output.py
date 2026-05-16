# Generates the annotated output format from the document model

from dipper.constants import (
    GROUP_FORMAT,
    MARK_FORMAT,
    META_FILEPATH_FORMAT,
    SEPARATOR_LINE,
    UNDERLINE_CHAR,
    UNDERLINE_MIN,
)
from dipper.model import DocumentModel


def format_range(start: int, end: int) -> str:
    return f"{start}-{end}" if start != end else str(start)


def encode_ranges(line_numbers: list[int]) -> str:
    # Compress 1-based line numbers into range notation, e.g. [1,2,3,7] → "1-3,7"
    if not line_numbers:
        return ""
    sorted_nums = sorted(line_numbers)
    ranges: list[str] = []
    start = end = sorted_nums[0]
    for num in sorted_nums[1:]:
        if num == end + 1:
            end = num
        else:
            ranges.append(format_range(start, end))
            start = end = num
    ranges.append(format_range(start, end))
    return ",".join(ranges)


def mark_line(text: str, group: int, line_number: int) -> str:
    underline = UNDERLINE_CHAR * max(len(text), UNDERLINE_MIN)
    return MARK_FORMAT.format(group=group, line=line_number, underline=underline)


def group_header(group: int, name: str | None, ranges: str) -> str:
    header = GROUP_FORMAT.format(group=group, ranges=ranges)
    return f"{header} {name}" if name else header


def collect(model: DocumentModel) -> tuple[list[str], dict[int, list[int]]]:
    """Return (body_lines, group_line_numbers) from the model."""
    body_lines: list[str] = []
    group_line_numbers: dict[int, list[int]] = {}
    for idx, line in enumerate(model.lines):
        body_lines.append(line.text)
        if line.group != 0:
            line_number = idx + 1
            body_lines.append(mark_line(line.text, line.group, line_number))
            group_line_numbers.setdefault(line.group, []).append(line_number)
    return body_lines, group_line_numbers


def build_summary(model: DocumentModel, group_line_numbers: dict[int, list[int]]) -> list[str]:
    used_groups = sorted(model.selected_groups())
    summary: list[str] = []
    for group in used_groups:
        annotation = model.annotations.get(group)
        annotation_text = annotation.text if annotation else ""
        name = model.group_names.get(group)
        ranges = encode_ranges(group_line_numbers.get(group, []))
        summary.append(group_header(group, name, ranges))
        summary.append(annotation_text)
        summary.append("")
    return summary


def render_full(
    model: DocumentModel, body_lines: list[str], group_line_numbers: dict[int, list[int]]
) -> str:
    if not model.selected_groups():
        return "\n".join(body_lines)
    summary_block = ["", SEPARATOR_LINE, ""] + build_summary(model, group_line_numbers)
    return "\n".join(body_lines + summary_block)


def render_selected_lines(model: DocumentModel) -> str:
    out: list[str] = []
    for idx, line in enumerate(model.lines):
        if line.group != 0:
            out.append(line.text)
            out.append(mark_line(line.text, line.group, idx + 1))
    return "\n".join(out)


def render_output(
    model: DocumentModel,
    lines: bool = False,
    summary: bool = False,
    filepath: str | None = None,
) -> str:
    meta = META_FILEPATH_FORMAT.format(filepath=filepath) if filepath else None
    body_lines, group_line_numbers = collect(model)

    if not lines and not summary:
        body = render_full(model, body_lines, group_line_numbers)
        return f"{meta}\n{body}" if meta else body

    content_parts: list[str] = []
    if lines:
        selected = render_selected_lines(model)
        if selected:
            content_parts.append(selected)
    if summary:
        summary_block = build_summary(model, group_line_numbers)
        if summary_block:
            content_parts.append("\n".join(summary_block))
    content = "\n\n".join(content_parts)
    return f"{meta}\n{content}" if meta else content
