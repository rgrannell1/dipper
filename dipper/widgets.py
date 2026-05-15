# Textual widgets: annotation popup modal

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.screen import ModalScreen
from textual.widgets import Input, Label

from dipper.constants import GROUP_COLOURS


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


class CommandModal(ModalScreen[str | None]):
    """Bottom command-bar for : (goto line) and / (search) commands."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

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

    DEFAULT_CSS = """
    CommandModal {
        background: transparent;
        align: left bottom;
    }
    #cmd-bar {
        height: 1;
        width: 100%;
        background: $panel;
        padding: 0 1;
    }
    #cmd-prefix {
        width: auto;
        color: $text;
    }
    #cmd-input {
        border: none;
        height: 1;
        background: $panel;
        width: 1fr;
        padding: 0;
    }
    """
