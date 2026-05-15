The system reads a file path as a CLI argument, or reads from stdin when no path is given. It displays the file contents in a scrollable terminal UI with syntax highlighting derived from the file extension or a guessed language.

The user can press Tab on any line to toggle it into the current selection. Selected lines are visually distinguished. The user can press keys 1–9 to set the active colour group; all subsequently selected lines belong to that group, and lines already selected move into the new group. Colour groups are rendered with distinct foreground colours in the TUI.

When the user presses Enter with one or more lines selected, a modal popup appears for entering a text annotation. Submitting the popup attaches that annotation text to the current group.

Pressing a configurable key (e.g. w or ctrl+s) writes the annotated output to stdout and exits. The output format is the original file with underline markers (`^^^^^^`) and group labels appended immediately after each selected line, and a summary section at the end separated by a tilde rule, listing each group label and its annotation text.

Lines not in any group are reproduced in the output without modification.

The system does not modify the source file.

The project has a pytest-based unit test suite covering the document model and output renderer. Tests for the model cover: toggling a line into the active group, toggling it back out, moving a line to a different group, group membership reporting, nearest annotated group selection, and the default group label. Tests for the output renderer cover: no selected lines produces original text with no separator; a selected line with no annotation produces a mark line with a `%%clipper:mark:N%%` prefix and a `^` underline of at least the minimum length; the underline length matches the source line length when that is longer than the minimum; the separator block appears between body and summary; annotation text appears after the group header; a pre-named group includes the name on the group header line; multiple groups each produce their own header and annotation; lines outside any group appear verbatim without a mark line. The test suite is runnable via `uv run pytest`.
