# Action logic for ClipperApp — plain functions taking app as first argument.

from __future__ import annotations

import functools
import re as _re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dipper.app import ClipperApp

from textual.css.query import NoMatches

from dipper.highlight import highlighted_lines
from dipper.modals import AnnotationModal, CommandModal, GroupsModal, RenameModal
from dipper.themes import DEFAULT_THEME, THEMES
from dipper.widgets import LineListView


def jump_to_line(app: ClipperApp, idx: int) -> None:
    lv = app.line_view()
    lv.index = idx
    lv.scroll_to_widget(lv.query_one(f"#l{idx}"))


def cursor_group(app: ClipperApp) -> int:
    # Returns 0 when the view isn't mounted yet or the cursor sits on an unassigned line.
    try:
        idx = app.line_view().cursor_index
    except NoMatches:
        return 0
    lines = app._model.lines
    return lines[idx].group if idx < len(lines) else 0


def set_group(app: ClipperApp, group: int) -> None:
    old_anchor = app._model.range_anchor
    app._model.active_group = group
    lv = app.line_view()
    if old_anchor is not None:
        lv.redraw_line(old_anchor)  # erase the anchor diamond now that the anchor is cleared
    app.refresh_status()


def rename_done(app: ClipperApp, group: int, result: str) -> None:
    app._model.set_group_name(group, result)
    app.refresh_status()


def open_rename_group(app: ClipperApp) -> None:
    # Prefer the group under the cursor; fall back to active_group when cursor is on an unassigned line.
    grp = cursor_group(app) or app._model.active_group
    existing = app._model.group_names.get(grp, "")
    callback = functools.partial(rename_done, app, grp)
    app.push_screen(RenameModal(grp, existing), callback)


def annotate_done(app: ClipperApp, group: int, result: str) -> None:
    app._model.set_annotation(group, result)
    app.refresh_status()


def open_annotate(app: ClipperApp) -> None:
    used = app._model.selected_groups()
    if not used:
        return
    # Prefer annotating the active group if it has lines; otherwise fall back to the lowest used group.
    group = app._model.active_group if app._model.active_group in used else min(used)
    annotation = app._model.annotations.get(group)
    existing = annotation.text if annotation else ""
    label = app._model.group_label(group)
    callback = functools.partial(annotate_done, app, group)
    app.push_screen(AnnotationModal(group, label, existing), callback)


def fill_range(app: ClipperApp) -> None:
    # First press sets the anchor; second press fills from anchor to cursor and clears it.
    lv = app.line_view()
    idx = lv.cursor_index
    if app._model.range_anchor is None:
        app._model.set_range_anchor(idx)
        lv.redraw_line(idx)
        app.refresh_status()
    else:
        affected = app._model.fill_range(idx)
        lv.redraw_lines(affected)
        app.refresh_status()


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


def apply_clear_search(app: ClipperApp, lv: LineListView) -> None:
    old_matches = set(app._model.match_indices)
    app._model.clear_search()
    lv.redraw_lines(old_matches)
    app.refresh_status()


def apply_search(app: ClipperApp, lv: LineListView, value: str) -> None:
    try:
        pattern = _re.compile(value, _re.IGNORECASE)
    except _re.error:
        return
    old_matches = set(app._model.match_indices)
    indices = [idx for idx, line in enumerate(app._model.lines) if pattern.search(line.text)]
    app._model.set_search(value, indices)
    lv.redraw_lines(old_matches.symmetric_difference(set(indices)))  # redraw only lines whose match status changed
    app.refresh_status()
    if indices:
        jump_to_line(app, indices[0])


def search_result(app: ClipperApp, value: str | None) -> None:
    # None means the modal was dismissed without submitting; empty string means clear the search.
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
    idx = app._model.next_match()
    if idx is not None:
        jump_to_line(app, idx)
        app.refresh_status()


def prev_match(app: ClipperApp) -> None:
    idx = app._model.prev_match()
    if idx is not None:
        jump_to_line(app, idx)
        app.refresh_status()


def select_all_matches(app: ClipperApp) -> None:
    changed = app._model.select_all_matches()
    if changed:
        app.line_view().redraw_lines(changed)
        app.refresh_status()


def reset(app: ClipperApp) -> None:
    app._model.reset()
    lv = app.line_view()
    line_count = len(app._model.lines)
    lv.redraw_lines(range(line_count))
    app.refresh_status()


def open_groups_overview(app: ClipperApp) -> None:
    app.push_screen(GroupsModal(app._model), lambda _: app.refresh_status())


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
