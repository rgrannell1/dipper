"""Custom Textual widgets: LineListView"""

from typing import ClassVar

from rich.text import Text
from textual import events
from textual.binding import Binding
from textual.message import Message
from textual.widgets import ListItem, ListView, Static

from dipper.commons.constants import GROUP_COLOURS
from dipper.model.state import AppState
from dipper.view.render import gutter_text, indicator_text


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

    def line_gutter(self, idx: int) -> Text:
        """Line number gutter, highlighted yellow when the line is a search match."""
        line_num = str(idx + 1).rjust(self._gutter_width)
        match_set = set(self._model.search.indices)
        highlighted = idx in match_set
        return gutter_text(line_num, highlighted)

    def indicator(self, idx: int, group: int) -> Text:
        """Coloured dot showing group membership, or anchor diamond when range-fill is pending."""
        is_anchor = idx == self._model.range_fill.anchor
        return indicator_text(group, self._model.range_fill.anchor_group, is_anchor)

    def line_text(self, idx: int) -> Text:
        """Full rendered line: gutter + indicator + syntax-highlighted source text."""
        line = self._model.lines[idx]
        hi_text = Text.from_ansi(self._hi_lines[idx])
        is_annotated = line.group != 0
        if is_annotated:
            hi_text.stylize(f"bold {GROUP_COLOURS[line.group]}")
        gutter = self.line_gutter(idx)
        indicator = self.indicator(idx, line.group)
        return Text.assemble(gutter, indicator, hi_text)

    def redraw_line(self, idx: int) -> None:
        """Re-render a single list item from current model state."""
        if not (0 <= idx < len(self._model.lines)):
            return
        self.query_one(f"#l{idx} Static", Static).update(self.line_text(idx))

    def redraw_lines(self, indices) -> None:
        """Re-render multiple list items."""
        for idx in indices:
            self.redraw_line(idx)

    def action_toggle_line(self) -> None:
        idx = self.index
        if idx is None:
            return
        self._model.take_snapshot()
        self._model.toggle_line(idx)
        self.redraw_line(idx)
        self.post_message(self.LineToggled())

    def on_key(self, event: events.Key) -> None:
        ch = event.character
        is_group_digit = ch is not None and ch.isdigit() and ch != "0"
        if is_group_digit:
            self.app.set_group(int(ch))  # type: ignore[attr-defined]
            event.stop()

    @property
    def cursor_index(self) -> int:
        return self.index if self.index is not None else 0
