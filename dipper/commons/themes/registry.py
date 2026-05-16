"""THEMES registry and DEFAULT_THEME constant."""

from dipper.commons.themes.dark import DARK, DarkStyle
from dipper.commons.themes.dark_plus import DARK_PLUS, DarkPlusStyle
from dipper.commons.themes.dracula import DRACULA, DraculaStyle
from dipper.commons.themes.github_light import GITHUB_LIGHT, GitHubLightStyle
from dipper.commons.themes.lavender import LAVENDER, LavenderStyle
from dipper.commons.themes.light_plus import LIGHT_PLUS, LightPlusStyle
from dipper.commons.themes.roseate import ROSEATE, RoseateStyle

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
