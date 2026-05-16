"""Popup modal for entering annotation text for a group block."""

from pathlib import Path
from typing import ClassVar

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Input, Label

from dipper.view.render import annotation_modal_title


class AnnotationModal(ModalScreen[str]):
    """Popup for entering annotation text for a specific block."""

    BINDINGS: ClassVar[list[Binding]] = [Binding("escape", "dismiss('')", "Cancel")]
    CSS_PATH = str(Path(__file__).parent / "annotation.tcss")

    def __init__(
        self,
        group: int,
        label: str,
        existing: str = "",
        block_range: tuple[int, int] | None = None,
    ) -> None:
        super().__init__()
        self._group = group
        self._label = label
        self._existing = existing
        self._block_range = block_range

    def compose(self) -> ComposeResult:
        start_line, end_line = self._block_range if self._block_range else (0, 0)
        title = annotation_modal_title(self._group, self._label, start_line, end_line)
        yield Label(title, id="modal-label")
        yield Input(value=self._existing, placeholder="Enter annotation…", id="modal-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)
