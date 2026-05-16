# Colour themes ported from maxima — each bundles a Textual app theme and a Pygments syntax style.

from typing import ClassVar

from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Token
from textual.theme import Theme

# ── Pygments styles ───────────────────────────────────────────────────────────

# ── Roseate palette ───────────────────────────────────────────────────────────
_R_BG = "#2c2833"
_R_SURFACE = "#221e2b"
_R_PANEL = "#3a3040"
_R_FG = "#FFF0F5"
_R_PRIMARY = "#ff82cb"   # keyword / accent
_R_SECONDARY = "#82AAFF"   # type / function
_R_COMMENT = "#6b5c70"
_R_STRING = "#a8d8ea"
_R_NUMBER = "#ffb347"
_R_PUNCT = "#d4b4e0"
_R_ERROR = "#ff5c8a"


class RoseateStyle(Style):
    background_color = _R_BG
    styles: ClassVar[dict] = {
        Token:              _R_FG,
        Comment:            _R_COMMENT,
        Keyword:            _R_PRIMARY,
        Keyword.Type:       _R_SECONDARY,
        Operator.Word:      _R_PRIMARY,
        Name.Function:      _R_SECONDARY,
        Name.Class:         _R_SECONDARY,
        Name.Builtin:       _R_PRIMARY,
        Name.Decorator:     _R_PRIMARY,
        String:             _R_STRING,
        Number:             _R_NUMBER,
        Punctuation:        _R_PUNCT,
    }


# ── Dark palette ──────────────────────────────────────────────────────────────
_D_BG = "#0d0d0d"
_D_SURFACE = "#1a1a1a"
_D_PANEL = "#222222"
_D_FG = "#c8c8c8"
_D_PRIMARY = "#5fafff"   # keyword / accent
_D_SECONDARY = "#87af87"   # type / function
_D_COMMENT = "#666666"
_D_STRING = "#afd787"
_D_NUMBER = "#d7af87"
_D_PUNCT = "#c8c8c8"
_D_ERROR = "#ff5f5f"


class DarkStyle(Style):
    background_color = _D_BG
    styles: ClassVar[dict] = {
        Token:              _D_FG,
        Comment:            _D_COMMENT,
        Keyword:            _D_PRIMARY,
        Keyword.Type:       _D_SECONDARY,
        Operator.Word:      _D_PRIMARY,
        Name.Function:      _D_SECONDARY,
        Name.Class:         _D_SECONDARY,
        Name.Builtin:       _D_PRIMARY,
        String:             _D_STRING,
        Number:             _D_NUMBER,
        Punctuation:        _D_PUNCT,
    }


# ── Lavender palette ──────────────────────────────────────────────────────────
_L_BG = "#f5f0ff"
_L_SURFACE = "#ebe4f8"
_L_PANEL = "#ddd6f0"
_L_FG = "#2d1f5e"
_L_PRIMARY = "#7c4dce"   # keyword / accent
_L_SECONDARY = "#c2185b"   # type / function
_L_COMMENT = "#9b8ab8"
_L_STRING = "#2e7d32"
_L_NUMBER = "#e65100"
_L_PUNCT = "#4a3080"
_L_ERROR = "#c2185b"


class LavenderStyle(Style):
    background_color = _L_BG
    styles: ClassVar[dict] = {
        Token:              _L_FG,
        Comment:            _L_COMMENT,
        Keyword:            _L_PRIMARY,
        Keyword.Type:       _L_SECONDARY,
        Operator.Word:      _L_PRIMARY,
        Name.Function:      _L_SECONDARY,
        Name.Class:         _L_SECONDARY,
        Name.Builtin:       _L_PRIMARY,
        String:             _L_STRING,
        Number:             _L_NUMBER,
        Punctuation:        _L_PUNCT,
    }


# ── Dracula palette ───────────────────────────────────────────────────────────
_DR_BG = "#282A36"
_DR_SURFACE = "#21222C"
_DR_PANEL = "#44475A"
_DR_FG = "#F8F8F2"
_DR_PRIMARY = "#FF79C6"   # keyword / accent
_DR_SECONDARY = "#8BE9FD"   # type / function
_DR_COMMENT = "#6272A4"
_DR_FUNCTION = "#50FA7B"
_DR_STRING = "#F1FA8C"
_DR_NUMBER = "#BD93F9"
_DR_PUNCT = "#F8F8F2"
_DR_WARNING = "#FFB86C"
_DR_ERROR = "#FF5555"


