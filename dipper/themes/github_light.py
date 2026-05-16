"""GitHub Light theme — red and purple on white."""

from typing import ClassVar

from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Token
from textual.theme import Theme

_BG = "#FFFFFF"
_SURFACE = "#F6F8FA"
_PANEL = "#EAECEF"
_FG = "#24292E"
_PRIMARY = "#D73A49"
_SECONDARY = "#6F42C1"
_COMMENT = "#6A737D"
_STRING = "#032F62"
_NUMBER = "#005CC5"
_PUNCT = "#24292E"
_WARNING = "#E36209"
_SUCCESS = "#22863A"


class GitHubLightStyle(Style):
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


GITHUB_LIGHT = Theme(
    name="github-light",
    primary=_PRIMARY,
    secondary=_SECONDARY,
    warning=_WARNING,
    error=_PRIMARY,
    success=_SUCCESS,
    accent=_SECONDARY,
    foreground=_FG,
    background=_BG,
    surface=_SURFACE,
    panel=_PANEL,
    dark=False,
)
