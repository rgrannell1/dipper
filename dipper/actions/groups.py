"""Group management actions: set group, rename, annotate."""

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dipper.app import ClipperApp

from dipper.actions.nav import cursor_group
from dipper.modals import AnnotationModal, RenameModal
from dipper.state import selected_groups


def set_group(app: ClipperApp, group: int) -> None:
    old_anchor = app._model.range_fill.anchor
    app._model.active_group = group
    lv = app.line_view()
    if old_anchor is not None:
        lv.redraw_line(old_anchor)  # erase the anchor diamond now that the anchor is cleared
    app.refresh_status()


def rename_done(app: ClipperApp, group: int, result: str) -> None:
    app._model.groups.set_name(group, result)
    app.refresh_status()


def open_rename_group(app: ClipperApp) -> None:
    """Prefer the group under the cursor; fall back to active_group when cursor is on an unassigned line."""
    grp = cursor_group(app) or app._model.active_group
    existing = app._model.groups.names.get(grp, "")
    callback = functools.partial(rename_done, app, grp)
    app.push_screen(RenameModal(grp, existing), callback)


def annotate_done(app: ClipperApp, group: int, result: str) -> None:
    app._model.groups.set_annotation(group, result)
    app.refresh_status()


def open_annotate(app: ClipperApp) -> None:
    used = selected_groups(app._model.lines)
    if not used:
        return
    # Prefer annotating the active group if it has lines; otherwise fall back to the lowest used group.
    group = app._model.active_group if app._model.active_group in used else min(used)
    annotation = app._model.groups.annotations.get(group)
    existing = annotation.text if annotation else ""
    label = app._model.groups.label(group)
    callback = functools.partial(annotate_done, app, group)
    app.push_screen(AnnotationModal(group, label, existing), callback)
