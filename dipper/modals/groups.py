# Modal showing all nine groups for bulk name management.

import functools
from pathlib import Path
from typing import ClassVar

from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import ListView, Static

from dipper.constants import GROUP_COUNT
from dipper.modals.rename import RenameModal
from dipper.model import AppState
from dipper.view import group_row_item, group_row_text


class GroupsModal(ModalScreen[None]):
    """Overview of all nine groups: shows names and line counts, supports inline rename and clear."""

    BINDINGS: ClassVar[list[Binding]] = [Binding("escape", "dismiss", "Close")]
    CSS_PATH = str(Path(__file__).parent / "groups.tcss")

    def __init__(self, model: AppState) -> None:
        super().__init__()
        self._model = model

    def compose(self) -> ComposeResult:
        yield ListView(*[group_row_item(self._model, grp) for grp in range(1, GROUP_COUNT + 1)], id="groups-list")

    def redraw_row(self, group: int) -> None:
        self.query_one(f"#gs-{group}", Static).update(group_row_text(self._model, group))

    def focused_group(self) -> int | None:
        lv = self.query_one("#groups-list", ListView)
        if lv.index is None:
            return None
        return lv.index + 1

    def rename_done(self, group: int, name: str) -> None:
        self._model.set_group_name(group, name)
        self.redraw_row(group)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        group = self.focused_group()
        if group is None:
            return
        existing = self._model.group_names.get(group, "")
        callback = functools.partial(self.rename_done, group)
        self.app.push_screen(RenameModal(group, existing), callback)

    def on_key(self, event: events.Key) -> None:
        if event.key != "x":
            return
        group = self.focused_group()
        if group is None:
            return
        self._model.set_group_name(group, "")
        self.redraw_row(group)
        event.stop()
