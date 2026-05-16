"""Theme registry — bundles Textual app themes with Pygments syntax styles."""

from dipper.themes.dark import DARK, DarkStyle
from dipper.themes.dark_plus import DARK_PLUS, DarkPlusStyle
from dipper.themes.dracula import DRACULA, DraculaStyle
from dipper.themes.github_light import GITHUB_LIGHT, GitHubLightStyle
from dipper.themes.lavender import LAVENDER, LavenderStyle
from dipper.themes.light_plus import LIGHT_PLUS, LightPlusStyle
from dipper.themes.roseate import ROSEATE, RoseateStyle

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
