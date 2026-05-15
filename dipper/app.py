# Main Textual application for clipper

import functools
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.command import Provider, Hit, Hits
from textual.message import Message
from textual.widgets import Footer, Header, Label, ListView, ListItem, Static
from textual import events

from rich.text import Text
from rich.style import Style

from dipper.constants import GROUP_COLOURS, WRITE_KEY
from dipper.highlight import highlighted_lines
from dipper.model import DocumentModel, LineState
from dipper.output import render_output
from dipper.widgets import AnnotationModal, CommandModal, RenameModal


class GroupProvider(Provider):
    """Command palette provider showing all active groups with names and notes."""

    async def search(self, query: str) -> Hits:
        app: ClipperApp = self.app  # type: ignore
        model = app._model
        used = sorted(model.selected_groups())
        matcher = self.matcher(query)

        for group in used:
            label = model.group_label(group)
            annotation = model.annotations.get(group)
            note = annotation.text if annotation else ""
            colour = GROUP_COLOURS[group]

            searchable = f"group {group}: {label}  {note}"
            score = matcher.match(searchable) if query else 1.0
            if score == 0:
                continue

            display = Text()
            display.append("● ", style=Style(color=colour, bold=True))
            display.append(f"group {group}: ", style="dim")
            display.append(label, style=Style(color=colour, bold=True))
            if note:
                display.append(f"  —  {note}", style="dim")

            first_line = next(
                (idx for idx, line in enumerate(model.lines) if line.group == group), None
            )
            command = functools.partial(app._jump_to_line, first_line) if first_line is not None else app._noop

            yield Hit(score=score, match_display=display, command=command)


class LineListView(ListView):
    """Annotatable line list backed by Textual ListView."""

    class LineToggled(Message):
        pass

    BINDINGS = [
        Binding("tab", "toggle_line", "Select line", priority=True),
    ]


    def __init__(self, model: DocumentModel, hi_lines: list[str]) -> None:
        self._model = model
        self._hi_lines = hi_lines
        self._gutter_width = len(str(len(hi_lines))) + 1
        self._match_indices: set[int] = set()
        items = [
            ListItem(Static(self._line_text(idx), markup=False), id=f"l{idx}")
            for idx in range(len(hi_lines))
        ]
        super().__init__(*items)

    def _line_text(self, idx: int) -> Text:
        line = self._model.lines[idx]
        hi_text = Text.from_ansi(self._hi_lines[idx])

        if line.group != 0:
            colour = GROUP_COLOURS[line.group]
            hi_text.stylize(f"bold {colour}")

        line_num = str(idx + 1).rjust(self._gutter_width)
        gutter_style = "bold yellow" if idx in self._match_indices else "dim"
        gutter = Text(f"{line_num} ", style=gutter_style)

        if line.group != 0:
            colour = GROUP_COLOURS[line.group]
            indicator = Text("● ", style=f"bold {colour}")
        else:
            indicator = Text("  ")

        return Text.assemble(gutter, indicator, hi_text)

    def _redraw_line(self, idx: int) -> None:
        self.query_one(f"#l{idx} Static", Static).update(self._line_text(idx))

    def set_matches(self, indices: set[int]) -> None:
        old = self._match_indices
        self._match_indices = indices
        for idx in old.symmetric_difference(indices):
            self._redraw_line(idx)

    def action_toggle_line(self) -> None:
        idx = self.index
        if idx is None:
            return
        self._model.toggle_line(idx)
        self._redraw_line(idx)
        self.post_message(self.LineToggled())

    @property
    def cursor_index(self) -> int:
        return self.index if self.index is not None else 0





