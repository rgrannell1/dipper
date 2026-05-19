"""Key bindings for the dipper ClipperApp."""

from typing import ClassVar

from textual.binding import Binding

APP_BINDINGS: ClassVar[list[Binding]] = [
    Binding("q", "write_output", "Write & quit"),
    Binding("n", "annotate", "Note"),
    Binding("r", "rename_group", "Rename"),
    Binding("o", "groups_overview", "Groups"),
    Binding("u", "undo", "Undo"),
    Binding("x", "reset", "Reset"),
    Binding("question_mark", "help", "Help"),
    Binding("f", "fill_range", "Fill range", show=False),
    Binding("colon", "goto_line", "Go to line", show=False),
    Binding("slash", "search", "Search", show=False),
    Binding("greater_than_sign", "next_block", "Next block", show=False, priority=True),
    Binding("less_than_sign", "prev_block", "Prev block", show=False, priority=True),
    Binding("p", "paste_last", "Paste last", show=False),
]
