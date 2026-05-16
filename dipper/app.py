# Main Textual application for dipper

import functools
import re as _re
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label, ListView
from textual import events

from dipper.highlight import highlighted_lines
from dipper.model import AppState
from dipper.state import LineState
from dipper.output import render_output
from dipper.modals import AnnotationModal, CommandModal, GroupsModal, RenameModal
from dipper.view import GroupProvider, LineListView, status_bar_text


class ClipperApp(App):
    """File annotation TUI."""

    TITLE = "dipper"
    COMMANDS = {GroupProvider}
    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding("n", "annotate", "Note"),
        Binding("r", "rename_group", "Rename"),
        Binding("f", "fill_range", "Fill range"),
        Binding("q", "write_output", "Write & quit"),
        Binding("colon", "goto_line", "Go to line"),
        Binding("slash", "search", "Search"),
        Binding("greater_than_sign", "next_match", "Next match", show=False, priority=True),
        Binding("less_than_sign", "prev_match", "Prev match", show=False, priority=True),
        Binding("x", "reset", "Reset", show=False),
        Binding("o", "groups_overview", "Groups"),
    ]

    def __init__(
        self,
        source: str,
        filename: str | None,
        prompt: str | None = None,
        header: str | None = None,
        group_names: dict[int, str] | None = None,
        output_lines: bool = False,
        output_summary: bool = False,
    ) -> None:
        super().__init__()
        lines = source.splitlines()
        self._model = AppState(
            lines=[LineState(text=line) for line in lines],
            group_names=dict(group_names or {}),
        )
        self._hi_lines = highlighted_lines(source, filename)
        self._filename = filename or "<stdin>"
        self._output_filepath = filename
        self._header = header
        self._output_lines = output_lines
        self._output_summary = output_summary
        if prompt is not None:
            self.sub_title = prompt

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        if self._header is not None:
            yield Label(self._header, id="header-label")
        yield LineListView(self._model, self._hi_lines)
        yield Label(status_bar_text(self._model, self._filename), id="status")
        yield Footer()

    def cursor_group(self) -> int:
        """Returns the group of the line under the cursor, or 0 if none."""
        try:
            idx = self.line_view().cursor_index
        except Exception:
            return 0
        return self._model.lines[idx].group if idx < len(self._model.lines) else 0

    def refresh_status(self) -> None:
        """Re-renders the status label from current model state."""
        self.query_one("#status", Label).update(status_bar_text(self._model, self._filename))

    def line_view(self) -> LineListView:
        """Returns the LineListView widget."""
        return self.query_one(LineListView)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        self.refresh_status()

    def on_line_list_view_line_toggled(self, event: LineListView.LineToggled) -> None:
        self.refresh_status()

    def rename_done(self, group: int, result: str) -> None:
        """Callback for RenameModal: commits the new group name to the model."""
        self._model.set_group_name(group, result)
        self.refresh_status()

    def action_rename_group(self) -> None:
        grp = self.cursor_group() or self._model.active_group
        existing = self._model.group_names.get(grp, "")
        callback = functools.partial(self.rename_done, grp)
        self.push_screen(RenameModal(grp, existing), callback)

    def annotate_done(self, group: int, result: str) -> None:
        """Callback for AnnotationModal: commits the note text to the model."""
        self._model.set_annotation(group, result)
        self.refresh_status()

    def action_annotate(self) -> None:
        used = self._model.selected_groups()
        if not used:
            return
        group = self._model.active_group if self._model.active_group in used else min(used)
        existing = self._model.annotations[group].text if group in self._model.annotations else ""
        label = self._model.group_label(group)
        callback = functools.partial(self.annotate_done, group)
        self.push_screen(AnnotationModal(group, label, existing), callback)

    def action_fill_range(self) -> None:
        lv = self.line_view()
        idx = lv.cursor_index
        if self._model.range_anchor is None:
            self._model.set_range_anchor(idx)
            lv.redraw_line(idx)
            self.refresh_status()
        else:
            affected = self._model.fill_range(idx)
            lv.redraw_lines(affected)
            self.refresh_status()

    def action_write_output(self) -> None:
        result = render_output(
            self._model, lines=self._output_lines, summary=self._output_summary,
            filepath=self._output_filepath,
        )
        self.exit(result)

    def jump_to_line(self, idx: int) -> None:
        """Moves the list cursor to idx and scrolls it into view."""
        lv = self.line_view()
        lv.index = idx
        lv.scroll_to_widget(lv.query_one(f"#l{idx}"))

    def noop(self) -> None:
        """No-op callable used as a command palette command when there is no target line."""
        pass

    def open_goto_line(self) -> None:
        """Opens the go-to-line command modal and jumps to the entered line number."""
        def on_result(value: str | None) -> None:
            if value is None:
                return
            try:
                n = int(value.strip())
                idx = max(0, min(n - 1, len(self._model.lines) - 1))
                self.jump_to_line(idx)
            except ValueError:
                pass
        self.push_screen(CommandModal(":"), on_result)

    def apply_clear_search(self, lv: LineListView) -> None:
        """Clears the active search and redraws previously highlighted lines."""
        old_matches = set(self._model.match_indices)
        self._model.clear_search()
        lv.redraw_lines(old_matches)
        self.refresh_status()

    def apply_search(self, lv: LineListView, value: str) -> None:
        """Compiles pattern, updates match state, redraws changed lines, jumps to first match."""
        try:
            pattern = _re.compile(value, _re.IGNORECASE)
        except _re.error:
            return
        old_matches = set(self._model.match_indices)
        indices = [idx for idx, line in enumerate(self._model.lines) if pattern.search(line.text)]
        self._model.set_search(value, indices)
        lv.redraw_lines(old_matches.symmetric_difference(set(indices)))
        self.refresh_status()
        if indices:
            self.jump_to_line(indices[0])

    def search_result(self, value: str | None) -> None:
        """Callback from the search modal: clears on empty input, applies pattern otherwise."""
        if value is None:
            return
        lv = self.line_view()
        if not value:
            self.apply_clear_search(lv)
        else:
            self.apply_search(lv, value)

    def next_match(self) -> None:
        """Advances the search cursor to the next match and scrolls to it."""
        idx = self._model.next_match()
        if idx is not None:
            self.jump_to_line(idx)
            self.refresh_status()

    def prev_match(self) -> None:
        """Retreats the search cursor to the previous match and scrolls to it."""
        idx = self._model.prev_match()
        if idx is not None:
            self.jump_to_line(idx)
            self.refresh_status()

    def select_all_matches(self) -> None:
        """Assigns all currently matched lines to the active group."""
        changed = self._model.select_all_matches()
        if changed:
            self.line_view().redraw_lines(changed)
            self.refresh_status()

    def action_goto_line(self) -> None:
        self.open_goto_line()

    def action_search(self) -> None:
        self.push_screen(CommandModal("/"), self.search_result)

    def action_next_match(self) -> None:
        self.next_match()

    def action_prev_match(self) -> None:
        self.prev_match()

    def on_key(self, event: events.Key) -> None:
        ch = event.character
        if ch == "g":
            self.jump_to_line(0)
            event.stop()
        elif ch == "G":
            self.jump_to_line(len(self._model.lines) - 1)
            event.stop()
        elif ch == "*":
            self.select_all_matches()
            event.stop()

    def action_reset(self) -> None:
        """Clears all group annotations and redraws every line."""
        self._model.reset()
        lv = self.line_view()
        lv.redraw_lines(range(len(self._model.lines)))
        self.refresh_status()

    def action_groups_overview(self) -> None:
        self.push_screen(GroupsModal(self._model), lambda _: self.refresh_status())

    def set_group(self, group: int) -> None:
        """Changes the active group, clearing any pending range-fill anchor."""
        old_anchor = self._model.range_anchor
        self._model.active_group = group  # validated; clears anchor
        lv = self.line_view()
        if old_anchor is not None:
            lv.redraw_line(old_anchor)
        self.refresh_status()


def run(
    source: str,
    filename: str | None,
    prompt: str | None = None,
    header: str | None = None,
    group_names: dict[int, str] | None = None,
    output_lines: bool = False,
    output_summary: bool = False,
    output_path: str | None = None,
) -> None:
    app = ClipperApp(
        source, filename, prompt=prompt, header=header,
        group_names=group_names, output_lines=output_lines, output_summary=output_summary,
    )
    result = app.run()
    if result:
        if output_path:
            from pathlib import Path
            Path(output_path).write_text(result)
        else:
            print(result)