class DraculaStyle(Style):
    background_color = _DR_BG
    styles: ClassVar[dict] = {
        Token:              _DR_FG,
        Comment:            _DR_COMMENT,
        Keyword:            _DR_PRIMARY,
        Keyword.Type:       _DR_SECONDARY,
        Operator.Word:      _DR_PRIMARY,
        Name.Function:      _DR_FUNCTION,
        Name.Class:         _DR_FUNCTION,
        Name.Builtin:       _DR_PRIMARY,
        Name.Decorator:     _DR_FUNCTION,
        String:             _DR_STRING,
        Number:             _DR_NUMBER,
        Punctuation:        _DR_PUNCT,
    }


# ── Dark+ palette ─────────────────────────────────────────────────────────────
_DP_BG = "#1E1E1E"
_DP_SURFACE = "#252526"
_DP_PANEL = "#333333"
_DP_FG = "#D4D4D4"
_DP_PRIMARY = "#569CD6"   # keyword / accent
_DP_SECONDARY = "#4EC9B0"   # type
_DP_COMMENT = "#6A9955"
_DP_FUNCTION = "#DCDCAA"
_DP_STRING = "#CE9178"
_DP_NUMBER = "#B5CEA8"
_DP_PUNCT = "#D4D4D4"
_DP_ERROR = "#F44747"


class DarkPlusStyle(Style):
    background_color = _DP_BG
    styles: ClassVar[dict] = {
        Token:              _DP_FG,
        Comment:            _DP_COMMENT,
        Keyword:            _DP_PRIMARY,
        Keyword.Type:       _DP_SECONDARY,
        Operator.Word:      _DP_PRIMARY,
        Name.Function:      _DP_FUNCTION,
        Name.Class:         _DP_SECONDARY,
        Name.Builtin:       _DP_PRIMARY,
        String:             _DP_STRING,
        Number:             _DP_NUMBER,
        Punctuation:        _DP_PUNCT,
    }


# ── Light+ palette ────────────────────────────────────────────────────────────
_LP_BG = "#FFFFFF"
_LP_SURFACE = "#F3F3F3"
_LP_PANEL = "#E8E8E8"
_LP_FG = "#000000"
_LP_PRIMARY = "#0451A5"   # builtin / accent
_LP_SECONDARY = "#267F99"   # type
_LP_ACCENT = "#0000FF"   # keyword
_LP_COMMENT = "#008000"
_LP_FUNCTION = "#795E26"
_LP_STRING = "#A31515"
_LP_NUMBER = "#098658"
_LP_PUNCT = "#000000"


class LightPlusStyle(Style):
    background_color = _LP_BG
    styles: ClassVar[dict] = {
        Token:              _LP_FG,
        Comment:            _LP_COMMENT,
        Keyword:            _LP_ACCENT,
        Keyword.Type:       _LP_SECONDARY,
        Operator.Word:      _LP_ACCENT,
        Name.Function:      _LP_FUNCTION,
        Name.Class:         _LP_SECONDARY,
        Name.Builtin:       _LP_PRIMARY,
        String:             _LP_STRING,
        Number:             _LP_NUMBER,
        Punctuation:        _LP_PUNCT,
    }


# ── GitHub Light palette ──────────────────────────────────────────────────────
_GL_BG = "#FFFFFF"
_GL_SURFACE = "#F6F8FA"
_GL_PANEL = "#EAECEF"
_GL_FG = "#24292E"
_GL_PRIMARY = "#D73A49"   # keyword / accent
_GL_SECONDARY = "#6F42C1"   # type / function
_GL_COMMENT = "#6A737D"
_GL_STRING = "#032F62"
_GL_NUMBER = "#005CC5"
_GL_PUNCT = "#24292E"
_GL_WARNING = "#E36209"
_GL_SUCCESS = "#22863A"


