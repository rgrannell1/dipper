"""Styled CLI help display shown when dipper is invoked with no arguments."""

from rich.console import Console
from rich.text import Text

RULE = "─" * 45

EXAMPLES = [
    ("dipper <file>", "open a file interactively"),
    ("dipper <file> --preset cr", "code-review groups"),
    ("dipper <file> --groups bug,note", "custom groups"),
    ("dipper <file> --output out.txt", "save annotations to file"),
    ("dipper --lines < file", "output marked lines only"),
    ("dipper --summary < file", "output summary block only"),
]

FOOTER_FLAGS = ["dipper <file>", "--preset", "--groups", "--lines", "--summary", "--output"]


def help_text() -> Text:
    text = Text()
    text.append("dipper\n", style="bold")
    text.append(RULE + "\n", style="dim")
    text.append("\n")
    for command, description in EXAMPLES:
        text.append(f"  {command:<38}", style="cyan")
        text.append(f"{description}\n", style="dim")
    text.append("\n")
    text.append(RULE + "\n", style="dim")
    footer = "  •  ".join(FOOTER_FLAGS)
    text.append(footer + "\n", style="dim")
    return text


def print_help() -> None:
    Console().print(help_text())
