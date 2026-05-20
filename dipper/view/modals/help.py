"""Modal showing the full keybinding reference."""

from pathlib import Path
from typing import ClassVar, override

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Static

from dipper.view.bindings import BINDING_DEFS


def help_table() -> str:
    rows = []
    for bd in BINDING_DEFS:
        if not bd.show_help:
            continue
        if not bd.key:
            rows.append("")
        else:
            rows.append(f"[bold]{bd.key:<12}[/bold] {bd.description}")
    return "\n".join(rows)


class HelpModal(ModalScreen[None]):
    """Full keybinding reference."""

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("escape", "dismiss", "Close"),
        Binding("question_mark", "dismiss", "Close", show=False),
    ]
    CSS_PATH = str(Path(__file__).parent / "help.tcss")
    CONTAINER_ID = "help-container"

    @override
    def compose(self) -> ComposeResult:
        yield Static(help_table(), id=self.CONTAINER_ID)

    def on_mount(self) -> None:
        self.query_one(f"#{self.CONTAINER_ID}").border_title = "help"
