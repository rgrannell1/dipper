# Syntax highlighting: converts source text to Rich-marked-up lines

from pygments import highlight
from pygments.formatters import TerminalTrueColorFormatter
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename, guess_lexer
from pygments.style import Style
from pygments.util import ClassNotFound

from dipper.themes import DEFAULT_THEME, THEMES


def choose_lexer(source: str, filename: str | None):
    if filename:
        try:
            return get_lexer_for_filename(filename)
        except ClassNotFound:
            pass
    try:
        return guess_lexer(source)
    except ClassNotFound:
        return get_lexer_by_name("text")


def highlighted_lines(source: str, filename: str | None = None, style: type[Style] | None = None) -> list[str]:
    """Return source split into lines with ANSI colour codes applied."""
    resolved_style = style or THEMES[DEFAULT_THEME]["pygments"]
    lexer = choose_lexer(source, filename)
    formatter = TerminalTrueColorFormatter(style=resolved_style)
    rendered = highlight(source, lexer, formatter)
    # Strip trailing newline that pygments always appends
    lines = rendered.splitlines()
    # Pad so length matches source line count (pygments may trim trailing blanks)
    source_count = len(source.splitlines())
    while len(lines) < source_count:
        lines.append("")
    return lines
