"""Dark+ theme — VS Code dark, blue and teal on dark grey."""

from typing import ClassVar

from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Token
from textual.theme import Theme

_BG = "#1E1E1E"
_SURFACE = "#252526"
_PANEL = "#333333"
_FG = "#D4D4D4"
_PRIMARY = "#569CD6"
_SECONDARY = "#4EC9B0"
_COMMENT = "#6A9955"
_FUNCTION = "#DCDCAA"
_STRING = "#CE9178"
_NUMBER = "#B5CEA8"
_PUNCT = "#D4D4D4"
_ERROR = "#F44747"


class DarkPlusStyle(Style):
    background_color = _BG
    styles: ClassVar[dict] = {
        Token:          _FG,
        Comment:        _COMMENT,
        Keyword:        _PRIMARY,
        Keyword.Type:   _SECONDARY,
        Operator.Word:  _PRIMARY,
        Name.Function:  _FUNCTION,
        Name.Class:     _SECONDARY,
        Name.Builtin:   _PRIMARY,
        String:         _STRING,
        Number:         _NUMBER,
        Punctuation:    _PUNCT,
    }


DARK_PLUS = Theme(
    name="dark-plus",
    primary=_PRIMARY,
    secondary=_SECONDARY,
    warning=_STRING,
    error=_ERROR,
    success=_NUMBER,
    accent=_FUNCTION,
    foreground=_FG,
    background=_BG,
    surface=_SURFACE,
    panel=_PANEL,
    dark=True,
)
