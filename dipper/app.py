# Main Textual application for dipper

import functools
import re as _re
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.command import Provider, Hit, Hits
from textual.message import Message
from textual.widgets import Footer, Header, Label, ListView, ListItem, Static
from textual import events

from rich.text import Text
from rich.style import Style

from dipper.constants import GROUP_COLOURS
from dipper.highlight import highlighted_lines
from dipper.model import AppState, LineState
from dipper.output import render_output
from dipper.modals import AnnotationModal, CommandModal, RenameModal


# --- view helpers (pure functions, no app/widget state) ---


def group_dot(colour: str) -> Text:
    return Text("● ", style=Style(color=colour, bold=True))


def group_display(group: int, label: str, note: str) -> Text:
    colour = GROUP_COLOURS[group]
    display = Text()
    display.append_text(group_dot(colour))
    display.append(f"group {group}: ", style="dim")
    display.append(label, style=Style(color=colour, bold=True))
    if note:
        display.append(f"  —  {note}", style="dim")
    return display


def group_score(matcher, query: str, group: int, label: str, note: str) -> float:
    searchable = f"group {group}: {label}  {note}"
    return matcher.match(searchable) if query else 1.0


def gutter_text(line_num: str, highlighted: bool) -> Text:
    style = "bold yellow" if highlighted else "dim"
    return Text(f"{line_num} ", style=style)


def indicator_text(group: int, anchor_group: int, is_anchor: bool) -> Text:
    if group != 0:
        return Text("● ", style=f"bold {GROUP_COLOURS[group]}")
    if is_anchor:
        return Text("◆ ", style=f"bold {GROUP_COLOURS[anchor_group]}")
    return Text("  ")


def search_hit_text(pattern: str, pos: int, total: int) -> Text:
    result = Text()
    result.append(f"  |  /{pattern} [{pos}/{total}]", style="bold yellow")
    return result


def search_miss_text(pattern: str) -> Text:
    result = Text()
    result.append(f"  |  /{pattern} [no matches]", style="dim yellow")
    return result


def group_used_dot(group: int) -> Text:
    return Text("● ", style=Style(color=GROUP_COLOURS[group], bold=True))


# --- command palette provider ---


class GroupProvider(Provider):
    """Command palette provider showing all active groups with names and notes."""

    async def search(self, query: str) -> Hits:
        app: ClipperApp = self.app  # type: ignore
        model = app._model
        matcher = self.matcher(query)

        for group in sorted(model.selected_groups()):
            label = model.group_label(group)
            annotation = model.annotations.get(group)
            note = annotation.text if annotation else ""

            score = group_score(matcher, query, group, label, note)
            if score == 0:
                continue

            first_line = next(
                (idx for idx, line in enumerate(model.lines) if line.group == group), None
            )
            jump = functools.partial(app.jump_to_line, first_line)
            command = jump if first_line is not None else app.noop

            yield Hit(
                score=score,
                match_display=group_display(group, label, note),
                command=command,
            )


