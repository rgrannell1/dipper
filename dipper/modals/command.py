# Popup modal for : (goto line) and / (search) command bar.

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.widgets import Input, Label


class CommandModal(ModalScreen[str | None]):
    """Bottom command-bar for : (goto line) and / (search) commands."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]
    CSS_PATH = str(Path(__file__).parent / "command.tcss")

    def __init__(self, prefix: str) -> None:
        super().__init__()
        self._prefix = prefix

    def compose(self) -> ComposeResult:
        with Horizontal(id="cmd-bar"):
            yield Label(self._prefix, id="cmd-prefix")
            yield Input(id="cmd-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def action_cancel(self) -> None:
        self.dismiss(None)
