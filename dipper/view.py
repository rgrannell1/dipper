# View layer: pure render helpers, GroupProvider, and LineListView

from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.command import Provider, Hit, Hits
from textual.message import Message
from textual.widgets import ListView, ListItem, Static
from textual import events

from rich.text import Text
from rich.style import Style

from dipper.constants import GROUP_COLOURS
from dipper.model import AppState

if TYPE_CHECKING:
    from dipper.app import ClipperApp


# --- pure render helpers ---


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


def group_name_text(group: int, name: str) -> Text:
    colour = GROUP_COLOURS[group]
    if name:
        return Text(name, style=Style(color=colour, bold=True))
    return Text(f"group {group}", style="dim")


def group_line_count_text(count: int) -> Text:
    label = f"{count} line{'s' if count != 1 else ''}"
    return Text(f"  —  {label}", style="dim")


def group_row_text(model: AppState, group: int) -> Text:
    colour = GROUP_COLOURS[group]
    count = sum(1 for line in model.lines if line.group == group)
    name = model.group_names.get(group, "")
    result = Text()
    result.append_text(group_dot(colour))
    result.append_text(group_name_text(group, name))
    result.append_text(group_line_count_text(count))
    return result


def group_modal_title(group: int) -> str:
    colour = GROUP_COLOURS[group]
    return f"[{colour}]●  group {group}[/]"


def annotation_modal_title(group: int, label: str) -> str:
    colour = GROUP_COLOURS[group]
    return f"[{colour}]Annotation for {label}[/]"


def group_row_item(model: AppState, grp: int) -> ListItem:
    return ListItem(Static(group_row_text(model, grp), markup=False, id=f"gs-{grp}"), id=f"gr-{grp}")


def search_section_text(model: AppState) -> Text:
    pattern = model.search_pattern
    result = Text()
    if not pattern:
        return result
    if model.match_indices:
        pos = model.match_cursor + 1
        total = len(model.match_indices)
        result.append_text(search_hit_text(pattern, pos, total))
    else:
        result.append_text(search_miss_text(pattern))
    return result


def status_bar_text(model: AppState, filename: str) -> Text:
    active = model.active_group
    colour = GROUP_COLOURS[active]
    result = Text(no_wrap=True, overflow="ellipsis")
    result.append_text(group_dot(colour))
    result.append(model.group_label(active), style=Style(color=colour, bold=True))
    used = sorted(model.selected_groups())
    if used:
        result.append("  |  ", style="dim")
        for grp in used:
            result.append_text(group_used_dot(grp))
    result.append_text(search_section_text(model))
    result.append(f"  |  {filename}", style="dim")
    return result


# --- command palette provider ---


class GroupProvider(Provider):
    """Command palette provider listing all annotated groups with jump-to support."""

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


def theme_display(name: str, primary: str) -> Text:
    result = Text()
    result.append("◉ ", style=f"bold {primary}")
    result.append(name, style=Style(color=primary, bold=True))
    return result


class ThemeProvider(Provider):
    """Command palette provider listing all available colour themes."""

    async def search(self, query: str) -> Hits:
        from dipper.themes import THEMES
        app: ClipperApp = self.app  # type: ignore
        matcher = self.matcher(query)

        for name, entry in THEMES.items():
            searchable = f"Theme - {name}"
            score = matcher.match(searchable) if query else 1.0
            if score == 0:
                continue
            primary = entry["textual"].primary
            yield Hit(
                score=score,
                match_display=theme_display(searchable, primary),
                command=functools.partial(app.change_theme, name),
            )


# --- main list widget ---


class LineListView(ListView):
    """Scrollable list of source lines; renders purely from AppState, owns no model state."""

    class LineToggled(Message):
        pass

    BINDINGS = [
        Binding("tab", "toggle_line", "Select line", priority=True),
    ]

    def __init__(self, model: AppState, hi_lines: list[str]) -> None:
        self._model = model
        self._hi_lines = hi_lines
        self._gutter_width = len(str(len(hi_lines))) + 1
        items = []
        for idx in range(len(hi_lines)):
            static = Static(self.line_text(idx), markup=False)
            items.append(ListItem(static, id=f"l{idx}"))
        super().__init__(*items)

    def gutter(self, idx: int) -> Text:
        """Line number gutter, highlighted yellow when the line is a search match."""
        line_num = str(idx + 1).rjust(self._gutter_width)
        highlighted = idx in set(self._model.match_indices)
        return gutter_text(line_num, highlighted)

    def indicator(self, idx: int, group: int) -> Text:
        """Coloured dot showing group membership, or anchor diamond when range-fill is pending."""
        is_anchor = idx == self._model.range_anchor
        return indicator_text(group, self._model.range_anchor_group, is_anchor)

    def line_text(self, idx: int) -> Text:
        """Full rendered line: gutter + indicator + syntax-highlighted source text."""
        line = self._model.lines[idx]
        hi_text = Text.from_ansi(self._hi_lines[idx])
        if line.group != 0:
            hi_text.stylize(f"bold {GROUP_COLOURS[line.group]}")
        gutter = self.gutter(idx)
        indicator = self.indicator(idx, line.group)
        return Text.assemble(gutter, indicator, hi_text)

    def redraw_line(self, idx: int) -> None:
        """Re-render a single list item from current model state."""
        self.query_one(f"#l{idx} Static", Static).update(self.line_text(idx))

    def redraw_lines(self, indices) -> None:
        """Re-render multiple list items."""
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
