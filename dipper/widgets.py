"""Custom Textual widgets: LineListView"""

from typing import ClassVar

from rich.text import Text
from textual import events
from textual.binding import Binding
from textual.message import Message
from textual.widgets import ListItem, ListView, Static

from dipper.constants import GROUP_COLOURS
from dipper.model import AppState


def gutter_text(line_num: str, highlighted: bool) -> Text:
    style = "bold yellow" if highlighted else "dim"
    return Text(f"{line_num} ", style=style)


def indicator_text(group: int, anchor_group: int, is_anchor: bool) -> Text:
    if group != 0:
        return Text("● ", style=f"bold {GROUP_COLOURS[group]}")
    if is_anchor:
        return Text("◆ ", style=f"bold {GROUP_COLOURS[anchor_group]}")
    return Text("  ")


class LineListView(ListView):
    """Scrollable list of source lines; renders purely from AppState, owns no model state."""

    class LineToggled(Message):
        pass

    BINDINGS: ClassVar[list[Binding]] = [
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
        highlighted = idx in set(self._model.search.indices)
        return gutter_text(line_num, highlighted)

    def indicator(self, idx: int, group: int) -> Text:
        """Coloured dot showing group membership, or anchor diamond when range-fill is pending."""
        is_anchor = idx == self._model.range_fill.anchor
        return indicator_text(group, self._model.range_fill.anchor_group, is_anchor)

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
