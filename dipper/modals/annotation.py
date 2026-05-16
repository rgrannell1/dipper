# Popup modal for entering annotation text for a group.

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Input, Label

from dipper.constants import GROUP_COLOURS


class AnnotationModal(ModalScreen[str]):
    """Popup for entering annotation text for a group."""

    BINDINGS = [Binding("escape", "dismiss('')", "Cancel")]
    CSS_PATH = str(Path(__file__).parent / "annotation.tcss")

    def __init__(self, group: int, label: str, existing: str = "") -> None:
        super().__init__()
        self._group = group
        self._label = label
        self._existing = existing

    def compose(self) -> ComposeResult:
        colour = GROUP_COLOURS[self._group]
        yield Label(f"[{colour}]Annotation for {self._label}[/]", id="modal-label")
        yield Input(value=self._existing, placeholder="Enter annotation…", id="modal-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)
