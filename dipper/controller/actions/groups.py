"""Group management actions: set group, rename, annotate."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dipper.view.app import ClipperApp

from dipper.controller.actions.nav import cursor_group
from dipper.model.state import nearest_block, selected_groups
from dipper.view.modals import AnnotationModal, RenameModal


def set_group(app: ClipperApp, group: int) -> None:
    old_anchor = app._model.range_fill.anchor
    app._model.active_group = group
    lv = app.line_view()
    if old_anchor is not None:
        lv.redraw_line(old_anchor)  # erase the anchor diamond now that the anchor is cleared
    app.refresh_status()


def rename_done(app: ClipperApp, group: int, result: str) -> None:
    app._model.take_snapshot()
    app._model.groups.set_name(group, result)
    app.refresh_status()


def open_rename_group(app: ClipperApp) -> None:
    """Prefer the group under the cursor; fall back to active_group when cursor is on an unassigned line."""
    grp = cursor_group(app) or app._model.active_group
    name_map = app._model.groups.names
    existing = name_map.get(grp, "")
    callback = functools.partial(rename_done, app, grp)
    app.push_screen(RenameModal(grp, existing), callback)


def annotate_done(app: ClipperApp, group: int, block_start: int, result: str) -> None:
    app._model.take_snapshot()
    app._model.groups.set_annotation(group, block_start, result)
    app.refresh_status()


def find_annotate_target(app: ClipperApp) -> tuple[int, int, int, int] | None:
    """Return (group, block_start, start_line, end_line) for the block to annotate, or None."""
    used = selected_groups(app._model.lines)
    if not used:
        return None
    cursor_idx = app.line_view().cursor_index
    block = app._model.block_at(cursor_idx) or nearest_block(app._model.lines, cursor_idx)
    if block is None:
        return None
    group, block_start = block
    all_blocks = app._model.blocks(group)
    block_bounds = next(span for span in all_blocks if span[0] == block_start)
    return group, block_start, block_bounds[0] + 1, block_bounds[1] + 1


def open_annotate(app: ClipperApp) -> None:
    """Open annotation modal for the block at or nearest to the cursor."""
    target = find_annotate_target(app)
    if target is None:
        return
    group, block_start, start_line, end_line = target
    existing = app._model.groups.block_annotation(group, block_start)
    label = app._model.groups.label(group)
    callback = functools.partial(annotate_done, app, group, block_start)
    app.push_screen(AnnotationModal(group, label, existing, (start_line, end_line)), callback)
