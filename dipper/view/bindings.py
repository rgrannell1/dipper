"""Key bindings for the dipper ClipperApp."""

from typing import ClassVar

from textual.binding import Binding

APP_BINDINGS: ClassVar[list[Binding]] = [
    Binding("n", "annotate", "Note"),
    Binding("r", "rename_group", "Rename"),
    Binding("f", "fill_range", "Fill range", show=False),
    Binding("q", "write_output", "Write & quit"),
    Binding("colon", "goto_line", "Go to line", show=False),
    Binding("slash", "search", "Search", show=False),
    Binding("greater_than_sign", "next_match", "Next match", show=False, priority=True),
    Binding("less_than_sign", "prev_match", "Prev match", show=False, priority=True),
    Binding("x", "reset", "Reset"),
    Binding("u", "undo", "Undo"),
    Binding("o", "groups_overview", "Groups"),
    Binding("question_mark", "help", "Help"),
    Binding("p", "paste_last", "Paste last", show=False),
]
