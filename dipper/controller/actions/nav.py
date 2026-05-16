"""Navigation actions: jump to line, cursor group query, goto-line modal."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dipper.view.app import ClipperApp

from textual.css.query import NoMatches

from dipper.view.modals import CommandModal


def jump_to_line(app: ClipperApp, idx: int) -> None:
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
