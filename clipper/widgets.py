# Textual widgets: annotation popup modal

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Input, Label

from clipper.constants import GROUP_COLOURS


class RenameModal(ModalScreen[str]):
    """Popup for renaming a group."""

    BINDINGS = [Binding("escape", "dismiss('')", "Cancel")]

    def __init__(self, group: int, existing: str = "") -> None:
        super().__init__()
        self._group = group
        self._existing = existing

    def compose(self) -> ComposeResult:
        colour = GROUP_COLOURS[self._group]
        yield Label(f"[{colour}]●  group {self._group}[/]", id="modal-label")
        yield Input(value=self._existing, placeholder=f"name…", id="modal-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    DEFAULT_CSS = """
    RenameModal {
        align: center middle;
    }
    RenameModal > Label {
        margin: 1 2;
    }
    RenameModal > Input {
        width: 60;
        margin: 0 2 1 2;
    }
    """


class AnnotationModal(ModalScreen[str]):
    """Popup for entering annotation text for a group."""

    BINDINGS = [
        Binding("escape", "dismiss('')", "Cancel"),
    ]

    def __init__(self, group: int, existing: str = "") -> None:
        super().__init__()
        self._group = group
        self._existing = existing

    def compose(self) -> ComposeResult:
        colour = GROUP_COLOURS[self._group]
        yield Label(f"[{colour}]Annotation for COMMENT_GROUP_{self._group}[/]", id="modal-label")
        yield Input(value=self._existing, placeholder="Enter annotation…", id="modal-input")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    DEFAULT_CSS = """
    AnnotationModal {
        align: center middle;
    }
    AnnotationModal > Label {
        margin: 1 2;
    }
    AnnotationModal > Input {
        width: 60;
        margin: 0 2 1 2;
    }
    """
