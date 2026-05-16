# Popup modal for renaming a group.

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Input, Label

from dipper.view import group_modal_title

CSS_PATH = Path(__file__).parent / "rename.tcss"


class RenameModal(ModalScreen[str]):
    """Popup for renaming a group."""

    BINDINGS = [Binding("escape", "dismiss('')", "Cancel")]
    CSS_PATH = str(Path(__file__).parent / "rename.tcss")

    def __init__(self, group: int, existing: str = "") -> None:
        super().__init__()
        self._group = group
        self._existing = existing

    def compose(self) -> ComposeResult:
        yield Label(group_modal_title(self._group), id="modal-label")
        yield Input(value=self._existing, placeholder="name…", id="modal-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)
