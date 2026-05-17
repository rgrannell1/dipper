"""Modal showing the full keybinding reference."""

from pathlib import Path
from typing import ClassVar, override

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Static

KEYBINDINGS = [
    ("tab", "select / deselect line"),
    ("1-9", "set active group"),
    ("g / G", "jump to top / bottom"),
    ("", ""),
    ("/", "search"),
    ("> / <", "next / previous match"),
    ("*", "select all matches"),
    ("", ""),
    ("f", "fill range"),
    ("n", "annotate block"),
    ("r", "rename group"),
    ("o", "groups overview"),
    ("", ""),
    ("u", "undo"),
    ("x", "reset all"),
    ("q", "write & quit"),
    ("?", "this help"),
    ("ctrl+p", "command palette"),
]


def help_table() -> str:
    rows = []
    for key, description in KEYBINDINGS:
        if not key:
            rows.append("")
        else:
            rows.append(f"[bold]{key:<12}[/bold] {description}")
    return "\n".join(rows)


class HelpModal(ModalScreen[None]):
    """Full keybinding reference."""

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "dismiss", "Close"),
        Binding("question_mark", "dismiss", "Close", show=False),
    ]
    CSS_PATH = str(Path(__file__).parent / "help.tcss")

    @override
    def compose(self) -> ComposeResult:
        yield Static(help_table(), id="help-container")