class ClipperApp(App):
    """File annotation TUI."""

    TITLE = "dipper"
    COMMANDS = {GroupProvider}

    BINDINGS = [
        Binding("n", "annotate", "Note"),
        Binding("r", "rename_group", "Rename"),
        Binding(WRITE_KEY, "write_output", "Write & quit"),
        Binding("q", "quit_no_output", "Quit"),
        Binding("colon", "goto_line", "Go to line"),
        Binding("slash", "search", "Search"),
        Binding("greater_than_sign", "next_match", "Next match", show=False, priority=True),
        Binding("less_than_sign", "prev_match", "Prev match", show=False, priority=True),
        *[Binding(str(grp), f"set_group_{grp}", show=False, priority=True) for grp in range(1, 10)],
    ]

    CSS = """
    LineListView {
        height: 1fr;
    }
    #header-label {
        height: 1;
        background: $panel;
        padding: 0 1;
        color: $text-muted;
    }
    #status {
        height: 1;
        background: $panel;
        padding: 0 1;
    }
    """

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
        self._model = DocumentModel(
            lines=[LineState(text=line) for line in lines],
            group_names=dict(group_names or {}),
        )
        self._hi_lines = highlighted_lines(source, filename)
        self._filename = filename or "<stdin>"
        self._header = header
        self._output_lines = output_lines
        self._output_summary = output_summary
        self._search_pattern: str = ""
        self._match_indices: list[int] = []
        self._match_cursor: int = 0
        if prompt is not None:
            self.sub_title = prompt

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        if self._header is not None:
            yield Label(self._header, id="header-label")
        yield LineListView(self._model, self._hi_lines)
        yield Label(self._status_text(), id="status")
        yield Footer()

    def _cursor_group(self) -> int:
        try:
            idx = self._line_view().cursor_index
        except Exception:
            return 0
        return self._model.lines[idx].group if idx < len(self._model.lines) else 0

    def _status_text(self) -> Text:
        active = self._model.active_group
        used = sorted(self._model.selected_groups())
        result = Text(no_wrap=True, overflow="ellipsis")

        for grp in used:
            colour = GROUP_COLOURS[grp]
            dot = "◉" if grp == active else "●"
            result.append(dot, style=Style(color=colour, bold=True))
            result.append(" ")

        try:
            cursor = self._line_view().cursor_index
        except Exception:
            cursor = 0

        nearest = self._model.nearest_group(cursor)
        if nearest is not None:
            colour = GROUP_COLOURS[nearest]
            label = self._model.group_label(nearest)
            result.append("  |  ", style="dim")
            result.append(label, style=Style(color=colour, bold=True))
            annotation = self._model.annotations.get(nearest)
            if annotation and annotation.text:
                result.append("  ", style="dim")
                result.append(annotation.text, style="dim")
                result.append("  |  edit", style="dim")

        if self._search_pattern:
            if self._match_indices:
                pos = self._match_cursor + 1
                total = len(self._match_indices)
                result.append(f"  |  /{self._search_pattern} [{pos}/{total}]", style="bold yellow")
            else:
                result.append(f"  |  /{self._search_pattern} [no matches]", style="dim yellow")

        result.append(f"  |  {self._filename}", style="dim")
        return result

    def _refresh_status(self) -> None:
        self.query_one("#status", Label).update(self._status_text())

    def _line_view(self) -> LineListView:
        return self.query_one(LineListView)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        self._refresh_status()

    def on_line_list_view_line_toggled(self, event: LineListView.LineToggled) -> None:
        self._refresh_status()

    def _on_rename_dismiss(self, group: int, result: str) -> None:
        if result:
            self._model.group_names[group] = result
        else:
            self._model.group_names.pop(group, None)
        self._refresh_status()

    def action_rename_group(self) -> None:
        grp = self._cursor_group() or self._model.active_group
        existing = self._model.group_names.get(grp, "")
        callback = functools.partial(self._on_rename_dismiss, grp)
        self.push_screen(RenameModal(grp, existing), callback)

    def _on_annotate_dismiss(self, group: int, result: str) -> None:
        if result:
            self._model.set_annotation(group, result)
        else:
            self._model.annotations.pop(group, None)
        self._refresh_status()

    def action_annotate(self) -> None:
        used = self._model.selected_groups()
        if not used:
            return
        group = self._model.active_group if self._model.active_group in used else min(used)
        existing = self._model.annotations[group].text if group in self._model.annotations else ""
        callback = functools.partial(self._on_annotate_dismiss, group)
        self.push_screen(AnnotationModal(group, existing), callback)

    def action_write_output(self) -> None:
        self.exit(render_output(self._model, lines=self._output_lines, summary=self._output_summary))

    def action_quit_no_output(self) -> None:
        self.exit(None)

    def _jump_to_line(self, idx: int) -> None:
        lv = self._line_view()
        lv.index = idx
        lv.scroll_to_widget(lv.query_one(f"#l{idx}"))

    def _noop(self) -> None:
        pass

    def on_line_list_view_group_selected(self, event: LineListView.GroupSelected) -> None:
        self._refresh_status()

    def _open_goto_line(self) -> None:
        def on_result(value: str | None) -> None:
            if value is None:
                return
            try:
                n = int(value.strip())
                idx = max(0, min(n - 1, len(self._model.lines) - 1))
                self._jump_to_line(idx)
            except ValueError:
                pass
        self.push_screen(CommandModal(":"), on_result)

    def _open_search(self) -> None:
        import re as _re

        def on_result(value: str | None) -> None:
            if value is None:
                return
            if not value:
                self._search_pattern = ""
                self._match_indices = []
                self._match_cursor = 0
                self._line_view().set_matches(set())
                self._refresh_status()
                return
            try:
                pattern = _re.compile(value, _re.IGNORECASE)
            except _re.error:
                return
            self._search_pattern = value
            self._match_indices = [
                idx for idx, line in enumerate(self._model.lines)
                if pattern.search(line.text)
            ]
            self._match_cursor = 0
            self._line_view().set_matches(set(self._match_indices))
            self._refresh_status()
            if self._match_indices:
                self._jump_to_line(self._match_indices[0])

        self.push_screen(CommandModal("/"), on_result)

    def _next_match(self) -> None:
        if not self._match_indices:
            return
        self._match_cursor = (self._match_cursor + 1) % len(self._match_indices)
        self._jump_to_line(self._match_indices[self._match_cursor])
        self._refresh_status()

    def _prev_match(self) -> None:
        if not self._match_indices:
            return
        self._match_cursor = (self._match_cursor - 1) % len(self._match_indices)
        self._jump_to_line(self._match_indices[self._match_cursor])
        self._refresh_status()

    def _select_all_matches(self) -> None:
        if not self._match_indices:
            return
        lv = self._line_view()
        group = self._model.active_group
        for idx in self._match_indices:
            self._model.lines[idx].group = group
            lv._redraw_line(idx)
        self._refresh_status()

    def action_goto_line(self) -> None:
        self._open_goto_line()

    def action_search(self) -> None:
        self._open_search()

    def action_next_match(self) -> None:
        self._next_match()

    def action_prev_match(self) -> None:
        self._prev_match()

    def on_key(self, event: events.Key) -> None:
        ch = event.character
        if ch == "g":
            self._jump_to_line(0)
            event.stop()
        elif ch == "G":
            self._jump_to_line(len(self._model.lines) - 1)
            event.stop()
        elif ch == "*":
            self._select_all_matches()
            event.stop()

    def _set_group(self, group: int) -> None:
        self._model.active_group = group
        self._refresh_status()


for _grp in range(1, 10):
    setattr(ClipperApp, f"action_set_group_{_grp}", functools.partialmethod(ClipperApp._set_group, _grp))


def run(
    source: str,
    filename: str | None,
    prompt: str | None = None,
    header: str | None = None,
    group_names: dict[int, str] | None = None,
    output_lines: bool = False,
    output_summary: bool = False,
) -> None:
    app = ClipperApp(source, filename, prompt=prompt, header=header, group_names=group_names, output_lines=output_lines, output_summary=output_summary)
    result = app.run()
    if result:
        print(result)
