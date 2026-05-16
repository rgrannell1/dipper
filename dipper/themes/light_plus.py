"""Light+ theme — VS Code light, blue and teal on white."""

from typing import ClassVar

from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Token
from textual.theme import Theme

_BG = "#FFFFFF"
_SURFACE = "#F3F3F3"
_PANEL = "#E8E8E8"
_FG = "#000000"
_PRIMARY = "#0451A5"
_SECONDARY = "#267F99"
_ACCENT = "#0000FF"
_COMMENT = "#008000"
_FUNCTION = "#795E26"
_STRING = "#A31515"
_NUMBER = "#098658"
_PUNCT = "#000000"


class LightPlusStyle(Style):
    background_color = _BG
    styles: ClassVar[dict] = {
        Token:          _FG,
        Comment:        _COMMENT,
        Keyword:        _ACCENT,
        Keyword.Type:   _SECONDARY,
        Operator.Word:  _ACCENT,
        Name.Function:  _FUNCTION,
        Name.Class:     _SECONDARY,
        Name.Builtin:   _PRIMARY,
        String:         _STRING,
        Number:         _NUMBER,
        Punctuation:    _PUNCT,
    }


LIGHT_PLUS = Theme(
    name="light-plus",
    primary=_PRIMARY,
    secondary=_SECONDARY,
    warning=_FUNCTION,
    error=_STRING,
    success=_COMMENT,
    accent=_ACCENT,
    foreground=_FG,
    background=_BG,
    surface=_SURFACE,
    panel=_PANEL,
    dark=False,
)
