"""Theme switching action."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dipper.app import ClipperApp

from dipper.highlight import highlighted_lines
from dipper.themes import DEFAULT_THEME, THEMES


def change_theme(app: ClipperApp, theme_name: str) -> None:
    entry = THEMES.get(theme_name, THEMES[DEFAULT_THEME])
    new_hi_lines = highlighted_lines(app._source, app._source_filename, style=entry["pygments"])
    app._hi_lines = new_hi_lines
    lv = app.line_view()
    lv._hi_lines = new_hi_lines  # sync the view's reference
    app.register_theme(entry["textual"])
    app.theme = entry["textual"].name
    line_count = len(app._model.lines)
    lv.redraw_lines(range(line_count))
