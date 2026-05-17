"""Miscellaneous actions: reset state, undo, preset switching, open modals."""

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


def change_preset(app: ClipperApp, preset_name: str, group_csv: str) -> None:
    app._model.take_snapshot()
    app._model.reset()
    new_names = {
        idx: name.strip()
        for idx, name in enumerate(group_csv.split(","), start=1)
        if name.strip()
    }
    for idx, name in new_names.items():
        app._model.groups.set_name(idx, name)
    lv = app.line_view()
    lv.redraw_lines(range(len(app._model.lines)))
    app.refresh_status()
