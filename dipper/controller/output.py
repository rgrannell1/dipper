"""Generates the annotated output format from the document model"""

import json

from dipper.commons.constants import (
    GROUP_FORMAT,
    MARK_FORMAT,
    META_FILEPATH_FORMAT,
    META_HASH_FORMAT,
    SEPARATOR_LINE,
    UNDERLINE_CHAR,
    UNDERLINE_MIN,
)
from dipper.commons.hash import source_hash
from dipper.model.state import DocumentModel, selected_groups


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


def prepend_meta(text: str, meta: str | None) -> str:
    return f"{meta}\n{text}" if meta else text


def collect(model: DocumentModel) -> tuple[list[str], dict[int, list[int]]]:
    """Return (body_lines, group_line_numbers) from the model."""
    body_lines: list[str] = []
    group_line_numbers: dict[int, list[int]] = {}
    for idx, line in enumerate(model.lines):
        body_lines.append(line.text)
        if line.group != 0:
            line_number = idx + 1
            # underline marker so downstream tooling can locate each annotated line
            body_lines.append(mark_line(line.text, line.group, line_number))
            group_line_numbers.setdefault(line.group, []).append(line_number)
    return body_lines, group_line_numbers


def build_summary(model: DocumentModel) -> list[str]:
    """Build the summary block with one entry per block, sorted by start line."""
    entries: list[tuple[int, int, str | None, str, str]] = []
    for group in sorted(selected_groups(model.lines)):
        name = model.groups.names.get(group)
        for start_idx, end_idx in model.blocks(group):
            line_numbers = list(range(start_idx + 1, end_idx + 2))
            ranges = encode_ranges(line_numbers)
            annotation_text = model.groups.block_annotation(group, start_idx)
            entries.append((start_idx, group, name, ranges, annotation_text))

    entries.sort(key=lambda entry: entry[0])

    summary: list[str] = []
    for _, group, name, ranges, annotation_text in entries:
        summary.append(group_header(group, name, ranges))
        summary.append(annotation_text)
        summary.append("")
    return summary


def render_full(model: DocumentModel, body_lines: list[str]) -> str:
    if not selected_groups(model.lines):
        return "\n".join(body_lines)
    summary_block = ["", SEPARATOR_LINE, "", *build_summary(model)]
    return "\n".join(body_lines + summary_block)


def render_selected_lines(model: DocumentModel) -> str:
    out: list[str] = []
    for idx, line in enumerate(model.lines):
        if line.group != 0:
            out.append(line.text)
            out.append(mark_line(line.text, line.group, idx + 1))
    return "\n".join(out)


def render_filtered(
    model: DocumentModel,
    lines: bool,
    summary: bool,
) -> str:
    """Render only the requested sections (selected lines, summary, or both)."""
    content_parts: list[str] = []
    if lines:
        selected = render_selected_lines(model)
        if selected:
            content_parts.append(selected)
    if summary:
        summary_block = build_summary(model)
        if summary_block:
            content_parts.append("\n".join(summary_block))
    return "\n\n".join(content_parts)


def render_json(model: DocumentModel, filepath: str | None) -> str:
    """Emit a JSON object with filepath and group data; mutually exclusive with text modes."""
    groups: dict[str, object] = {}
    for group in sorted(selected_groups(model.lines)):
        name = model.groups.names.get(group, f"group {group}")
        line_nums = sorted(idx + 1 for idx, line in enumerate(model.lines) if line.group == group)
        # Collect annotations across all blocks for this group
        block_texts = [
            model.groups.block_annotation(group, start_idx)
            for start_idx, _ in model.blocks(group)
            if model.groups.block_annotation(group, start_idx)
        ]
        annotation = block_texts[0] if len(block_texts) == 1 else ("; ".join(block_texts) if block_texts else None)
        groups[str(group)] = {"name": name, "annotation": annotation, "lines": line_nums}
    return json.dumps({"filepath": filepath, "groups": groups}, indent=2)


def render_output(  # noqa: PLR0913, PLR0917
    model: DocumentModel,
    lines: bool = False,
    summary: bool = False,
    full: bool = False,
    filepath: str | None = None,
    source: str | None = None,
) -> str:
    filepath_meta = META_FILEPATH_FORMAT.format(filepath=filepath) if filepath else None  # type: ignore
    hash_meta = META_HASH_FORMAT.format(hash=source_hash(source)) if source else None
    meta = "\n".join(part for part in [filepath_meta, hash_meta] if part) or None
    body_lines, _ = collect(model)

    if full:
        return prepend_meta(render_full(model, body_lines), meta)

    if lines or summary:
        return prepend_meta(render_filtered(model, lines, summary), meta)

    # default: compact — selected lines + marks, then summary block
    return prepend_meta(render_filtered(model, lines=True, summary=True), meta)
