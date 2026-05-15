# Generates the annotated output format from the document model

from clipper.constants import (
    GROUP_FORMAT,
    MARK_FORMAT,
    SEPARATOR_LINE,
    UNDERLINE_CHAR,
    UNDERLINE_MIN,
)
from clipper.model import DocumentModel


def _mark_line(text: str, group: int) -> str:
    underline = UNDERLINE_CHAR * max(len(text), UNDERLINE_MIN)
    return MARK_FORMAT.format(group=group, underline=underline)


def _group_header(group: int, name: str | None) -> str:
    header = GROUP_FORMAT.format(group=group)
    return f"{header} {name}" if name else header


def render_output(model: DocumentModel) -> str:
    body_lines: list[str] = []

    for line in model.lines:
        body_lines.append(line.text)
        if line.group != 0:
            body_lines.append(_mark_line(line.text, line.group))

    used_groups = sorted(model.selected_groups())

    if not used_groups:
        return "\n".join(body_lines)

    summary_lines: list[str] = ["", SEPARATOR_LINE, ""]
    for group in used_groups:
        annotation = model.annotations.get(group)
        annotation_text = annotation.text if annotation else ""
        name = model.group_names.get(group)
        summary_lines.append(_group_header(group, name))
        summary_lines.append(annotation_text)
        summary_lines.append("")

    return "\n".join(body_lines + summary_lines)
