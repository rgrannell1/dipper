"""Main Textual application for dipper"""

from pathlib import Path
from typing import ClassVar

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label, ListView

from dipper.commons.colour import resolve_diff_colours, resolve_diff_marks
from dipper.commons.constants import ABORT_BATCH, PREV_FILE
from dipper.commons.highlight import highlighted_lines
from dipper.commons.loader import load_session
from dipper.commons.themes import DEFAULT_THEME, THEMES
from dipper.controller.actions import groups as groups_actions
from dipper.controller.actions import misc as misc_actions
from dipper.controller.actions import nav as nav_actions
from dipper.controller.actions import range_fill as range_fill_actions
from dipper.controller.actions import search as search_actions
from dipper.controller.actions import theme as theme_actions
from dipper.controller.output import render_json, render_output
from dipper.model.state import AppState, LineState
from dipper.model.state.search import SearchOverlays
from dipper.view.app_types import LastAction, RunArgs
from dipper.view.bindings import APP_BINDINGS
from dipper.view.providers import GroupProvider, PresetProvider, ThemeProvider
from dipper.view.render import status_bar_text
from dipper.view.widgets import LineListView


class ClipperApp(App):  # noqa: PLR0904
    """File annotation TUI."""

    TITLE = "dipper"
    COMMANDS: ClassVar[set] = {GroupProvider, PresetProvider, ThemeProvider}
    CSS_PATH = "app.tcss"

    BINDINGS: ClassVar[list[Binding]] = APP_BINDINGS

    def __init__(self, source: str, args: RunArgs) -> None:  # noqa: PLR0915
        super().__init__()
        theme_entry = THEMES.get(args.theme, THEMES[DEFAULT_THEME])
        self._model = AppState(
            lines=[LineState(text=line) for line in source.splitlines()],
            group_names=dict(args.group_names),
        )
        if args.load_path:
            self.apply_load(source, args.filename, args.load_path)
        self._source = source
        self._source_filename = args.filename
        self._hi_lines = highlighted_lines(source, args.filename, style=theme_entry["pygments"])
        self._filename = args.filename or "<stdin>"
        self._output_filepath = args.filename
        self._output_path = args.output_path
        self._header = args.header
        self._output_lines = args.output_lines
        self._output_summary = args.output_summary
        self._output_full = args.output_full
        self._output_json = args.output_json
        self._files_mode = args.files_mode
        self._presets = args.presets
        self.register_theme(theme_entry["textual"])
        self.theme = theme_entry["textual"].name
        self.sub_title = args.prompt or ""
        self._last_action: LastAction | None = None
        if args.diff_lines:
            line_colours = resolve_diff_colours(theme_entry["pygments"], args.diff_lines)
            line_marks = resolve_diff_marks(args.diff_lines)
            overlays = SearchOverlays(line_colours=line_colours, line_marks=line_marks)
            self._model.search.set("diff", sorted(line_colours), overlays=overlays)

    def apply_load(self, source: str, filename: str | None, load_path: str) -> None:
        """Restore line groups, names, and block annotations from a saved session."""
        session = load_session(source, filename, load_path)
        for line_num, grp in session.line_groups.items():
            idx = line_num - 1
            if 0 <= idx < len(self._model.lines):
                self._model.set_line_group(idx, grp)
        for grp, name in session.group_names.items():
            self._model.groups.set_name(grp, name)
        for (grp, block_start), text in session.block_annotations.items():
            if 0 <= block_start < len(self._model.lines):
                self._model.groups.set_annotation(grp, block_start, text)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        if self._header is not None:
            yield Label(self._header, id="header-label")
        yield LineListView(self._model, self._hi_lines)
        yield Label(status_bar_text(self._model, self._filename, 0), id="status")
        yield Footer()

    def on_mount(self) -> None:
        if self._files_mode:
            self.bind("ctrl+x", "abort_batch", description="Abort batch")
            self.bind("right_square_bracket", "write_output", description="Next file", show=True)
            self.bind("left_square_bracket", "prev_file", description="Prev file", show=True)

    def action_abort_batch(self) -> None:
        self.exit(ABORT_BATCH)

    def refresh_status(self) -> None:
        cursor_idx = self.line_view().cursor_index
        self.query_one("#status", Label).update(status_bar_text(self._model, self._filename, cursor_idx))

    def line_view(self) -> LineListView:
        return self.query_one(LineListView)

    def jump_to_line(self, idx: int) -> None:
        nav_actions.jump_to_line(self, idx)

    def set_group(self, group: int) -> None:
        groups_actions.set_group(self, group)

    def change_theme(self, theme_name: str) -> None:
        theme_actions.change_theme(self, theme_name)

    def change_preset(self, preset_name: str, group_csv: str) -> None:
        misc_actions.change_preset(self, preset_name, group_csv)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        self.refresh_status()

    def on_line_list_view_line_toggled(self, event: LineListView.LineToggled) -> None:
        cursor_idx = self.line_view().cursor_index
        line = self._model.lines[cursor_idx]
        if line.group != 0:
            self._last_action = LastAction(group=line.group, note=None)
        self.refresh_status()

    def on_key(self, event: events.Key) -> None:
        ch = event.character
        if ch == "g":
            nav_actions.jump_to_line(self, 0)
            event.stop()
        elif ch == "G":
            last_idx = len(self._model.lines) - 1
            nav_actions.jump_to_line(self, last_idx)
            event.stop()
        elif ch == "*":
            search_actions.select_all_matches(self)
            event.stop()

    def action_annotate(self) -> None:
        groups_actions.open_annotate(self)

    def action_rename_group(self) -> None:
        groups_actions.open_rename_group(self)

    def action_fill_range(self) -> None:
        range_fill_actions.fill_range(self)

    def rendered_output(self) -> str | None:
        """Render the current session to a string (JSON or annotated text)."""
        if self._output_json:
            return render_json(self._model, self._output_filepath)
        return render_output(
            self._model, lines=self._output_lines, summary=self._output_summary,
            full=self._output_full, filepath=self._output_filepath, source=self._source,
        )

    def write_current_file(self) -> None:
        if self._output_path:
            result = self.rendered_output()
            if result is not None:
                Path(self._output_path).write_text(result)

    def action_write_output(self) -> None:
        if self._files_mode:
            self.write_current_file()
            self.exit(None)
        else:
            self.exit(self.rendered_output())

    def action_prev_file(self) -> None:
        self.write_current_file()
        self.exit(PREV_FILE)

    def action_goto_line(self) -> None:
        nav_actions.open_goto_line(self)

    def action_search(self) -> None:
        search_actions.open_search(self)

    def action_next_match(self) -> None:
        search_actions.next_match(self)

    def action_prev_match(self) -> None:
        search_actions.prev_match(self)

    def action_next_block(self) -> None:
        nav_actions.next_block(self)

    def action_prev_block(self) -> None:
        nav_actions.prev_block(self)

    def action_reset(self) -> None:
        misc_actions.reset(self)

    def action_undo(self) -> None:
        misc_actions.undo(self)

    def action_groups_overview(self) -> None:
        misc_actions.open_groups_overview(self)

    def action_paste_last(self) -> None:
        groups_actions.paste_last(self)

    def action_help(self) -> None:
        misc_actions.open_help(self)


def run(source: str, args: RunArgs) -> tuple[str | None, dict[int, str]]:
    app = ClipperApp(source, args)
    result = app.run()
    final_group_names = dict(app._model.groups.names)
    if result and result not in {ABORT_BATCH, PREV_FILE}:
        if args.output_path:
            Path(args.output_path).write_text(result)
        else:
            print(result)
    return result, final_group_names
