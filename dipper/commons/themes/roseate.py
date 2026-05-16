"""Roseate theme — warm pink and blue tones on a deep purple background."""

from typing import ClassVar

from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Token
from textual.theme import Theme

_BG = "#2c2833"
_SURFACE = "#221e2b"
_PANEL = "#3a3040"
_FG = "#FFF0F5"
_PRIMARY = "#ff82cb"
_SECONDARY = "#82AAFF"
_COMMENT = "#6b5c70"
_STRING = "#a8d8ea"
_NUMBER = "#ffb347"
_PUNCT = "#d4b4e0"
_ERROR = "#ff5c8a"


class RoseateStyle(Style):
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
        Name.Decorator: _PRIMARY,
        String:         _STRING,
        Number:         _NUMBER,
        Punctuation:    _PUNCT,
    }


ROSEATE = Theme(
    name="roseate",
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
    dark=True,
)
