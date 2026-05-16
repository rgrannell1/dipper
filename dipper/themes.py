# Colour themes ported from maxima — each bundles a Textual app theme and a Pygments syntax style.

from typing import ClassVar

from pygments.style import Style
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Token
from textual.theme import Theme

# ── Pygments styles ───────────────────────────────────────────────────────────


class RoseateStyle(Style):
    background_color = "#2c2833"
    styles: ClassVar[dict] = {
        Token:              "#FFF0F5",
        Comment:            "#6b5c70",
        Keyword:            "#ff82cb",
        Keyword.Type:       "#82AAFF",
        Operator.Word:      "#ff82cb",
        Name.Function:      "#82AAFF",
        Name.Class:         "#82AAFF",
        Name.Builtin:       "#ff82cb",
        Name.Decorator:     "#ff82cb",
        String:             "#a8d8ea",
        Number:             "#ffb347",
        Punctuation:        "#d4b4e0",
    }


class DarkStyle(Style):
    background_color = "#0d0d0d"
    styles: ClassVar[dict] = {
        Token:              "#c8c8c8",
        Comment:            "#666666",
        Keyword:            "#5fafff",
        Keyword.Type:       "#87af87",
        Operator.Word:      "#5fafff",
        Name.Function:      "#87af87",
        Name.Class:         "#87af87",
        Name.Builtin:       "#5fafff",
        String:             "#afd787",
        Number:             "#d7af87",
        Punctuation:        "#c8c8c8",
    }


class LavenderStyle(Style):
    background_color = "#f5f0ff"
    styles: ClassVar[dict] = {
        Token:              "#2d1f5e",
        Comment:            "#9b8ab8",
        Keyword:            "#7c4dce",
        Keyword.Type:       "#c2185b",
        Operator.Word:      "#7c4dce",
        Name.Function:      "#c2185b",
        Name.Class:         "#c2185b",
        Name.Builtin:       "#7c4dce",
        String:             "#2e7d32",
        Number:             "#e65100",
        Punctuation:        "#4a3080",
    }


class DraculaStyle(Style):
    background_color = "#282A36"
    styles: ClassVar[dict] = {
        Token:              "#F8F8F2",
        Comment:            "#6272A4",
        Keyword:            "#FF79C6",
        Keyword.Type:       "#8BE9FD",
        Operator.Word:      "#FF79C6",
        Name.Function:      "#50FA7B",
        Name.Class:         "#50FA7B",
        Name.Builtin:       "#FF79C6",
        Name.Decorator:     "#50FA7B",
        String:             "#F1FA8C",
        Number:             "#BD93F9",
        Punctuation:        "#F8F8F2",
    }


class DarkPlusStyle(Style):
    background_color = "#1E1E1E"
    styles: ClassVar[dict] = {
        Token:              "#D4D4D4",
        Comment:            "#6A9955",
        Keyword:            "#569CD6",
        Keyword.Type:       "#4EC9B0",
        Operator.Word:      "#569CD6",
        Name.Function:      "#DCDCAA",
        Name.Class:         "#4EC9B0",
        Name.Builtin:       "#569CD6",
        String:             "#CE9178",
        Number:             "#B5CEA8",
        Punctuation:        "#D4D4D4",
    }


class LightPlusStyle(Style):
    background_color = "#FFFFFF"
    styles: ClassVar[dict] = {
        Token:              "#000000",
        Comment:            "#008000",
        Keyword:            "#0000FF",
        Keyword.Type:       "#267F99",
        Operator.Word:      "#0000FF",
        Name.Function:      "#795E26",
        Name.Class:         "#267F99",
        Name.Builtin:       "#0451A5",
        String:             "#A31515",
        Number:             "#098658",
        Punctuation:        "#000000",
    }


class GitHubLightStyle(Style):
    background_color = "#FFFFFF"
    styles: ClassVar[dict] = {
        Token:              "#24292E",
        Comment:            "#6A737D",
        Keyword:            "#D73A49",
        Keyword.Type:       "#6F42C1",
        Operator.Word:      "#D73A49",
        Name.Function:      "#6F42C1",
        Name.Class:         "#6F42C1",
        Name.Builtin:       "#D73A49",
        String:             "#032F62",
        Number:             "#005CC5",
        Punctuation:        "#24292E",
    }


# ── Textual themes ────────────────────────────────────────────────────────────


ROSEATE = Theme(
    name="roseate",
    primary="#ff82cb",
    secondary="#82AAFF",
    warning="#ffb347",
    error="#ff5c8a",
    success="#a8d8ea",
    accent="#ff82cb",
    foreground="#FFF0F5",
    background="#2c2833",
    surface="#221e2b",
    panel="#3a3040",
    dark=True,
)

DARK = Theme(
    name="maxima-dark",
    primary="#5fafff",
    secondary="#87af87",
    warning="#d7af87",
    error="#ff5f5f",
    success="#87af87",
    accent="#5fafff",
    foreground="#c8c8c8",
    background="#0d0d0d",
    surface="#1a1a1a",
    panel="#222222",
    dark=True,
)

LAVENDER = Theme(
    name="lavender",
    primary="#7c4dce",
    secondary="#c2185b",
    warning="#e65100",
    error="#c2185b",
    success="#2e7d32",
    accent="#7c4dce",
    foreground="#2d1f5e",
    background="#f5f0ff",
    surface="#ebe4f8",
    panel="#ddd6f0",
    dark=False,
)

DRACULA = Theme(
    name="maxima-dracula",
    primary="#FF79C6",
    secondary="#8BE9FD",
    warning="#FFB86C",
    error="#FF5555",
    success="#50FA7B",
    accent="#BD93F9",
    foreground="#F8F8F2",
    background="#282A36",
    surface="#21222C",
    panel="#44475A",
    dark=True,
)

DARK_PLUS = Theme(
    name="dark-plus",
    primary="#569CD6",
    secondary="#4EC9B0",
    warning="#CE9178",
    error="#F44747",
    success="#B5CEA8",
    accent="#DCDCAA",
    foreground="#D4D4D4",
    background="#1E1E1E",
    surface="#252526",
    panel="#333333",
    dark=True,
)

LIGHT_PLUS = Theme(
    name="light-plus",
    primary="#0451A5",
    secondary="#267F99",
    warning="#795E26",
    error="#A31515",
    success="#008000",
    accent="#0000FF",
    foreground="#000000",
    background="#FFFFFF",
    surface="#F3F3F3",
    panel="#E8E8E8",
    dark=False,
)

GITHUB_LIGHT = Theme(
    name="github-light",
    primary="#D73A49",
    secondary="#6F42C1",
    warning="#E36209",
    error="#D73A49",
    success="#22863A",
    accent="#6F42C1",
    foreground="#24292E",
    background="#FFFFFF",
    surface="#F6F8FA",
    panel="#EAECEF",
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
