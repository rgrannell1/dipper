"""Range fill action: anchor a start line then fill to cursor on second press."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dipper.app import ClipperApp


def fill_range(app: ClipperApp) -> None:
    """First press sets the anchor; second press fills from anchor to cursor and clears it."""
    lv = app.line_view()
    idx = lv.cursor_index
    if app._model.range_fill.anchor is None:
        app._model.range_fill.set_anchor(idx, app._model.groups.active)
        lv.redraw_line(idx)
        app.refresh_status()
    else:
        affected = app._model.range_fill.fill(app._model.lines, idx, app._model.groups.active)
        lv.redraw_lines(affected)
        app.refresh_status()
