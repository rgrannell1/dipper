# Popup modal for entering annotation text for a group.

from pathlib import Path
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Input, Label

from dipper.view import annotation_modal_title


class AnnotationModal(ModalScreen[str]):
    """Popup for entering annotation text for a group."""

    BINDINGS: ClassVar[list[Binding]] = [Binding("escape", "dismiss('')", "Cancel")]
    CSS_PATH = str(Path(__file__).parent / "annotation.tcss")

    def __init__(self, group: int, label: str, existing: str = "") -> None:
        super().__init__()
        self._group = group
        self._label = label
        self._existing = existing

    def compose(self) -> ComposeResult:
        yield Label(annotation_modal_title(self._group, self._label), id="modal-label")
        yield Input(value=self._existing, placeholder="Enter annotation…", id="modal-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)
