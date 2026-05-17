"""Miscellaneous actions: reset state, undo, open groups overview modal."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dipper.view.app import ClipperApp

from dipper.view.modals import GroupsModal, HelpModal


def reset(app: ClipperApp) -> None:
    app._model.take_snapshot()
    app._model.reset()
    lv = app.line_view()
    line_count = len(app._model.lines)
    lv.redraw_lines(range(line_count))
    app.refresh_status()


def undo(app: ClipperApp) -> None:
    restored = app._model.undo()
    if restored:
        lv = app.line_view()
        line_count = len(app._model.lines)
        lv.redraw_lines(range(line_count))
        app.refresh_status()


def open_groups_overview(app: ClipperApp) -> None:
    app.push_screen(GroupsModal(app._model), lambda _: app.refresh_status())


def open_help(app: ClipperApp) -> None:
    app.push_screen(HelpModal())
