"""Search actions: apply search, clear search, navigate matches, select all matches."""

from __future__ import annotations

import functools
import re as regex_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dipper.view.app import ClipperApp

from dipper.controller.actions.nav import jump_to_line
from dipper.view.modals import CommandModal
from dipper.view.widgets import LineListView


def apply_clear_search(app: ClipperApp, lv: LineListView) -> None:
    old_matches = set(app._model.search.indices)
    app._model.search.clear()
    lv.redraw_lines(old_matches)
    app.refresh_status()


def apply_search(app: ClipperApp, lv: LineListView, value: str) -> None:
    try:
        pattern = regex_module.compile(value, regex_module.IGNORECASE)
    except regex_module.error:
        return
    old_matches = set(app._model.search.indices)
    indices = [idx for idx, line in enumerate(app._model.lines) if pattern.search(line.text)]
    app._model.search.set(value, indices)
    lv.redraw_lines(old_matches.symmetric_difference(set(indices)))  # redraw only lines whose match status changed
    app.refresh_status()
    if indices:
        jump_to_line(app, indices[0])


def search_result(app: ClipperApp, value: str | None) -> None:
    """None means the modal was dismissed without submitting; empty string means clear the search."""
    if value is None:
        return
    lv = app.line_view()
    if not value:
        apply_clear_search(app, lv)
    else:
        apply_search(app, lv, value)


def open_search(app: ClipperApp) -> None:
    callback = functools.partial(search_result, app)
    app.push_screen(CommandModal("/"), callback)


def next_match(app: ClipperApp) -> None:
    idx = app._model.search.advance()
    if idx is not None:
        jump_to_line(app, idx)
        app.refresh_status()


def prev_match(app: ClipperApp) -> None:
    idx = app._model.search.retreat()
    if idx is not None:
        jump_to_line(app, idx)
        app.refresh_status()


def select_all_matches(app: ClipperApp) -> None:
    changed = app._model.search.select_all(app._model.lines, app._model.groups.active)
    if changed:
        app.line_view().redraw_lines(changed)
        app.refresh_status()
