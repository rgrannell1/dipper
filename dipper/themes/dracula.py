"""Dracula theme — pink and cyan on deep charcoal."""

from typing import ClassVar

from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Token
from textual.theme import Theme

_BG = "#282A36"
_SURFACE = "#21222C"
_PANEL = "#44475A"
_FG = "#F8F8F2"
_PRIMARY = "#FF79C6"
_SECONDARY = "#8BE9FD"
_COMMENT = "#6272A4"
_FUNCTION = "#50FA7B"
_STRING = "#F1FA8C"
_NUMBER = "#BD93F9"
_PUNCT = "#F8F8F2"
_WARNING = "#FFB86C"
_ERROR = "#FF5555"


class DraculaStyle(Style):
    background_color = _BG
    styles: ClassVar[dict] = {
        Token:          _FG,
        Comment:        _COMMENT,
        Keyword:        _PRIMARY,
        Keyword.Type:   _SECONDARY,
        Operator.Word:  _PRIMARY,
        Name.Function:  _FUNCTION,
        Name.Class:     _FUNCTION,
        Name.Builtin:   _PRIMARY,
        Name.Decorator: _FUNCTION,
        String:         _STRING,
        Number:         _NUMBER,
        Punctuation:    _PUNCT,
    }


DRACULA = Theme(
    name="maxima-dracula",
    primary=_PRIMARY,
    secondary=_SECONDARY,
    warning=_WARNING,
    error=_ERROR,
    success=_FUNCTION,
    accent=_NUMBER,
    foreground=_FG,
    background=_BG,
    surface=_SURFACE,
    panel=_PANEL,
    dark=True,
)