class GitHubLightStyle(Style):
    background_color = _GL_BG
    styles: ClassVar[dict] = {
        Token:              _GL_FG,
        Comment:            _GL_COMMENT,
        Keyword:            _GL_PRIMARY,
        Keyword.Type:       _GL_SECONDARY,
        Operator.Word:      _GL_PRIMARY,
        Name.Function:      _GL_SECONDARY,
        Name.Class:         _GL_SECONDARY,
        Name.Builtin:       _GL_PRIMARY,
        String:             _GL_STRING,
        Number:             _GL_NUMBER,
        Punctuation:        _GL_PUNCT,
    }


# ── Textual themes ────────────────────────────────────────────────────────────


ROSEATE = Theme(
    name="roseate",
    primary=_R_PRIMARY,
    secondary=_R_SECONDARY,
    warning=_R_NUMBER,
    error=_R_ERROR,
    success=_R_STRING,
    accent=_R_PRIMARY,
    foreground=_R_FG,
    background=_R_BG,
    surface=_R_SURFACE,
    panel=_R_PANEL,
    dark=True,
)

DARK = Theme(
    name="maxima-dark",
    primary=_D_PRIMARY,
    secondary=_D_SECONDARY,
    warning=_D_NUMBER,
    error=_D_ERROR,
    success=_D_SECONDARY,
    accent=_D_PRIMARY,
    foreground=_D_FG,
    background=_D_BG,
    surface=_D_SURFACE,
    panel=_D_PANEL,
    dark=True,
)

LAVENDER = Theme(
    name="lavender",
    primary=_L_PRIMARY,
    secondary=_L_SECONDARY,
    warning=_L_NUMBER,
    error=_L_ERROR,
    success=_L_STRING,
    accent=_L_PRIMARY,
    foreground=_L_FG,
    background=_L_BG,
    surface=_L_SURFACE,
    panel=_L_PANEL,
    dark=False,
)

DRACULA = Theme(
    name="maxima-dracula",
    primary=_DR_PRIMARY,
    secondary=_DR_SECONDARY,
    warning=_DR_WARNING,
    error=_DR_ERROR,
    success=_DR_FUNCTION,
    accent=_DR_NUMBER,
    foreground=_DR_FG,
    background=_DR_BG,
    surface=_DR_SURFACE,
    panel=_DR_PANEL,
    dark=True,
)

DARK_PLUS = Theme(
    name="dark-plus",
    primary=_DP_PRIMARY,
    secondary=_DP_SECONDARY,
    warning=_DP_STRING,
    error=_DP_ERROR,
    success=_DP_NUMBER,
    accent=_DP_FUNCTION,
    foreground=_DP_FG,
    background=_DP_BG,
    surface=_DP_SURFACE,
    panel=_DP_PANEL,
    dark=True,
)

LIGHT_PLUS = Theme(
    name="light-plus",
    primary=_LP_PRIMARY,
    secondary=_LP_SECONDARY,
    warning=_LP_FUNCTION,
    error=_LP_STRING,
    success=_LP_COMMENT,
    accent=_LP_ACCENT,
    foreground=_LP_FG,
    background=_LP_BG,
    surface=_LP_SURFACE,
    panel=_LP_PANEL,
    dark=False,
)

GITHUB_LIGHT = Theme(
    name="github-light",
    primary=_GL_PRIMARY,
    secondary=_GL_SECONDARY,
    warning=_GL_WARNING,
    error=_GL_PRIMARY,
    success=_GL_SUCCESS,
    accent=_GL_SECONDARY,
    foreground=_GL_FG,
    background=_GL_BG,
    surface=_GL_SURFACE,
    panel=_GL_PANEL,
    dark=False,
)


# ── Theme registry ────────────────────────────────────────────────────────────


THEMES: dict[str, dict] = {
    "roseate":      {"textual": ROSEATE, "pygments": RoseateStyle},
    "dark":         {"textual": DARK, "pygments": DarkStyle},
    "lavender":     {"textual": LAVENDER, "pygments": LavenderStyle},
    "dracula":      {"textual": DRACULA, "pygments": DraculaStyle},
    "dark-plus":    {"textual": DARK_PLUS, "pygments": DarkPlusStyle},
    "light-plus":   {"textual": LIGHT_PLUS, "pygments": LightPlusStyle},
    "github-light": {"textual": GITHUB_LIGHT, "pygments": GitHubLightStyle},
}

DEFAULT_THEME = "roseate"