class LineListView(ListView):
    """Line list that renders purely from AppState — owns no model state of its own."""

    class LineToggled(Message):
        pass

    BINDINGS = [
        Binding("tab", "toggle_line", "Select line", priority=True),
    ]

    def __init__(self, model: AppState, hi_lines: list[str]) -> None:
        self._model = model
        self._hi_lines = hi_lines
        self._gutter_width = len(str(len(hi_lines))) + 1
        items = [
            ListItem(Static(self.line_text(idx), markup=False), id=f"l{idx}")
            for idx in range(len(hi_lines))
        ]
        super().__init__(*items)

    def gutter(self, idx: int) -> Text:
        line_num = str(idx + 1).rjust(self._gutter_width)
        highlighted = idx in set(self._model.match_indices)
        return gutter_text(line_num, highlighted)

    def indicator(self, idx: int, group: int) -> Text:
        is_anchor = idx == self._model.range_anchor
        return indicator_text(group, self._model.range_anchor_group, is_anchor)

    def line_text(self, idx: int) -> Text:
        line = self._model.lines[idx]
        hi_text = Text.from_ansi(self._hi_lines[idx])
        if line.group != 0:
            hi_text.stylize(f"bold {GROUP_COLOURS[line.group]}")
        return Text.assemble(self.gutter(idx), self.indicator(idx, line.group), hi_text)

    def redraw_line(self, idx: int) -> None:
        self.query_one(f"#l{idx} Static", Static).update(self.line_text(idx))

    def redraw_lines(self, indices) -> None:
        for idx in indices:
            self.redraw_line(idx)

    def action_toggle_line(self) -> None:
        idx = self.index
        if idx is None:
            return
        self._model.toggle_line(idx)
        self.redraw_line(idx)
        self.post_message(self.LineToggled())

    def on_key(self, event: events.Key) -> None:
        ch = event.character
        if ch is not None and ch.isdigit() and ch != "0":
            self.app.set_group(int(ch))  # type: ignore[attr-defined]
            event.stop()

    @property
    def cursor_index(self) -> int:
        return self.index if self.index is not None else 0


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
        yield Label(self.status_text(), id="status")
        yield Footer()

    def cursor_group(self) -> int:
        try:
            idx = self.line_view().cursor_index
        except Exception:
            return 0
        return self._model.lines[idx].group if idx < len(self._model.lines) else 0

    def append_search_section(self, result: Text) -> None:
        pattern = self._model.search_pattern
        if not pattern:
            return
        if self._model.match_indices:
            pos = self._model.match_cursor + 1
            total = len(self._model.match_indices)
            result.append_text(search_hit_text(pattern, pos, total))
        else:
            result.append_text(search_miss_text(pattern))

    def status_text(self) -> Text:
        active = self._model.active_group
        result = Text(no_wrap=True, overflow="ellipsis")
        colour = GROUP_COLOURS[active]
        result.append_text(group_dot(colour))
        result.append(self._model.group_label(active), style=Style(color=colour, bold=True))
        used = sorted(self._model.selected_groups())
        if used:
            result.append("  |  ", style="dim")
            for grp in used:
                result.append_text(group_used_dot(grp))
        self.append_search_section(result)
        result.append(f"  |  {self._filename}", style="dim")
        return result

    def refresh_status(self) -> None:
        self.query_one("#status", Label).update(self.status_text())

    def line_view(self) -> LineListView:
        return self.query_one(LineListView)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        self.refresh_status()

    def on_line_list_view_line_toggled(self, event: LineListView.LineToggled) -> None:
        self.refresh_status()

    def rename_done(self, group: int, result: str) -> None:
        self._model.set_group_name(group, result)
        self.refresh_status()

    def action_rename_group(self) -> None:
        grp = self.cursor_group() or self._model.active_group
        existing = self._model.group_names.get(grp, "")
        callback = functools.partial(self.rename_done, grp)
        self.push_screen(RenameModal(grp, existing), callback)

    def annotate_done(self, group: int, result: str) -> None:
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
        lv = self.line_view()
        lv.index = idx
        lv.scroll_to_widget(lv.query_one(f"#l{idx}"))

    def noop(self) -> None:
        pass

    def open_goto_line(self) -> None:
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
        old_matches = set(self._model.match_indices)
        self._model.clear_search()
        lv.redraw_lines(old_matches)
        self.refresh_status()

    def apply_search(self, lv: LineListView, value: str) -> None:
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
        if value is None:
            return
        lv = self.line_view()
        if not value:
            self.apply_clear_search(lv)
        else:
            self.apply_search(lv, value)

    def next_match(self) -> None:
        idx = self._model.next_match()
        if idx is not None:
            self.jump_to_line(idx)
            self.refresh_status()

    def prev_match(self) -> None:
        idx = self._model.prev_match()
        if idx is not None:
            self.jump_to_line(idx)
            self.refresh_status()

    def select_all_matches(self) -> None:
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

    def set_group(self, group: int) -> None:
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
