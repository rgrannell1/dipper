"""Lavender theme — purple and crimson on a soft light background."""

from typing import ClassVar

from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Token
from textual.theme import Theme

_BG = "#f5f0ff"
_SURFACE = "#ebe4f8"
_PANEL = "#ddd6f0"
_FG = "#2d1f5e"
_PRIMARY = "#7c4dce"
_SECONDARY = "#c2185b"
_COMMENT = "#9b8ab8"
_STRING = "#2e7d32"
_NUMBER = "#e65100"
_PUNCT = "#4a3080"
_ERROR = "#c2185b"


class LavenderStyle(Style):
    background_color = _BG
    styles: ClassVar[dict] = {
        Token:          _FG,
        Comment:        _COMMENT,
        Keyword:        _PRIMARY,
        Keyword.Type:   _SECONDARY,
        Operator.Word:  _PRIMARY,
        Name.Function:  _SECONDARY,
        Name.Class:     _SECONDARY,
        Name.Builtin:   _PRIMARY,
        String:         _STRING,
        Number:         _NUMBER,
        Punctuation:    _PUNCT,
    }


LAVENDER = Theme(
    name="lavender",
    primary=_PRIMARY,
    secondary=_SECONDARY,
    warning=_NUMBER,
    error=_ERROR,
    success=_STRING,
    accent=_PRIMARY,
    foreground=_FG,
    background=_BG,
    surface=_SURFACE,
    panel=_PANEL,
    dark=False,
)
