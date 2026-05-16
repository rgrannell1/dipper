# Main Textual application for dipper

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Label, ListView
from textual import events

from dipper.highlight import highlighted_lines
from dipper.model import AppState
from dipper.state import LineState
from dipper.output import render_output
from dipper.themes import THEMES, DEFAULT_THEME
from dipper.view import GroupProvider, LineListView, ThemeProvider, status_bar_text
from dipper import actions


class ClipperApp(App):
    """File annotation TUI."""

    TITLE = "dipper"
    COMMANDS = {GroupProvider, ThemeProvider}
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
        Binding("x", "reset", "Reset"),
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
        theme: str = DEFAULT_THEME,
    ) -> None:
        super().__init__()
        theme_entry = THEMES.get(theme, THEMES[DEFAULT_THEME])
        lines = source.splitlines()
        self._model = AppState(
            lines=[LineState(text=line) for line in lines],
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
        if prompt is not None:
            self.sub_title = prompt

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
        actions.jump_to_line(self, idx)

    def set_group(self, group: int) -> None:
        actions.set_group(self, group)

    def noop(self) -> None:
        pass

    def change_theme(self, theme_name: str) -> None:
        actions.change_theme(self, theme_name)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        self.refresh_status()

    def on_line_list_view_line_toggled(self, event: LineListView.LineToggled) -> None:
        self.refresh_status()

    def on_key(self, event: events.Key) -> None:
        ch = event.character
        if ch == "g":
            actions.jump_to_line(self, 0)
            event.stop()
        elif ch == "G":
            last_idx = len(self._model.lines) - 1
            actions.jump_to_line(self, last_idx)
            event.stop()
        elif ch == "*":
            actions.select_all_matches(self)
            event.stop()

    def action_annotate(self) -> None:
        actions.open_annotate(self)

    def action_rename_group(self) -> None:
        actions.open_rename_group(self)

    def action_fill_range(self) -> None:
        actions.fill_range(self)

    def action_write_output(self) -> None:
        result = render_output(
            self._model, lines=self._output_lines, summary=self._output_summary,
            filepath=self._output_filepath,
        )
        self.exit(result)

    def action_goto_line(self) -> None:
        actions.open_goto_line(self)

    def action_search(self) -> None:
        actions.open_search(self)

    def action_next_match(self) -> None:
        actions.next_match(self)

    def action_prev_match(self) -> None:
        actions.prev_match(self)

    def action_reset(self) -> None:
        actions.reset(self)

    def action_groups_overview(self) -> None:
        actions.open_groups_overview(self)


def run(
    source: str,
    filename: str | None,
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
            from pathlib import Path
            Path(output_path).write_text(result)
        else:
            print(result)
