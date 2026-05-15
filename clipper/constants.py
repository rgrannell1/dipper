# Constants for the clipper annotation tool

# Number of colour groups available to the user (1–9)
GROUP_COUNT = 9

# Key that writes annotated output to stdout and exits
WRITE_KEY = "w"

# Prefix shared by all clipper-generated output lines
CLIPPER_PREFIX = "%%clipper:"

# Mark line emitted after each selected source line; N is the group number
MARK_FORMAT = "%%clipper:mark:{group}%% {underline}"

# Visual underline character repeated after the mark prefix
UNDERLINE_CHAR = "^"

# Minimum underline length in characters
UNDERLINE_MIN = 6

# Separator between annotated body and group summary
SEPARATOR_LINE = "%%clipper:separator%%"

# Group header line in the summary section
GROUP_FORMAT = "%%clipper:group:{group}%%"

# Colours for groups 1–9, indexed by group number (1-based, index 0 unused)
GROUP_COLOURS = [
    "",          # placeholder, groups are 1-based
    "bright_red",
    "bright_yellow",
    "bright_green",
    "bright_cyan",
    "bright_blue",
    "bright_magenta",
    "orange3",
    "deep_pink2",
    "grey82",
]
