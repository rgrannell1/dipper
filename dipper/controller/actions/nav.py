"""Navigation actions: jump to line, cursor group query, goto-line modal."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dipper.view.app import ClipperApp

from textual.css.query import NoMatches

from dipper.model.state.queries import next_block_start, next_diff_hunk_start, prev_block_start, prev_diff_hunk_start
from dipper.view.modals import CommandModal


def jump_to_line(app: ClipperApp, idx: int) -> None:
    line_count = len(app._model.lines)
    if line_count == 0 or not (0 <= idx < line_count):
        return
    lv = app.line_view()
    lv.index = idx
    lv.scroll_to_widget(lv.query_one(f"#l{idx}"))


def cursor_group(app: ClipperApp) -> int:
    """Returns 0 when the view isn't mounted yet or the cursor sits on an unassigned line."""
    try:
        idx = app.line_view().cursor_index
    except NoMatches:
        return 0
    lines = app._model.lines
    return lines[idx].group if idx < len(lines) else 0


def next_block(app: ClipperApp) -> None:
    """Jump to the next group block start, falling back to diff hunk starts."""
    cursor = app.line_view().cursor_index
    idx = next_block_start(app._model.lines, cursor)
    if idx is None:
        idx = next_diff_hunk_start(app._model.search.indices, cursor)
    if idx is not None:
        jump_to_line(app, idx)


def prev_block(app: ClipperApp) -> None:
    """Jump to the previous group block start, falling back to diff hunk starts."""
    cursor = app.line_view().cursor_index
    idx = prev_block_start(app._model.lines, cursor)
    if idx is None:
        idx = prev_diff_hunk_start(app._model.search.indices, cursor)
    if idx is not None:
        jump_to_line(app, idx)


def open_goto_line(app: ClipperApp) -> None:
    def on_result(value: str | None) -> None:
        if value is None:
            return
        try:
            line_num = int(value.strip())
            last = len(app._model.lines) - 1
            idx = max(0, min(line_num - 1, last))
            jump_to_line(app, idx)
        except ValueError:
            pass
    app.push_screen(CommandModal(":"), on_result)
