"""Main Textual application for dipper"""

from pathlib import Path
from typing import ClassVar

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label, ListView

from dipper.commons.highlight import highlighted_lines
from dipper.commons.themes import DEFAULT_THEME, THEMES
from dipper.controller.actions import groups as groups_actions
from dipper.controller.actions import misc as misc_actions
from dipper.controller.actions import nav as nav_actions
from dipper.controller.actions import range_fill as range_fill_actions
from dipper.controller.actions import search as search_actions
from dipper.controller.actions import theme as theme_actions
from dipper.controller.output import render_output
from dipper.model.state import AppState, LineState
from dipper.view.bindings import APP_BINDINGS
from dipper.view.providers import GroupProvider, ThemeProvider
from dipper.view.render import status_bar_text
from dipper.view.widgets import LineListView


class ClipperApp(App):
    """File annotation TUI."""

    TITLE = "dipper"
    COMMANDS: ClassVar[set] = {GroupProvider, ThemeProvider}
    CSS_PATH = "app.tcss"

    BINDINGS: ClassVar[list[Binding]] = APP_BINDINGS

    def __init__(  # noqa: PLR0913
        self,
        source: str,
        filename: str | None,
        *,
        prompt: str | None = None,
        header: str | None = None,
        group_names: dict[int, str] | None = None,
        output_lines: bool = False,
        output_summary: bool = False,
        theme: str = DEFAULT_THEME,
    ) -> None:
        super().__init__()
        theme_entry = THEMES.get(theme, THEMES[DEFAULT_THEME])
        self._model = AppState(
            lines=[LineState(text=line) for line in source.splitlines()],
            group_names=dict(group_names or {}),
        )
        self._source = source
        self._source_filename = filename
        self._hi_lines = highlighted_lines(source, filename, style=theme_entry["pygments"])
        self._filename = filename or "<stdin>"
        self._output_filepath = filename
        self._header = header
        self._output_lines = output_lines
        self._output_summary = output_summary
        self.register_theme(theme_entry["textual"])
        self.theme = theme_entry["textual"].name
        self.sub_title = prompt or ""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        if self._header is not None:
            yield Label(self._header, id="header-label")
        yield LineListView(self._model, self._hi_lines)
        yield Label(status_bar_text(self._model, self._filename), id="status")
        yield Footer()

    def refresh_status(self) -> None:
        self.query_one("#status", Label).update(status_bar_text(self._model, self._filename))

    def line_view(self) -> LineListView:
        return self.query_one(LineListView)

    def jump_to_line(self, idx: int) -> None:
        nav_actions.jump_to_line(self, idx)

    def set_group(self, group: int) -> None:
        groups_actions.set_group(self, group)

    def change_theme(self, theme_name: str) -> None:
        theme_actions.change_theme(self, theme_name)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        self.refresh_status()

    def on_line_list_view_line_toggled(self, event: LineListView.LineToggled) -> None:
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

    def action_write_output(self) -> None:
        result = render_output(
            self._model, lines=self._output_lines, summary=self._output_summary,
            filepath=self._output_filepath,
        )
        self.exit(result)

    def action_goto_line(self) -> None:
        nav_actions.open_goto_line(self)

    def action_search(self) -> None:
        search_actions.open_search(self)

    def action_next_match(self) -> None:
        search_actions.next_match(self)

    def action_prev_match(self) -> None:
        search_actions.prev_match(self)

    def action_reset(self) -> None:
        misc_actions.reset(self)

    def action_groups_overview(self) -> None:
        misc_actions.open_groups_overview(self)


def run(  # noqa: PLR0913
    source: str,
    filename: str | None,
    *,
    prompt: str | None = None,
    header: str | None = None,
    group_names: dict[int, str] | None = None,
    output_lines: bool = False,
    output_summary: bool = False,
    output_path: str | None = None,
    theme: str = DEFAULT_THEME,
) -> None:
    app = ClipperApp(
        source, filename, prompt=prompt, header=header,
        group_names=group_names, output_lines=output_lines, output_summary=output_summary,
        theme=theme,
    )
    result = app.run()
    if result:
        if output_path:
            Path(output_path).write_text(result)
        else:
            print(result)
