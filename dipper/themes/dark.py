"""Dark theme — cool blue and green on near-black."""

from typing import ClassVar

from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Token
from textual.theme import Theme

_BG = "#0d0d0d"
_SURFACE = "#1a1a1a"
_PANEL = "#222222"
_FG = "#c8c8c8"
_PRIMARY = "#5fafff"
_SECONDARY = "#87af87"
_COMMENT = "#666666"
_STRING = "#afd787"
_NUMBER = "#d7af87"
_PUNCT = "#c8c8c8"
_ERROR = "#ff5f5f"


class DarkStyle(Style):
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


DARK = Theme(
    name="maxima-dark",
    primary=_PRIMARY,
    secondary=_SECONDARY,
    warning=_NUMBER,
    error=_ERROR,
    success=_SECONDARY,
    accent=_PRIMARY,
    foreground=_FG,
    background=_BG,
    surface=_SURFACE,
    panel=_PANEL,
    dark=True,
)
